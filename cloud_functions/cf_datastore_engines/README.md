# Cloud Function for Google Cloud Discovery Engine Integration (Search, Answer, Conversation)

This Cloud Function demonstrates how to integrate Google Cloud Discovery Engine's Search, Answer, and Conversation engines with GCP Dialogflow CX via HTTP requests.

## Purpose

This function bridges the gap between Dialogflow CX and Discovery Engine, enabling you to leverage the powerful capabilities of Search, Answer, and Conversation engines within your conversational flows. While Dialogflow CX offers Vertex AI Datastore integration, it lacks direct support for these engines. By deploying this Cloud Function and creating corresponding webhooks in Dialogflow CX, you can build seamless, interactive user experiences.

**Dialogflow CX Webhook Setup:**

Create three webhooks in your Dialogflow CX agent, pointing to the following Cloud Function endpoints:

* **Conversation Engine:** `POST https://<YOUR_CLOUD_FUNCTION_URL>/conversation`
* **Search Engine:** `POST https://<YOUR_CLOUD_FUNCTION_URL>/search`
* **Answer Engine:** `POST https://<YOUR_CLOUD_FUNCTION_URL>/answer`

Then, configure these webhooks within your Dialogflow CX flows or page fulfillments as needed.

## Discovery Engine Datastores

Vertex AI Datastores act as a knowledge base, allowing you to ingest and structure data from various sources (websites, BigQuery, Cloud Storage) in structured, unstructured, or hybrid formats.

This Cloud Function utilizes Datastores in conjunction with the following Discovery Engine functionalities:

* **Search Engine:** Enables keyword and semantic search over a catalog, returning a ranked list of relevant items (products, documents, etc.).
* **Answer Engine:** Directly answers user questions by extracting information from your data, providing concise answers with citations.
* **Conversation Engine:** Powers conversational experiences by maintaining context and generating natural language responses.

**Reference:** [Google Cloud Generative AI App Builder REST API](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest)

## Deployment

1.  Deploy the code to a Google Cloud Function (2nd gen).
2.  Set the entry point to `my_function`.
3.  Use a Python 3.10+ runtime environment.
4.  Configure the `datastore_id` environment variable with the full resource name: `projects/<PROJECT_ID>/locations/<LOCATION>/collections/<COLLECTION_ID>/dataStores/<DATASTORE_ID>`.

## Testing

The Cloud Function exposes the following HTTP POST endpoints:

### 1. `use_conversation()` (/conversation)

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/conversation \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?"
}'
```

### 2. `use_search()` (/search)

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/search \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?"
}'
```

### 3. `use_answer()` (/answer)

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/answer \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "text": "what are the plans?"
}'
```
