# ⭐ ReviewBoost AI

**ReviewBoost AI** is an intelligent Google Business Profile review management and marketing assistant built with the **Google Agent Development Kit (ADK)**. It helps small and local businesses boost their Google reputation by calculating review goals, generating custom QR code feedback campaigns, managing customer review responses in Firestore, and creating AI promotional images and video campaigns.

---

## 🚀 Key Capabilities & Implemented Tools

All capabilities listed below are implemented and wired directly in `app/`:

- **🎯 Review Rating Calculator**: Calculates the exact number of 5-star reviews needed to reach a target rating goal (e.g., rising from 4.2 to 4.8 stars).
- **📱 QR Code Campaign Manager**: Generates Google Business review QR codes and persists campaigns in **Google Cloud Firestore**.
- **💬 Review Response Management**: Retrieves customer reviews from Firestore and updates responses.
- **🖼️ AI Image Generation**: Generates promotional cards and flyers using **Gemini 3.1 Flash Lite Image** (`gemini-3.1-flash-lite-image`) in the global region and uploads media directly to **Google Cloud Storage (GCS)**.
- **🎬 AI Video Generation**: Creates short promotional videos using **Gemini Omni Flash** (`gemini-omni-flash-preview`) in the global region and uploads them to GCS.
- **🧠 Cross-Session Long-Term Memory**: Uses Vertex AI **Memory Bank** (`PreloadMemoryTool`) to remember user preferences across sessions.
- **🎨 A2UI Rich Card Interface**: Emits A2UI (`v0.8 Basic Catalog`) structured cards, columns, rows, and images for interactive display.
- **🔒 Code Execution Sandbox**: Runs Python code safely inside the `AgentEngineSandboxCodeExecutor`.
- **📍 Local Business Search**: Searches local business addresses and Google Maps Place IDs (`search_local_business_address`).

---

## 🏗️ Architecture & Google Cloud Stack

- **Agent Framework**: Google ADK (Agent Development Kit) v1.1.0 (Python)
- **Model**: Gemini 2.5 Flash (`gemini-2.5-flash`)
- **Database**: Google Cloud Firestore
- **Media Storage**: Google Cloud Storage (GCS)
- **Memory**: Vertex AI Memory Bank
- **Proxy & Web Frontend**: FastAPI proxy server with single-page chat UI

---

## 📂 Project Structure

```
reviewboost-ai/
├── app/
│   ├── agent.py               # Main ADK Agent definition & tool registry
│   ├── a2ui_utils.py          # A2UI callback and schema configuration
│   ├── firestore_service.py   # Firestore database CRUD functions
│   ├── image_service.py       # Gemini 3.1 Flash Lite image generation
│   ├── video_service.py       # Gemini Omni Flash video generation
│   ├── external_service.py    # QR code API & local business search
│   └── fast_api_app.py        # ADK Web FastAPI entrypoint
├── frontend/
│   ├── main.py                # FastAPI proxy server (A2A protocol)
│   ├── requirements.txt       # Frontend dependencies
│   └── static/
│       └── index.html         # Custom single-page chat UI
├── agents-cli-manifest.yaml   # Deployment manifest
├── pyproject.toml             # Python dependencies (uv)
└── README.md                  # Project documentation
```

---

## 💻 Local Setup & Execution Instructions

### Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud` CLI) authenticated with active project
- `uv` or `pip` package manager

### 1. Clone & Install Agent Dependencies
```bash
git clone <your-repo-url>
cd reviewboost-ai
uv sync
```

### 2. Environment Variables
Set your Google Cloud project and region credentials:
```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-east1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

### 3. Run Agent Locally (ADK Web)
To test the agent locally using the ADK Web interface:
```bash
adk web --agent_dir app
```

### 4. Run Frontend Proxy Locally
To run the custom chat frontend locally:
```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/us-east1/reasoningEngines/<resource-id>"
export AGENT_DIRECTORY="app"
python main.py
```
Open a browser and navigate to port `8080` on localhost to interact with the frontend.

---

## 🧪 Running Unit & Integration Tests

Run the automated test suite using `pytest`:
```bash
GOOGLE_GENAI_USE_VERTEXAI=true GOOGLE_CLOUD_LOCATION=global uv run pytest
```
