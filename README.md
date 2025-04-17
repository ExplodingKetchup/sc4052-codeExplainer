# Code explainer

This project is a simple client-server LLM-based application for explaining code segments in public Github repositories. It is a part of SC4052 Assignment 2 submission.

## 🚀 Features

- 🤖 **Github Code Search API**
  The application uses Github Code Search API to obtain context and related code of the provided code segment from Github.

- 🤖 **AI-Powered Code Explanation**  
  The application uses **Gemini 2.0 Flash** to interpret requested code in the context gathered using Github Code Search API.

## Project Structure
```
SC4052-codeExplainer/
│
├── client.py              # Streamlit client (frontend)
├── gemini_interface.py    # Module to invoke AI-based code explanation
├── github_api_invoker.py  # Module to invoke Github Code Search API and other Github APIs
├── requirements.txt       # List of pip Dependencies
└── server.py              # Flask server (backend)
```

## Run the Project

### Prerequisites
- Python 3.13 or higher
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Create and populate `.env` file with your API key for GEMINI model and GITHUB API token (classic)
``` bash
GEMINI_API_KEY=
GITHUB_API_KEY=
```
### Step 1: Run the Flask Backend
1. Navigate to the project directory.
2. Start the Flask server:
   ```bash
   flask --app server run
   ```
3. The backend will run on `http://localhost:5000`.

### Step 2: Run the Streamlit Frontend
1. Open a new terminal and navigate to the project directory.
2. Start the Streamlit app:
   ```bash
   streamlit run client.py
   ```
3. The frontend will be accessible at `http://localhost:8501`.

## Notes
- The backend and frontend must run simultaneously for the application to function correctly.
- We encountered problem while performing Code Search on Github repositories with special characters (e.g. `-` or `_`) in their names. Please avoid testing on such repositories. This is a limitation of the Github Code Search API.
