from aws_cdk import (
    Duration,
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_lambda_python_alpha as _alambda,
    aws_lambda_destinations as lambda_destinations,
    aws_iam as iam,
)
from constructs import Construct


class RagAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ########################### Creación de SNS y SQS #############################
        # Create SNS
        document_created_topic = sns.Topic(self, "DocumentCreatedTopic")
        # Create queue
        document_created_queue = sqs.Queue(
            self, "DocumentCreatedQueue", visibility_timeout=Duration.seconds(300)
        )
        # Attach SQS to SNS
        document_created_topic.add_subscription(
            sns_subscriptions.SqsSubscription(document_created_queue)
        )

        # Create SNS
        document_content_extracted_topic = sns.Topic(
            self, "DocumentContentExtractedTopic"
        )
        # Create queue
        document_content_extracted_queue = sqs.Queue(
            self,
            "DocumentContentExtractedQueue",
            visibility_timeout=Duration.seconds(300),
        )
        # Attach SQS to SNS
        document_content_extracted_topic.add_subscription(
            sns_subscriptions.SqsSubscription(document_content_extracted_queue)
        )

        # Create SNS
        document_content_summarized_topic = sns.Topic(
            self, "DocumentContentSummarizedTopic"
        )
        # Create queue
        document_content_summarized_queue = sqs.Queue(
            self,
            "DocumentContentSummarizedQueue",
            visibility_timeout=Duration.seconds(300),
        )
        # Attach SQS to SNS
        document_content_summarized_topic.add_subscription(
            sns_subscriptions.SqsSubscription(document_content_summarized_queue)
        )

        ########################### Creación de Fn Lambda #############################
        extract_document_metadata_lambda = lambda_.Function(
            self,
            "ExtractDocumentMetadataLambda",
            handler="extract_document_metadata.handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("extract-document-metadata-lambda"),
            environment={
                "DOCUMENT_CREATED_TOPIC_ARN": document_created_topic.topic_arn,
            },
            # on_success=lambda_destinations.SnsDestination(document_created_topic),
        )
        # extract_document_metadata_lambda = _alambda.PythonFunction(
        #     self,
        #     "ExtractDocumentMetadataLambda",
        #     entry="./extract-document-metadata-lambda/",
        #     index="extract_document_metadata.py",
        #     handler="handler",
        #     runtime=lambda_.Runtime.PYTHON_3_12,
        #     on_success=lambda_destinations.SnsDestination(document_created_topic),
        # )

        extract_document_metadata_lambda.role.add_to_policy(
            iam.PolicyStatement(
                actions=["dynamodb:PutItem"],
                resources=[
                    "arn:aws:dynamodb:us-east-1:581395982511:table/DocumentMetadataTable"
                ],
            )
        )

        extract_document_content_lambda = lambda_.Function(
            self,
            "ExtractDocumentContentLambda",
            handler="extract_document_content.handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("extract_document_content-lambda"),
            environment={
                "DOCUMENT_CONTENT_EXTRACTED_TOPIC_ARN": document_content_extracted_topic.topic_arn,
                "DOCUMENT_CREATED_QUEUE_ARN": document_created_queue.queue_arn,
            },
            # on_success=lambda_destinations.SnsDestination(
            #     document_content_extracted_topic
            # ),
        )

        summarize_document_content_lambda = lambda_.Function(
            self,
            "SummarizeDocumentContentLambda",
            handler="summarize_document_content.handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("summarize_document_content-lambda"),
            environment={
                "DOCUMENT_CONTENT_SUMMARIZED_TOPIC_ARN": document_content_summarized_topic.topic_arn,
                "DOCUMENT_CONTENT_EXTRACTED_QUEUE_ARN": document_content_extracted_queue.queue_arn,
            },
            # on_success=lambda_destinations.SnsDestination(
            #     document_content_summarized_topic
            # ),
        )

        generate_summarized_content_embeddings_lambda = lambda_.Function(
            self,
            "GenerateSummarizedContentEmbeddingsLambda",
            handler="generate_summarized_content_embeddings.handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset(
                "generate_summarized_content_embeddings-lambda"
            ),
            environment={
                "DOCUMENT_CONTENT_SUMMARIZED_QUEUE_ARN": document_content_summarized_queue.queue_arn,
            },
        )

        ########################### Agregar trigger s3 (OBJECT_CREATED) a Lambda  #############################
        bucket = s3.Bucket.from_bucket_name(self, "RAGDocuments", "rag-docs-s3-bucket")
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.LambdaDestination(extract_document_metadata_lambda),
            s3.NotificationKeyFilter(
                suffix=".pdf",
            ),
        )

        ########################### Agregar trigger SQS a Lambda  #############################
        sqs_event_source = lambda_event_sources.SqsEventSource(document_created_queue)
        extract_document_content_lambda.add_event_source(sqs_event_source)

        sqs_event_source = lambda_event_sources.SqsEventSource(
            document_content_extracted_queue
        )
        summarize_document_content_lambda.add_event_source(sqs_event_source)

        sqs_event_source = lambda_event_sources.SqsEventSource(
            document_content_summarized_queue
        )
        generate_summarized_content_embeddings_lambda.add_event_source(sqs_event_source)
