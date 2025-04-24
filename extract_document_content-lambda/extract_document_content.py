import json
import boto3
from botocore.exceptions import ClientError
import io


def download_s3_object(bucket_name: str, object_key: str):
    try:
        s3_client = boto3.client("s3")
        file_obj = io.BytesIO()
        s3_client.download_fileobj(Bucket=bucket_name, Key=object_key, Fileobj=file_obj)
        file_obj.seek(0)

        return file_obj.read()
    except ClientError as e:
        print(f"Error descargando objeto de S3: {e}")
        raise


def extract_document_content():
    pass


def handler(event, context):
    print("ExtractDocumentContentLambda")
    print(">>> Extraer contenido del documento.")

    for record in event["Records"]:
        body = json.loads(record["body"])
        print(json.dumps(body, indent=4))

        # bucket_name = inputs["s3"]["bucket_name"]
        # object_name = inputs["path"]
        # print(json.dumps(inputs, indent=4))

        # content = download_s3_object(bucket_name, object_name)
        # response = extract_document_content(content)
        # if response:
        #     print(">>> Documento extraido correctamente.")
        #     delete_message_from_sqs(record["receiptHandle"])

    return {"statusCode": 200, "body": "Procesamiento completado"}
