import uuid
import boto3
import json
import os
from datetime import datetime


def store_metadata_in_dynamodb(record):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("DocumentMetadataTable")

    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    size = record["s3"]["object"]["size"]

    metadata = {
        "uuid": str(uuid.uuid4()),
        "s3": {
            "bucket_name": bucket,
            "object_url": f"https://{bucket}.s3.amazonaws.com/{key}",
        },
        "path": key,
        "size": size,
        "documet_type": key.split(".")[-1],
        "solution_architect": None,
        "country": None,
        "tags": [],
        "created_at": datetime.now().isoformat(),
        "status": "METADATA_CREATED",
    }

    try:
        table.put_item(Item=metadata)
        print(f"Documento: {key} , metadata almacenada correctamente.")
        print(metadata)
        return metadata
    except Exception as e:
        print(f"Error storing metadata: {str(e)}")
        raise e


def publish_on_sns_topic(metadata):
    sns = boto3.client("sns")
    topic_arn = os.environ["DOCUMENT_CREATED_TOPIC_ARN"]

    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps({"document_metadata": metadata}),
        )
        print(f"Documento: {metadata['path']}, publicado en SNS.")
    except Exception as e:
        print(f"Error publishing on SNS topic: {str(e)}")
        raise e


def handler(event, context):
    print("ExtractDocumentMetadataLambda")
    print(">>> Extraer metadata del documento s3.")

    for record in event["Records"]:
        metadata = store_metadata_in_dynamodb(record)
        publish_on_sns_topic(metadata)
        # response.append(metadata)

    return True
