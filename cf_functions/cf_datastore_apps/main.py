import os
import logging
import json
from flask import Flask, request, jsonify
from typing import Dict, Any, List
from dfcx_scrapi.tools import webhook_util
from routers import answer_route_controller, search_route_controller, conversation_route_controller

app = Flask(__name__)

@app.route('/conversation', methods=['GET', 'POST'])
def ask_by_covnersation():
    """
    Handles conversation requests.

    Retrieves JSON data from the request, passes it to the conversation route controller,
    and returns a webhook response for conversation.

    Returns:
        str: JSON string of the webhook response.
    """
    response = conversation_route_controller(data=request.get_json())
    return fetch_wb_for_conversation(response)

@app.route('/search', methods=['GET', 'POST'])
def ask_by_search():
    """
    Handles search requests.

    Retrieves JSON data from the request, passes it to the search route controller,
    and returns a webhook response for search.

    Returns:
        str: JSON string of the webhook response.
    """
    response = search_route_controller(data=request.get_json())
    return fetch_wb_for_search(response)

@app.route('/answer', methods=['GET', 'POST'])
def ask_by_answer():
    """
    Handles answer requests.

    Retrieves JSON data from the request, passes it to the answer route controller,
    and returns a webhook response for answer.

    Returns:
        str: JSON string of the webhook response.
    """
    response = answer_route_controller(data=request.get_json())
    return fetch_wb_for_answer(response)

def fetch_wb_for_conversation(res):
    """
    Builds a webhook response for conversation based on the provided result.

    Args:
        res (Dict[str, Any]): The result from the conversation route controller.

    Returns:
        str: JSON string of the webhook response.
    """
    if res:
        wbhk_util = webhook_util.WebhookUtil()
        session_info = wbhk_util.build_session_info(
            parameters={
                "ds_reply": res["reply"],
                "ds_summary": res["summary"],
                "ds_session": res["session"],
                "ds_state": res["state"]
                
            }
        )
        wb_response = wbhk_util.build_response(
                response_text=res["reply"],
                session_info=session_info,
                append=True
            )
        response = json.dumps(wb_response)
        logging.info(response)
    else:
        return fetch_error_message({
            "ds_error": True,
            "error_message": "failed to return a reply"
            })
    return response

def fetch_wb_for_search(res):
    """
    Builds a webhook response for search based on the provided result.

    Args:
        res (Dict[str, Any]): The result from the search route controller.

    Returns:
        str: JSON string of the webhook response.
    """
    if res:
        wbhk_util = webhook_util.WebhookUtil()
        wb_response = wbhk_util.build_response(
                response_text=res["search"],
                append=True
            )
        response = json.dumps(wb_response)
        logging.info(response)
    else:
        return fetch_error_message({
            "ds_error": True,
            "error_message": "failed to search a repsonse"
            })
    return response

def fetch_wb_for_answer(res):
    """
    Builds a webhook response for answer based on the provided result.

    Args:
        res (Dict[str, Any]): The result from the answer route controller.

    Returns:
        str: JSON string of the webhook response.
    """
    if res:
        wbhk_util = webhook_util.WebhookUtil()
        session_info = wbhk_util.build_session_info(
            parameters={
                "ds_answer": res["answer"],
                "ds_related_questions": res["related_questions"]
            }
        )
        if "session_id" in res:
            session_info["ds_session"] = res["session_id"]
        if "state" in res:
            session_info["ds_state"] = res["state"]
        wb_response = wbhk_util.build_response(
                response_text=res["answer"],
                session_info=session_info,
                append=True
            )
        response = json.dumps(wb_response)
        logging.info(response)
    else:
        return fetch_error_message({
            "ds_error": True,
            "error_message": "failed to return an answer repsonse"
            })
    return response

def fetch_error_message(error: Dict[str, Any]):
    """
    Builds a webhook response for an error message.

    Args:
        error (Dict[str, Any]): A dictionary containing error information.

    Returns:
        str: JSON string of the error webhook response.
    """
    wbhk_util = webhook_util.WebhookUtil()
    session_info = wbhk_util.build_session_info(
        parameters={
            "ds_error": error["ds_error"],
            "ds_error_message": error["error_message"]
        }
    )
    wb_response = wbhk_util.build_response(
            response_text="Sorry, I am unable to answer your question.",
        )
    response = json.dumps(wb_response)
    logging.info(response)
    return response

def hello_http(request):
    """
    Handles HTTP requests and dispatches them to the Flask application.

    Args:
        request: The HTTP request object.

    Returns:
        The result of the Flask application's dispatch.
    """
    logging.info(f"Request body is :{request}")
    with app.test_request_context(
        path=request.path, method=request.method, 
        headers={k: v for k, v in request.headers.items()}, 
        data=request.data
    ):
        return app.full_dispatch_request()
