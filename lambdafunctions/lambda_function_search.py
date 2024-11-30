import json
import boto3
from opensearchpy import OpenSearch

# Initialize Lex runtime client
lex_client = boto3.client('lexv2-runtime')

# OpenSearch connection setup
opensearch_client = OpenSearch(
    hosts=[{'host': 'search-photos-kbihlhs7ixlzuve77np5oqqzam.aos.us-east-1.on.aws', 'port': 443}],
    http_auth=('master', 'Mimo@148'),  # Replace with your OpenSearch credentials
    use_ssl=True,
    verify_certs=True
)

def lambda_handler(event, context):
    # Extract the query from the event
    print("Received Event:")
    print(json.dumps(event, indent=2)) 
    query = event.get('q')
    print(f"Received Query: {query}")
    
    # Replace these values with your Lex bot's details
    bot_id = "YLRLMWGWT9"
    bot_alias_id = "TSTALIASID"
    locale_id = "en_US"
    session_id = "test-session"

    # Send the query to Lex bot
    response = lex_client.recognize_text(
        botId=bot_id,
        botAliasId=bot_alias_id,
        localeId=locale_id,
        sessionId=session_id,
        text=query
    )

    print(f"Lex Response: {json.dumps(response, indent=2)}")

    # Extract the slots from the Lex response
    slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})

    # Extract keywords with safe checks
    keyword1 = slots.get('keyword1', {}).get('value', {}).get('interpretedValue', None)
    keyword2 = None  # Default to None

    # Check if keyword2 exists in the slots dictionary
    if 'keyword2' in slots and slots['keyword2'] is not None:
        keyword2 = slots['keyword2'].get('value', {}).get('interpretedValue', None)

    # Log extracted keywords for debugging
    print(f"Extracted Keywords: Keyword1 = {keyword1}, Keyword2 = {keyword2}")
    
    # Generate a response based on keywords
    if keyword1 or keyword2:
        # Combine keywords for search and convert to camel case
        search_terms = []
        if keyword1:
            search_terms.append(keyword1.title())  # Convert to camel case
        if keyword2:
            search_terms.append(keyword2.title())  # Convert to camel case
        
        # Perform search in OpenSearch
        os_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"labels": search_term}} for search_term in search_terms
                    ],
                    "minimum_should_match": 1
                }
            }
        }
        
        try:
            search_results = opensearch_client.search(index="photos", body=os_query)
            hits = search_results['hits']['hits']
            results = [{"id": hit["_id"], "source": hit["_source"]} for hit in hits]
        except Exception as e:
            print(f"OpenSearch Search Error: {e}")
            results = []
        
    else:
        results = []
    print(f"Search Results: {json.dumps(results, indent=2)}")
    
    # Return response
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": f"Search results for keywords: {', '.join(search_terms) if search_terms else 'None'}",
            "results": results
        })
    }
