import os
import logging
import string
import json
from typing import Optional, Dict, Any, List
from google.cloud.discoveryengine_v1beta import types
from google.api_core import datetime_helpers

from search import Search
from google.cloud.discoveryengine_v1beta import types

def search_route_controller(data):
    """
    Handles search requests.

    Args:
        data (Dict[str, Any]): The request data containing user utterance.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing search results, or None if no utterance.
    """
    utterance = get_utterance(data)
    if utterance:
        return query_by_search(query=utterance)
    return None

def answer_route_controller(data):
    """
    Handles answer requests.

    Args:
        data (Dict[str, Any]): The request data containing user utterance and session parameters.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing answer results, or None if no utterance.
    """
    utterance = get_utterance(data)
    session = None
    if data.get("parameters"):
        session = data.get("parameters").get("ds_session", None)
    if utterance:
        return query_by_answer(query=utterance, session=session)
    return None

def conversation_route_controller(data):
    """
    Handles conversation requests.

    Args:
        data (Dict[str, Any]): The request data containing user utterance and session parameters.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing conversation results, or None if no utterance.
    """
    utterance = get_utterance(data)
    session = None
    if data.get("parameters"):
        session_json = data.get("parameters").get("ds_session", None)
    if utterance:
        return query_by_conversation(query=utterance, session=session_json)
    return None

def get_utterance(req):
    """
    Gets the user utterance from the request.

    Args:
        req (Dict[str, Any]): The webhook request.

    Returns:
        Optional[str]: A clean string from user's utterance, or None if no utterance found.
    """
    text = req.get("text")
    if not text:
        logging.warning("no plain text in request")
        text = req.get("transcript")
        if not text:
            logging.warning("no transcript in request")
            return None

    clean_utterance = text.lower().translate(
        str.maketrans("", "", string.punctuation))

    return clean_utterance

def query_by_search(query: str) -> Dict[str, Any]:
    """
    Queries by search.

    Args:
        query (str): The search query string.

    Returns:
        Dict[str, Any]: A dictionary containing search results, or an empty dictionary if an error occurred or no result was found.
    """
    datastore_id = os.environ.get("datastore_id")
    search_config: Dict[str, Any] = {
        "data_store_id": datastore_id,
        "query": query
    }
    s = Search()
    try:
        res = s.query_by_search(search_config=search_config, total_results=1)
    except Exception as e:
        logging.error(f"Failed to generate a search: {e}")
        return {}
    if res:
        try:
            search_result = res[0].document.derived_struct_data.get("extractive_answers")[0].get("content")
        except Exception as e:
            logging.error(f"Failed to extract a search content: {e}")
            return {}
        parsed_response: Dict[str, Any] = {
            "search": search_result,
        }
        return parsed_response
    return {}

def query_by_answer(query: str, session: Optional[str] = None) -> Dict[str, Any]:
    """
    Queries for an answer and related questions, optionally within a session.

    Args:
        query (str): The query string.
        session (Optional[str]): An optional session object.

    Returns:
        Dict[str, Any]: A dictionary containing the answer and related questions, or an empty dictionary if an error occurred or no result was found.
    """
    datastore_id = os.environ.get("datastore_id")
    answer_config: Dict[str, Any] = {
        "data_store_id": datastore_id,
        "query": query
    }
    answer_config["session"] = session.name if session else f"{datastore_id}/sessions/-"

    s = Search()
    try:
        res = s.query_by_answer(answer_config=answer_config, related_question=True)
    except Exception as e:
        logging.error(f"Failed to generate an answer: {e}")
        return {}
    if res and res.answer:
        related_questions: List[str] = list(res.answer.related_questions) if res.answer.related_questions else []
        parsed_response: Dict[str, Any] = {
            "answer": res.answer.answer_text if res.answer.answer_text else "",
            "related_questions": related_questions,
            "session_id": res.session.name,
            "state": res.session.state.name
        }
        return parsed_response
    return {}

def build_conv_session(session: Dict[str, Any])  -> types.conversation:
    """
    Builds a Conversation object from a session dictionary.

    Args:
        session (Dict[str, Any]): A dictionary containing session information.

    Returns:
        types.conversation: A Conversation object.
    """
    start_time = (
        datetime_helpers.DatetimeWithNanoseconds.from_rfc3339(session.get("start_date")) 
        if session.get("start_date") else None
    )
    end_time = (
        datetime_helpers.DatetimeWithNanoseconds.from_rfc3339(session.get("end_time")) 
        if session.get("end_time") else None
    )
    conversation = types.Conversation(
        name=session.get("name"),
        state=types.State(session.get("state")),
        user_pseudo_id=session.user_pseudo_id,
        messages=list(session.get("messages")),
        start_time=start_time,
        end_time=end_time
    )
    return conversation

def build_session_to_json(conversation: types.conversation) -> Dict[str, Any]:
    """
    Converts a Conversation object to a JSON-serializable dictionary.

    Args:
        conversation (types.conversation): A Conversation object.

    Returns:
        Dict[str, Any]: A dictionary representing the Conversation object.
    """
    conversation_data = {
        "name": conversation.name,
        "state": conversation.state,
        "user_pseudo_id": conversation.user_pseudo_id,
        "messages": conversation.messages,
        "start_time": conversation.start_time.rfc3339() if conversation.start_time else None,
        "end_time": conversation.end_time.rfc3339() if conversation.end_time else None,
    }

    return json.dumps(conversation_data, indent=2, default=str) 

def query_by_conversation(query: str, session: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Queries for a conversation and, optionally within a session.

    Args:
        query (str): The query string.
        session (Optional[Dict[str, Any]]): An optional session object.

    Returns:
        Dict[str, Any]: A dictionary containing the reply, or an empty dictionary if an error occurred or no result was found.
    """
    datastore_id = os.environ.get("datastore_id")
    conv_config: Dict[str, Any] = {
        "data_store_id": datastore_id,
        "query": query
    }
    conv_config["conversation"] = build_conv_session(session) if session else None

    s = Search()
    try:
        res = s.query_by_conversation(conv_config=conv_config, conversation=conv_config["conversation"])
    except Exception as e:
        logging.error(f"Failed to generate an answer: {e}")
        return {}
    if res:
        session_json = build_session_to_json(res.conversation)
        parsed_response: Dict[str, Any] = {
            "reply": res.reply.reply if res.reply else "",
            "summary": res.reply.summary.summary_text if res.reply else "",
            "session": session_json,
            "state": res.conversation.state.name
        }
        return parsed_response
    return {}
