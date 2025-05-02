import os
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://api:8000/api")

st.set_page_config(page_title="WikiPedia ChatBot", layout="centered")
st.title("WikiPedia ChatBot")

tab1, tab2 = st.tabs(["Find Page", "Ask a Question"])

with tab1:
    st.header("Find a Wiki Topic")
    topic = st.text_input("Enter a topic to search Wikipedia:")
    if st.button("Process Topic"):
        if topic.strip():
            with st.spinner("Processing topic..."):
                response = requests.post(f"{API_URL}/process", json={"topic": topic})
                if response.ok:
                    task_id = response.json()["task_id"]
                    st.session_state["task_id"] = task_id 
                    st.session_state["document_id"] = task_id.replace("_task", "")
                    st.success("Task started successfully. You can check the status.")
                else:
                    st.error("Error submitting topic to backend.")

    if "task_id" in st.session_state:
        if st.button("Check Task Status"):
            task_id = st.session_state["task_id"]
            res = requests.get(f"{API_URL}/status/{task_id}")
            if res.ok:
                status = res.json()["status"]
                st.info(f"Current status: {status}")
                if status == "finished":
                    st.session_state["document_ready"] = True
            else:
                st.error("Could not fetch task status.")

with tab2:
    st.header("Ask a Question about the Topic")

    if not st.session_state.get("document_ready"):
        st.warning("Please process a topic first and wait for it to finish.")
    else:
        document_id = st.session_state["document_id"]
        question = st.text_input("Your Question")

        if st.button("Send Question"):
            if question.strip():
                payload = {
                    "document_id": document_id,
                    "text": question
                }
                response = requests.post(f"{API_URL}/chat", json=payload)
                if response.ok:
                    st.success("AI Response:")
                    st.write(response.json()["response"])
                else:
                    st.error("Failed to get a response from the backend.")
            else:
                st.warning("Please enter a question.")
