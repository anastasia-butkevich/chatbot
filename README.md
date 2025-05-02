# Wikipedia ChatBot

## Overview
This FastAPI application allows users to initiate background tasks for retrieving and saving Wikipedia page, and chat with ChatGPT using the information from a specified document and previous chat history. It includes three main routes: one for starting a background task, one for checking the task status, and one for chatting with a bot. Task statuses are tracked, and session history is saved to enable ongoing interactions with the chatbot.
 
## Routes
The application contains three main routes:
1. `POST /api/process`: Start a background task.
2. `GET /api/status/{task_id}`:  Checks the status of a background task based on the `task_id`.
3. `POST /api/chat`: Starts a chat with a bot.

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

## Frontend
The application includes a Streamlit frontend with a simple and intuitive user interface. The frontend is structured as follows:

- **Page Configuration**: Sets up the page title and layout
- **Tabbed Interface**: Contains two tabs for different functionality
 - **Find Page Tab**: Allows users to search and process Wikipedia topics and check the task status.
 - **Ask a Question Tab**: Enables users to ask questions related to the processed topic and get AI responses.

The frontend communicates with the FastAPI backend through API requests and maintains state using Streamlit's session state functionality.

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
**IMPORTANT:** Ensure you have a valid OpenAI API key set in your environment variables or a `.env` file.

### **1. Clone the Repository**  
Firstly, navigate to the target directory where you want to store the repository. Then run:

git clone https://github.com/anastasia-butkevich/trainee-test-assignment.git

### **2. Create the `.env` File**  
Make sure to add a `.env` file in the root of the project with the API key:
```
OPENAI_API_KEY=your_openai_api_key
```

### **3. Build and Run the Application with Docker Compose**  
In the terminal, from the repository's root directory, run the following command to build the containers and start them:
```
docker-compose -f docker_compose.yml up --build
```
This will build the Docker image(s) and start both the FastAPI backend and Streamlit frontend as services defined in the `docker-compose.yml` file.

### **4. Access the Application**  
After running the container with Docker Compose, you can access the application as follows:

- **FastAPI Backend**: Navigate to `http://localhost:8000` in your browser.  
  You can test the API routes by visiting the `/docs/` endpoint or use tools like Postman or curl in the terminal.

- **Streamlit UI**: Navigate to `http://localhost:8501` to access the Streamlit front-end.

### **5. Stopping the Application**  
To stop the containers, run the following command:
```
docker-compose -f docker_compose.yml down
```

This will bring down both services and free up the ports used by Docker. If you only need to stop the running containers without removing them, you can use:
```
docker-compose -f docker_compose.yml stop
```
