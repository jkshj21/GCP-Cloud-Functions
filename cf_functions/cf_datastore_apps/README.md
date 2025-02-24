# The Cloud Function for GCP Discovery Engines (Search, Answer, Conversation)

This Cloud Function demonstrates how to deploy the Cloud Function that trigger by http requests and based on the http request path, it apply 3 GCP Discovery Engines, Search, Answer, and Conversation, to output the user query. 

## Purpose of this Cloud Function
The purpose is to integrate with GCP Dialogflow CX and GCP Discovery Engines API. Although, GCP Dialogflow CX has the function to add Vertex AI Datastore functionality, it doesn't have the functionality to use any of these Engines. By deploying this Cloud Function and then create the Webhooks within Dialogflow, it can create the seamless interactive fulfillment with the users. 

Set three Webhooks URLs by the following below:
* POST: https://<YOUR_CLOUD_FUNCTION_URL>/conversation
* POST: https://<YOUR_CLOUD_FUNCTION_URL>/search
* POST: https://<YOUR_CLOUD_FUNCTION_URL>/answer

And then define these Webhooks within the flow or page fulfillemnt in Dialogflow CX. 

## Discovery Engines with Datastore

What is GCP Datastore? Vertex AI datastores allow you to ingest and structure data from various sources, including websites, BigQuery, and Cloud Storage. This data can be structured (e.g., tables), unstructured (e.g., documents), or a combination of both.

There are three functionalities of this Cloud Function, they are:

* Search Engine: Designed for traditional keyword-based search and semantic search over a catalog of items (e.g., products, documents, web pages).Focuses on retrieving a ranked list of relevant results based on user queries.
* Answer Engine: Designed to directly answer user questions by extracting relevant information from your data. Focuses on providing concise and accurate answers rather than just a list of results.
* Conversation Engine: Designed to power conversational experiences, such as chatbots and voice assistants. Focuses on maintaining context and providing natural language responses throughout a conversation.

Reference: https://cloud.google.com/generative-ai-app-builder/docs/reference/rest


## Setup

1. Deploy the code to a GCP Cloud Function (version 2).
2. Set the Function Entry Point to `my_function`.
3. Use a Python 3.10+ runtime environment.
4. Set "datastore_id" in the Cloud Function environment variable. The format of "datastore_id" should be 'projects/<PROJECT_ID>/locations/<LOCATION>/collections/<COLLECTION_ID>/dataStores/<DATASTORE_ID>.

## Testing

The Cloud Function exposes the following HTTP routes:

### 1. `ask_by_covnersation()` (POST)

This function handles requests to the root path and the following a keyword, 'conversation'.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/conversation \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?",
}'
```

### 2. `ask_by_search()` (POST)

This function handles requests to the root path and the following a keyword, 'search'.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/search \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?",
}'
```

### 2. `ask_by_answer()` (POST)

This function handles requests to the root path and the following a keyword, 'answer'.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X DELETE https://<YOUR_CLOUD_FUNCTION_URL>/answer \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?"
}'

