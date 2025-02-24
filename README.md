<!-- PROJECT LOGO -->
<div align="center">
    <img src="https://github.com/jkshj21/gcp-ccai-functions-toolkit/blob/main/images/toolkit_log.png" alt="toolkit" width="1000">

  <h1 align="center">Python CCAI-Functions-Toolkit</h1>
  <p align="center">
    The ccai-functions-toolkit repository provides a collection of Google Cloud Functions designed to enhance and extend the capabilities of Google Cloud's Conversational AI (CCAI) platform, particularly Dialogflow CX.<br>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
    <li>
        <ul>
            <li><a href="#Deploying a Cloud Function using `gcloud`">How to deploy a Cloud Function?</a></li>
        </ul>
    </li>
</details>

<!-- INTRODUCTION -->
## Deploying a Cloud Function using `gcloud`

This document provides instructions on how to deploy a Google Cloud Function using the `gcloud` command-line tool.

## Prerequisites

* **Google Cloud SDK (gcloud CLI):** Ensure you have the Google Cloud SDK installed and configured. You can download and install it from the [official Google Cloud documentation](https://cloud.google.com/sdk/docs/install).
* **Authentication:** Authenticate with your Google Cloud account using `gcloud auth login`.
* **Project Selection:** Select the Google Cloud project where you want to deploy the function using `gcloud config set project YOUR_PROJECT_ID`.
* **Cloud Functions API Enabled:** Make sure the Cloud Functions API is enabled in your project. You can enable it via the [Google Cloud Console](https://console.cloud.google.com/apis/library/cloudfunctions.googleapis.com).
* **Cloud Build API Enabled (for 2nd gen):** If you are deploying a 2nd generation cloud function, ensure that the Cloud Build API is also enabled.

## Deployment Steps

1.  **Navigate to Function Directory:** Open your terminal or command prompt and navigate to the directory containing your Cloud Function code.

2.  **Deployment Command:** Use the following `gcloud` command to deploy your function:

    ```bash
    gcloud functions deploy YOUR_FUNCTION_NAME \
    --gen2 \ #use this line for 2nd gen functions
    --runtime YOUR_RUNTIME \
    --trigger-http \
    --allow-unauthenticated \ # Optional: If you want to allow unauthenticated access
    --region YOUR_REGION \
    --entry-point YOUR_ENTRY_POINT \
    --source . \ # The current directory as the source
    --set-env-vars VARIABLE1=VALUE1,VARIABLE2=VALUE2 # Optional environment variables
    ```

    **Replace the placeholders with your values:**

    * `YOUR_FUNCTION_NAME`: The name you want to give to your Cloud Function.
    * `YOUR_RUNTIME`: The runtime environment (e.g., `python310`, `nodejs18`).
    * `YOUR_REGION`: The Google Cloud region where you want to deploy the function (e.g., `us-central1`).
    * `YOUR_ENTRY_POINT`: The name of the function within your code that will be executed when the Cloud Function is triggered.
    * `VARIABLE1=VALUE1,VARIABLE2=VALUE2`: Environment variables you want to set (optional).

    **Important Notes:**

    * `--gen2` : Add this flag if you are deploying a 2nd generation cloud function. 2nd generation cloud functions have many benefits, such as longer timeouts and better scaling.
    * `--allow-unauthenticated`: If you want to allow anyone to invoke your function without authentication, include this flag. Be cautious when using this option, as it can expose your function to the public.
    * `--source .`: This specifies that the current directory should be used as the source code for the function. If your code is in a different directory, specify the path to that directory.
    * For more options and detailed information, refer to the `gcloud functions deploy` documentation: `gcloud functions deploy --help`.

3.  **Wait for Deployment:** The deployment process may take a few minutes. The `gcloud` command will display the progress and output the function's URL when it's complete.

4.  **Testing:** Once the deployment is successful, you can test your Cloud Function using the provided URL. You can use `curl`, Postman, or any other HTTP client.

## Example

```bash
#Navigate to Function Directory; for this example, it should be cd './cf_functions/cf_datastore_apps'
gcloud functions deploy my-http-function \
--gen2 \
--runtime python310 \
--trigger-http \
--allow-unauthenticated \
--region us-central1 \
--entry-point my_function \
--source . \
--set-env-vars DATASTORE_ID=projects/my-project/locations/us-central1/collections/default_collection/dataStores/my-datastore
