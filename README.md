# Wikipedia ChatBot

## Overview
This FastAPI application allows users to initiate background tasks for retrieving and saving Wikipedia page, and chat with ChatGPT using the information from a specified document and previous chat history. It includes three main routes: one for starting a background task, one for checking the task status, and one for chatting with a bot. Task statuses are tracked, and session history is saved to enable ongoing interactions with the chatbot.
 
## Routes
The application contains three main routes:
1. `POST /api/v1/process`: Start a background task.
2. `GET /api/v1/status/{task_id}`:  Checks the status of a background task based on the `task_id`.
3. `POST /api/v1/chat`: Starts a chat with a bot.

## Backround task processor
The background task processor is implemented using FastAPI's BackgroundTasks. The background task fetches data by a given topic from Wikipedia using the wikipedia library. The result is saved in a TXT file `data/documents/{document_id}.txt`. Statuses for each task are tracked and can be queried.

## Task Statuses  
To track and manage the statuses of background tasks, a custom class is implemented using FastAPI's Depends dependency injection.

- `pending`: Assigned when the task is first created.
- `running`: Assigned when the background task begins processing.
- `finished`: Assigned when the task is successfully completed.
- `failed`: Assigned if an error occurs during the task.
- `not found`: Assigned if an invalid task_id is provided when checking the task status.

## Chatbot
The chatbot uses OpenAI's GPT model, with the document’s and session's contents inserted into the prompt, and stores the session history in a JSON file `data/documents/{session_id}.json` for future interactions. The system makes use of the chat completions, where a series of messages, including system instructions and user input, are sent to generate contextual responses.

## Project structure

```
trainee-test-assignment
├── README.md
├── requirements.txt
├── docker
│   └── Dockerfile
├── data
│   ├── documents
│   └── sessions
└── src
    ├── app.py
    ├── worker.py
    └── status_manager    - contains the code for managing and storing task statuses
        ├── dependencies.py
        └── store_class.py
```

## Running Instructions
**IMPORTANT:** Ensure you have a valid OpenAI API key set in your environment variables or a .env file.

To run the application using Docker, follow the steps below:  
**1. Clone the repository:**  
Firstly, navigate to the target directory using `cd` where you want to store the repository. Then run `git clone`:
``` 
git clone https://github.com/anastasia-butkevich/trainee-test-assignment.git
```
**2. Build the Docker Image:**  
In the terminal, from the repository's root directory, run:
```
docker build -t chat_app -f docker/Dockerfile .
```
**3. Run the Docker Container**  
Start the container:
```
docker run -p 8000:8000 chat_app
```
**4. Access the Application:**  
After running the container, you can access the application by navigating to `http://localhost:8000` in your web browser. You can test the API routes by visiting the `/docs/` endpoint, or you can use Postman or curl in the terminal.

**5. Stopping the Application:**  
Stop the container by running:
```
docker stop <container-id>
```
