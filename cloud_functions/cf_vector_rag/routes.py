import os
import logging
from typing import List, Dict, Any
from google.cloud import storage, bigquery
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_community import BigQueryVectorStore
from langchain_community.document_loaders import PyPDFLoader, BSHTMLLoader, UnstructuredHTMLLoader

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
BUCEKT_NAME = os.environ.get("BUCKET_NAME")
DATASET = os.environ.get("DATASET")
TABLE_ID = os.environ.get("TABLE_ID")
DEFAULT_CHUNK_SIZE = 200
DEFAULT_CHUNK_OVERLAP = 20

def load_pdf_documents(file_path: str):
    return PyPDFLoader(file_path)

def load_html_documents(file_path: str):
    return UnstructuredHTMLLoader(file_path)

def add_document_name(loader: List):
    for doc in loader:
        doc.metadata["document_name"] = doc.metadata["source"].split("/")[-1]
    return loader

def load_files_from_gcs(bucket_name, folder_name: str=None):
    gcs_client = storage.Client()
    all_documents = []
    for blob in gcs_client.list_blobs(bucket_name, prefix=folder_name):
        if blob.name.endswith(".pdf"):
            loader = GCSFileLoader(
                project_name=PROJECT_ID,
                bucket=blob.bucket.name,
                blob=blob.name,
                loader_func=load_pdf_documents
                ).load()
        elif blob.name.endswith(".html"):
            loader = GCSFileLoader(
                project_name=PROJECT_ID,
                bucket=blob.bucket.name,
                blob=blob.name,
                loader_func=load_html_documents
                ).load()
            # html_metas = extract_meta_information(blob)
            # for doc in loader:
            #     doc.metadata.update(html_metas)
        else:
            continue
        loader = add_document_name(loader)
        all_documents.extend(loader)
    return all_documents

def add_docs_in_bqQueryVectorstore(docs):
    EMBEDDING_MODEL = VertexAIEmbeddings(
         model_name="textembedding-gecko@latest", project=PROJECT_ID
    )
    vector_store = BigQueryVectorStore(
        project_id=PROJECT_ID,
        location=LOCATION,
        dataset_name=DATASET,
        table_name=TABLE_ID,
        embedding=EMBEDDING_MODEL,
    )
    #add documents to the store
    client = bigquery.Client()
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE_ID}"
    if check_bigquery_table_has_data(client):
        delete_bigquery_table_data(client)
    doc_ids = vector_store.add_documents(docs)
    return vector_store

def process_docs(data: Dict[str, Any]):
    chunk_size = data.get("chunk_size", None)
    chunk_overlap = data.get("chunk_overlap", None)
    if not any([chunk_size, chunk_overlap]):
        chunk_size = DEFAULT_CHUNK_SIZE
        chunk_overlap = DEFAULT_CHUNK_OVERLAP
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )
    documents = load_files_from_gcs(bucket_name=BUCEKT_NAME)
    doc_splits = text_splitter.split_documents(documents)
    #Add chunk number to metada
    for idx, split in enumerate(doc_splits):
        split.metadata["chunk"] = idx
    return doc_splits

def preproc_run_route_controller(data: Dict[str, Any]):
    logging.info("Initiating document preprocessing.")
    docs = process_docs(data)
    vector_store = add_docs_in_bqQueryVectorstore(docs)
    return vector_store

def vs_qa_chain_controller(data: Dict[str, Any]):
    if not check_bigquery_table_has_data:
        logging.info(
            "BigQuery table is empty."
            "Initiating document preprocessing by calling preproc_run_route_controller(). "
            f"Using chunk_size={data.get('chunk_size', DEFAULT_CHUNK_SIZE)} and "
            f"chunk_overlap={data.get('chunk_overlap', DEFAULT_CHUNK_OVERLAP)}."
        )
        if "chunk_size" not in data and "chunk_overlap" not in data:
            data["chunk_size"] = DEFAULT_CHUNK_SIZE
            data["chunk_overlap"] = DEFAULT_CHUNK_OVERLAP
        preproc_run_route_controller(data)

    EMBEDDING_MODEL = VertexAIEmbeddings(
         model_name="textembedding-gecko@latest", project=PROJECT_ID
    )
    vector_store = BigQueryVectorStore(
        project_id=PROJECT_ID,
        location=LOCATION,
        dataset_name=DATASET,
        table_name=TABLE_ID,
        embedding=EMBEDDING_MODEL,
    )
    llm = VertexAI(model_name="gemini-pro")
    query = data.get("text", None)
    if not query:
        logging.Error("Request need a text to query Vector Store")
        return {
            "error": "Request doesn't have a text to query"
        }
    langchain_retriever = vector_store.as_retriever()
    llm = VertexAI(model_name="gemini-pro")
    retrieval_qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=langchain_retriever
    )
    try:
        response = retrieval_qa.invoke(query)
    except Error as e:
        logging.Error("Error occurred while querying Vector Store: {e}")
        return {
            "error": "Error occurred while querying Vector Store: {e}"
        }
    return response["result"]

def update_document_controller(doc_id: str, data: Dict[str, Any]):
    client = bigquery.Client()
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE_ID}"
    try:
        query = f"SELECT FROM `{table_ref}` WHERE doc_id = {doc_id}"
        query_job = client.query(query)
        results = list(query_job.results())
        if not results:
            logging.Error(f"Unable to find any documents with a provided doc_id: {doc_id}")
            return False
        existing_columns = [field.name for field in table.schema]
        update_query = f"UPDATE `{table_ref}` SET "
        updates = []
        for column, value in data.items():
            if column not in existing_columns:
                logging.Error(f"Column: {column}, does not exist in the table.")
                continue
            if isinstance(value, str):
                updates.append(f"{column} = '{value}'")
            else:
                updates.append(f"{column} = {value}")
        if not updates:
            logging.Error(f"No valid columns to update.")
            return False

        update_query += ", ".join(updates)
        update_query += f" WHERE doc_id = '{doc_id}'"
        update_job = client.query(update_query)
        update_job.result()
        logging.info(f"Row with doc_id {doc_id} updated successfully.")
        return True
    except Exception as e:
        logging.Error(f"Error updating row of doc_id: {doc_id}. Error message: {e}")
        return False

def delete_bigquery_table_data(client):
    """Deletes all data from a BigQuery table.

    Args:
        project_id: Google Cloud project ID.
        dataset_id: BigQuery dataset ID.
        table_id: BigQuery table ID.
    """
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE_ID}"
    try:
        # Use a delete job to remove all rows efficiently.
        delete_query = f"DELETE FROM `{table_ref}` WHERE TRUE"
        query_job = client.query(delete_query)
        query_job.result()  # Wait for the query to complete
        logging.info(f"All data deleted from table {table_ref}")
    except Exception as e:
        logging.Error(f"Error deleting data from table: {e}")

def check_bigquery_table_has_data(client):
    """Checks if a BigQuery table has any data.

    Args:
        project_id: Your Google Cloud project ID.
        dataset_name: The name of the BigQuery dataset.
        table_name: The name of the BigQuery table.

    Returns:
        True if the table has data, False otherwise.
    """

    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE_ID}"

    try:
        query = f"SELECT COUNT(*) FROM `{table_ref}`"
        query_job = client.query(query)
        row_count = list(query_job)[0][0]
        return row_count > 0  # Table has data if row_count is greater than 0
    except Exception as e:
        logging.Error(f"Error checking table: {e}")
        return False  # Assume no data in case of error
