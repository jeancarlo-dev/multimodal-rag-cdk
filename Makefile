

build-test: build test

test-fn1: 
	cdk synth
	sam build -t ./cdk.out/RagAppStack.template.json
	sam local invoke -t ./cdk.out/RagAppStack.template.json ExtractDocumentMetadataLambda --event events/s3-object_created-event.json --skip-pull-image
	
test:
	sam local invoke -e events/event.json --skip-pull-image

build:
	sam build
	
deploy:
	sam build 
	sam deploy --no-confirm-changeset