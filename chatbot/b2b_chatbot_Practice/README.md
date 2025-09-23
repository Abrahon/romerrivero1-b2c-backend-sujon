# Chatbot for B2B - FastAPI & Pinecone

This project provides a FastAPI backend for managing and querying chatbot training data using Pinecone vector database and Google Gemini LLM/embeddings.

## Features

- Add, edit, and delete training data (FAQ, product info, etc.)
- Query chatbot answers using RetrievalQA and Gemini LLM
- Stores data in Pinecone vector database

## Requirements

- Python 3.10+
- Pinecone account & API key
- Google Generative AI API key
- The following Python packages:
  - fastapi
  - uvicorn
  - pydantic
  - python-dotenv
  - langchain
  - langchain-google-genai
  - langchain-pinecone
  - pinecone-client

## Setup

1. Clone this repo.
2. Install dependencies:

    ```python
    %pip install fastapi uvicorn python-dotenv langchain langchain-google-genai langchain-pinecone pinecone-client
    ```

3. Create a `.env` file with your API keys:

    ```
    PINECONE_API_KEY=your_pinecone_api_key
    GOOGLE_API_KEY=your_google_api_key
    ```

4. Make sure your Pinecone index is created and named `shihab-chatbot`.

5. Run the server:

    ```python
    uvicorn final_project_till_8-20-25:app --reload
    ```

## API Endpoints

- `POST /train_data?doc_id=...` — Add training data (provide doc_id)
- `PUT /train_data/{edit_id}` — Edit training data by ID
- `DELETE /train_data/{delete_id}` — Delete training data by ID
- `POST /query` — Query chatbot (provide `{ "query": "your question" }`)

## Notes

- All training data fields are required.
- Keywords should be provided as a list of strings.
#
