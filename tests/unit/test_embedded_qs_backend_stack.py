import aws_cdk as core
import aws_cdk.assertions as assertions

from embedded_qs_backend.embedded_qs_backend_stack import EmbeddedQsBackendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in embedded_qs_backend/embedded_qs_backend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EmbeddedQsBackendStack(app, "embedded-qs-backend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
