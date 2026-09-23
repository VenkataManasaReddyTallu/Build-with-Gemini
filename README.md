# 🍳 Sous-Chef AI — Autonomous Culinary Agent & Modern Chat Application

**Sous-Chef AI** is a full-stack, production-grade autonomous agent system built with the **Google Agent Development Kit (ADK)**, **Gemini 3.1 Flash Lite**, **A2UI (Agent-to-User Interface v0.8)**, and deployed on **Google Cloud Vertex AI Agent Engine** and **Cloud Run**.

It enables home cooks to manage local cookbook recipes in Firestore, search global online recipe databases, scale yield portions, and generate vibrant dish presentation photos uploaded directly to Google Cloud Storage.

---

## 🌟 Key Features

- **📖 Firestore Cookbook Management**: Save, search, retrieve, and scale recipe yields directly in Google Cloud Firestore.
- **🌏 Real-Time Public API Lookup**: Query external recipe databases (Spoonacular API) for fresh global cooking inspiration.
- **📸 AI Dish Photo Generation**: Uses `gemini-3.1-flash-lite-image` in global region to generate high-resolution dish presentation photos, storing image artifacts to a public Google Cloud Storage bucket (`gs://sous-chef-recipes-...`).
- **🎨 Interactive A2UI Component System**: Uses A2UI Schema Manager (v0.8) and Basic Catalog to render structured cards, metadata badges, timing metrics, and dish photos.
- **🚀 Cloud Native & Serverless Architecture**:
  - **Backend Agent Engine**: Hosted on Vertex AI Reasoning Engine (`us-east1`).
  - **Frontend Proxy**: Minimal FastAPI proxy hosted on Cloud Run (`us-central1`).
  - **Modern Web UI**: Responsive glassmorphic dark UI with Google Fonts (`Outfit` & `Inter`), quick action chips, and animated typing indicators.

---

## 🏗️ Architecture & Project Structure

```
sous-chef-agent/
├── app/
│   ├── agent.py               # Main ADK Agent setup, instructions, and callbacks
│   ├── a2ui_utils.py          # A2UI after_model_callback transformer
│   └── tools/
│       └── firestore_tools.py # Firestore CRUD, API lookup, and GCS image generation
├── frontend/
│   ├── main.py                # FastAPI proxy handling A2A protocol & ADC authentication
│   ├── Procfile               # Cloud Run web process entrypoint
│   ├── requirements.txt       # Frontend dependencies (FastAPI, uvicorn, a2a-sdk)
│   └── static/
│       └── index.html         # High-end gourmet chat UI with A2UI renderer
├── agents-cli-manifest.yaml   # Agent Engine deployment manifest
├── deployment_metadata.json   # Active deployment resource metadata
├── pyproject.toml             # Agent project dependencies (google-adk, a2ui-agent-sdk)
└── README.md                  # Project documentation
```

---

## 🛠️ Tools & Capabilities

| Tool Name | Type | Description |
| :--- | :--- | :--- |
| `search_recipes` | Firestore | Searches stored cookbook recipes by title or category tags. |
| `get_recipe` | Firestore | Fetches full ingredients and step-by-step instructions for a specific recipe. |
| `add_recipe` | Firestore | Stores a new recipe in the Firestore database. |
| `scale_recipe_yield` | Logic | Dynamically rescales ingredient quantities for target serving sizes. |
| `lookup_online_recipes` | Public API | Searches Spoonacular API for online recipe ideas matching dietary preferences. |
| `generate_dish_photo` | Imagen / GCS | Generates dish photos using `gemini-3.1-flash-lite-image`, uploads to GCS, and returns public HTTPS URL. |

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.10+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Google Cloud SDK (`gcloud`) with active GCP Project & Application Default Credentials (`gcloud auth application-default login`)

### 2. Install Dependencies
```bash
# Clone repository
git clone <your-repo-url>
cd sous-chef-agent

# Sync virtual environment
uv sync
```

### 3. Run Agent Engine Playground (Local Testing)
```bash
agents-cli web
```
Open [http://localhost:8000](http://localhost:8000) to test agent reasoning, memory, and A2UI card generation.

### 4. Run Frontend Proxy Locally
```bash
cd frontend
uv pip install --python ../.venv -r requirements.txt
AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/us-east1/reasoningEngines/<ENGINE_ID>" \
AGENT_DIRECTORY="app" \
PORT=8080 \
uv run python main.py
```
Open [http://localhost:8080](http://localhost:8080) to interact with the agent via the custom UI.

---

## ☁️ Cloud Deployment

### 1. Deploy Agent to Vertex AI Agent Engine
```bash
agents-cli deploy --no-confirm-project
```

### 2. Deploy Frontend Proxy to Cloud Run
```bash
cd frontend
gcloud run deploy sous-chef-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<YOUR_AGENT_ENGINE_RESOURCE_NAME>",AGENT_DIRECTORY="app"
```

### 3. Configure IAM Access Permissions
Ensure the Cloud Run service account has `roles/aiplatform.user` permission to query the Reasoning Engine:
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT>" \
  --role="roles/aiplatform.user"
```

---

## 📜 License
Licensed under the Apache License, Version 2.0.
