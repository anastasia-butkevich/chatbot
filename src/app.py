from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel, Field, field_validator

from .worker import parse_data, get_chat_response
from .status_manager.store_class import TaskStatuses
from .status_manager.dependencies import task_statuses_instance


app = FastAPI()


class ProcessInputs(BaseModel):
    topic: str
    document_id: str = Field(..., max_length=50)


    @field_validator("document_id")
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class ChatInputs(BaseModel):
    session_id: str = Field(..., max_length=50)
    document_id: str = Field(..., max_length=50)
    text: str


    @field_validator("session_id", "document_id", "text")
    def check_non_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


@app.post("/api/v1/process")
async def process(inputs: ProcessInputs, background_tasks: BackgroundTasks, task_statuses: TaskStatuses = Depends(task_statuses_instance)):
    """
    Accept textual requests and launch a background task to gather textual information from Wikipedia.

    :return: task_id of the background task that was started
    """
    task_id = f"{inputs.document_id}_task"
    task_statuses.set_status_pending(task_id)

    background_tasks.add_task(parse_data, inputs.topic, inputs.document_id, task_id, task_statuses)

    return {"task_id": task_id}


@app.get("/api/v1/status/{task_id}")
def status(task_id: str, task_statuses: TaskStatuses = Depends(task_statuses_instance)):
    """
    Check the status of the background task. It should receive a task_id path parameter and return the status of the task.
    The task can have four possible statuses: pending, running, finished, or failed.

    :param task_id: str

    :return: status of the background task (pending, running, finished, or failed)
    """
    status = task_statuses.get_status(task_id)
    return {"status": status}


@app.post("/api/v1/chat")
def chat(inputs: ChatInputs):
    """
    Endpoint for interaction with СhatGPT. The document with `document_id` identifier should be inserted
    into СhatGPT prompt, so the user will be able to chat about specific topic.

    :param inputs: ChatInputs
        1. session_id – session identifier to keep track of the conversation.
        2. document_id - identified of a textual document to insert into prompt.
        2. text – user input text

    :return: bot response
    """
    response = get_chat_response(inputs.session_id, inputs.document_id, inputs.text)

    return {"response": response}


@app.get("/-/healthy/")
def healthy():
    return {}
