import aws_cdk as core
import aws_cdk.assertions as assertions

from rag_app.rag_app_stack import RagAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rag_app/rag_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RagAppStack(app, "rag-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
