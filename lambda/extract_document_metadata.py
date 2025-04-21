
def handler(event, context):
    print("Launch from s3 trigger ObjectCreated")
    print("Extracting document metadata")
    print(event)
    return {"statusCode": 200, "body": "Success!"}

