# GCP Cloud Function with Flask Routing

This Cloud Function demonstrates how to use Flask routing to handle multiple HTTP requests within a single Cloud Function. This approach centralizes functionality and is more efficient than deploying multiple individual Cloud Functions.

## Use Case

This pattern is particularly useful when working with GCP Dialogflow CX webhooks, where a single webhook might need to trigger various backend operations, such as:

* Updating backend systems
* Training LLMs
* Generating responses
* Setting parameters

Consolidating these functions into one Cloud Function simplifies management and deployment.

## Setup

1. Deploy the code to a GCP Cloud Function (version 2).
2. Set the Function Entry Point to `my_function`.
3. Use a Python 3.10+ runtime environment.

## Testing

The Cloud Function exposes the following HTTP routes:

### 1. `main()` (POST)

This function handles requests to the root path.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL> \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "name": "Developer"
}'
```

### 2. `update_user(id)` (POST)

This function handles requests to the root path.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X POST https://<YOUR_CLOUD_FUNCTION_URL>/user/123 \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "name": "Developer"
}'
```

### 2. `delete_user(id)` (POST)

This function handles requests to the root path.  Test it using the following `curl` command in the Cloud Console:

```bash
curl -X DELETE https://<YOUR_CLOUD_FUNCTION_URL>/user/123 \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "name": "Developer"
}'

