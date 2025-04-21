from aws_cdk import (
    Duration,
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications
)
from constructs import Construct


class RagAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SNS
        document_created_topic = sns.Topic(self, "DocumentCreatedTopic")
        # Create queue
        document_created_queue = sqs.Queue(self, "DocumentCreatedQueue", visibility_timeout=Duration.seconds(300))

        document_created_topic.add_subscription(sns_subscriptions.SqsSubscription(document_created_queue))

        # Create SNS
        document_content_extracted_topic = sns.Topic(self, "DocumentContentExtractedTopic")
        # Create queue
        document_content_extracted_queue = sqs.Queue(self, "DocumentContentExtractedQueue",
                                                     visibility_timeout=Duration.seconds(300))
        document_content_extracted_topic.add_subscription(
            sns_subscriptions.SqsSubscription(document_content_extracted_queue))

        # Create SNS
        document_content_summarized_topic = sns.Topic(self, "DocumentContentSummarizedTopic")
        # Create queue
        document_content_summarized_queue = sqs.Queue(self, "DocumentContentSummarizedQueue",
                                                      visibility_timeout=Duration.seconds(300))
        document_content_summarized_topic.add_subscription(
            sns_subscriptions.SqsSubscription(document_content_summarized_queue))

        # Create Lambda function
        extract_document_metadata_lambda = lambda_.Function(self, "ExtractDocumentMetadataLambda",
                                                            handler='extract_document_metadata.handler',
                                                            runtime=lambda_.Runtime.PYTHON_3_12,
                                                            code=lambda_.Code.from_asset('lambda'))

        extract_document_content_lambda = lambda_.Function(self, "ExtractDocumentContentLambda",
                                                           handler='extract_document_content.handler',
                                                           runtime=lambda_.Runtime.PYTHON_3_12,
                                                           code=lambda_.Code.from_asset('lambda'))

        summarize_document_content_lambda = lambda_.Function(self, "SummarizeDocumentContentLambda",
                                                             handler='summarize_document_content.handler',
                                                             runtime=lambda_.Runtime.PYTHON_3_12,
                                                             code=lambda_.Code.from_asset('lambda'))

        generate_summarized_content_embeddings_lambda = lambda_.Function(self,
                                                                         "GenerateSummarizedContentEmbeddingsLambda",
                                                                         handler='generate_summarized_content_embeddings.handler',
                                                                         runtime=lambda_.Runtime.PYTHON_3_12,
                                                                         code=lambda_.Code.from_asset('lambda'))

        # Add an event source to the existing s3 bucket
        bucket = s3.Bucket.from_bucket_name(self, "RAGDocuments", "rag-docs-s3-bucket")
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3_notifications.LambdaDestination(extract_document_metadata_lambda))


        sqs_event_source = lambda_event_sources.SqsEventSource(document_created_queue)
        extract_document_content_lambda.add_event_source(sqs_event_source)

        sqs_event_source = lambda_event_sources.SqsEventSource(document_content_extracted_queue)
        summarize_document_content_lambda.add_event_source(sqs_event_source)

        sqs_event_source = lambda_event_sources.SqsEventSource(document_content_summarized_queue)
        generate_summarized_content_embeddings_lambda.add_event_source(sqs_event_source)
