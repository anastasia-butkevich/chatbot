import os
import logging
import json
import wikipedia as wiki
from openai import OpenAI 
from .status_manager.store_class import TaskStatuses
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_data(topic: str, document_id: str, task_id: str, task_statuses: TaskStatuses):
    """
    Process a task by updating its statuses and saving the content of a Wikipedia page to a TXT file.
    
    :param topic: string content with the user request
    :param document_id: identifier for results storing
    :param task_id: identifier of a corresponding task
    :param task_statuses: object that manages task statuses

    """
    task_statuses.set_status_running(task_id) 


    page_content = retrieve_wikipedia_content(topic)
    if not page_content:
        task_statuses.set_status_failed(task_id)
        return

    file_path = f"data/documents/{document_id}.txt"
    save_text_to_file(file_path, page_content)

    task_statuses.set_status_finished(task_id)
    
    if not os.path.exists(file_path):
        task_statuses.set_status_failed(task_id)

    
def retrieve_wikipedia_content(topic: str) -> str | None:
    """Fetch Wikipedia content for a given topic."""
    try:
        return wiki.page(topic, auto_suggest=False).content
    except wiki.DisambiguationError as e:
        logger.warning(f"Disambiguation error: {topic}. Trying alternatives.")
        return resolve_disambiguation(e.options)
    except wiki.PageError:
        logger.error(f"Page not found for topic: {topic}")
    except Exception as e:
        logger.error(f"Unexpected error retrieving Wikipedia content: {e}")
    return None

    
def resolve_disambiguation(options: list[str]) -> str | None:
    """Try fetching the first available page from disambiguation options."""
    for option in options:
        try:
            return wiki.page(option, auto_suggest=False).content
        except wiki.PageError:
            logger.warning(f"Skipping unavailable Wikipedia page: {option}")
        except Exception as e:
            logger.error(f"Unexpected error resolving disambiguation: {e}")
    return None


def get_chat_response(session_id: str, document_id: str, inputs: str) -> str:
    """
    Generate a chat response based on stored document content and chat history.

    :param session_id: identifier of current session
    :param document_id: identifier of relevant page
    :param inputs: inputs to the chat
    
    :return: bot response

    :raise ValueError: if the OPENAI_API_KEY is missing
    """
    doc_path = f"data/documents/{document_id}.txt"
    session_path = f"data/sessions/{session_id}.json"
    session_history = get_session_history(session_path)

    if not OPENAI_API_KEY:
        raise ValueError("API key is missing. Please set the OPENAI_API_KEY variable.")
    
    if not os.path.exists(doc_path):
        logger.warning(f"File not found: {doc_path}")
        return "Error: The requested document does not exist. Please provide a valid document_id."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
        )
    chat_id = len(session_history.get("session_history", [])) + 1
    doc_content = read_text_from_file(doc_path)

    chat_output = ""
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that reads files and answers user questions."},
                {"role": "user", "content": f"Documents:\n{doc_content}\n\n{session_history}\n\nUser question: {inputs}"}
            ]
        )
        chat_output = completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
    
    chat_history = {
            "id": chat_id,
            "user_input": inputs,
            "response": chat_output,
            "document_id": document_id
        }
    update_session_history(session_path, chat_history)

    return chat_output


def get_session_history(session_path: str) -> dict:
    """Retrieve session history from a JSON file, creating one if necessary."""
    if not os.path.exists(session_path):
        save_json_to_file(session_path, {"session_history": []})
        logger.info(f"Created new session JSON file: {session_path}")

    return read_json_from_file(session_path)


def update_session_history(session_path: str,  chat_history: dict):
    """Append chat history to the session file."""
    session_data = read_json_from_file(session_path)
    session_data["session_history"].append(chat_history)
    save_json_to_file(session_path, session_data)


# I/O operations functions
def save_text_to_file(file_path: str, content: str):
    """Save text content to a file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding="utf8") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error writing into the file: {e}")


def read_text_from_file(file_path: str) -> str | None:
    """Read text content from a file, returning None if missing."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
    except OSError as e:
        logger.error(f"Failed to read file {file_path}: {e}")
    return None


def save_json_to_file(file_path: str, data: dict):
    """Save dictionary data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")


def read_json_from_file(file_path: str) -> dict:
    """Read JSON content from a file, returning an empty dictionary if doesn't exist."""
    if not os.path.exists(file_path):
        logger.warning(f"JSON file not found: {file_path}")
        return {"session_history": []}
    
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            content = json.load(f)
        return content
    except Exception as e:
        logger.error(f"Error reading from JSON file: {e}")
    return {"session_history": []}
