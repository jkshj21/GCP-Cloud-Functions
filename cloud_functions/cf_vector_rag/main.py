
import os
import functions_framework
import vertexai
from flask import Flask, request, jsonify
from langchain_google_vertexai import VertexAI
from routes import preproc_run_route_controller, vs_similarity_search_controller, update_document_controller

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
app = Flask(__name__)

@app.route('/vectorStore/chains/qa', methods=['GET', 'POST'])
def vs_similarity_search():
    return vs_qa_chain_controller(data=request.get_json())

@app.route('/preproc/run', methods=['GET', 'POST'])
def run_preprocessing():
    return preproc_run_route_controller(data=request.get_json())

@app.route('/preproc/documents/<string:id>', methods=['GET', 'POST'])
def update_document(id):
    if update_document_controller(doc_id=id, data=request.get_json()):
        return "Updated the document successfully"
    else:
        return "Failed to update the document"

def my_function(request):
    """
    Handles incoming requests and dispatches them to the internal Flask app.

    Args:
        request: The Cloud Function request object.

    Returns:
        The response from the internal Flask app.
    """
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    with app.test_request_context(
        path=request.path, method=request.method, 
        headers={k: v for k, v in request.headers.items()}, 
        data=request.data
    ):
        return app.full_dispatch_request()
