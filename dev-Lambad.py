import boto3
import json
from urllib.parse import unquote
def lambda_handler(event, context):
    # Extract bucket name and file name from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_name = unquote(event['Records'][0]['s3']['object']['key'])  # Decode the file name
    print("bn - ",bucket_name)
    print("fn - ",file_name)
    # Initialize the CodeBuild client
    codebuild = boto3.client('codebuild')
    
    # Start the CodeBuild project, passing the bucket name and file name as environment variables
    response = codebuild.start_build(
        projectName='datapipes-poc-PR',
        environmentVariablesOverride=[
            {
                'name': 'BUCKET_NAME',
                'value': bucket_name,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'FILE_NAME',
                'value': file_name,
                'type': 'PLAINTEXT'
            }
        ]
    )
    print(json.dumps(response, default=str))
    return {
        'statusCode': 200,
        'body': json.dumps('CodeBuild started successfully!')
    }
