
def handler(event, context):
    print("Summarize document content")
    print(event)
    return {"statusCode": 200, "body": "Success!"}

