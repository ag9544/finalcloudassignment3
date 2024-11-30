import boto3
import json
import datetime
from opensearchpy import OpenSearch

# AWS Clients
rekognition_client = boto3.client('rekognition')
s3_client = boto3.client('s3')

# OpenSearch Configuration
opensearch_client = OpenSearch(
    hosts=[{'host': 'search-photos-kbihlhs7ixlzuve77np5oqqzam.aos.us-east-1.on.aws', 'port': 443}],
    http_auth=('master', 'Mimo@148'),  # Replace with your OpenSearch credentials
    use_ssl=True,
    verify_certs=True
)

def lambda_handler(event, context):
    try:
        # Parse the S3 event
        print("Incoming Event:", json.dumps(event, indent=2))

        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        print(f"Processing file: {object_key} from bucket: {bucket}")
        # Detect labels using Rekognition
        rekognition_response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': object_key}},
            MaxLabels=10
        )
        labels = [label['Name'] for label in rekognition_response['Labels']]
        print(labels)
        # Retrieve metadata from S3
        #metadata = s3_client.head_object(Bucket=bucket, Key=object_key)
        custom_labels = metadata.get("Metadata", {}).get("custom_labels", '')
        #print("custom_labels are ",custom_labels)
        # Combine Rekognition labels with custom labels
        combined_labels = labels + custom_labels

        # Prepare the JSON object
        document = {
            "objectKey": object_key,
            "bucket": bucket,
            "createdTimestamp": datetime.datetime.now().isoformat(),
            "labels": combined_labels
        }

        # Index the document in OpenSearch
        opensearch_response = opensearch_client.index(
            index="photos",
            body=document,
            id=object_key
        )
        
        print("Document indexed:", opensearch_response)
        return {"statusCode": 200, "body": json.dumps("Photo indexed successfully!")}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps("An error occurred during processing.")}
