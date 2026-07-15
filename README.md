# ✈️ WanderAI – AI-Powered Travel Planner

>Personalised day-wise travel itineraries generated using Meta Llama 3.3 70B Instruct via IBM watsonx.ai.
> Built with Python Flask and a responsive Bootstrap 5 frontend.

---

## 📌 Features

| Feature | Details |
|---|---|
| 🗓️ Day-wise Itinerary | Morning / Afternoon / Evening breakdown for every day |
| 🏨 Hotel Recommendations | Budget, mid-range, and luxury options with price ranges |
| 🚌 Transportation Guide | How to get there and move around locally |
| 💰 Budget Breakdown | Per-person and total estimated costs |
| 🎒 Packing Checklist | Destination-specific essentials |
| 🌤️ Weather Advice | Climate expectations and seasonal tips |
| 🗺️ Attractions & Food | Top spots, hidden gems, and must-try dishes |
| 🛡️ Safety Tips | Destination-specific guidance |
| 💬 Chat Interface |  Multi-turn follow-up questions powered by Meta Llama 3.3 |
| 👥 Travel Types | Solo, couple, family, and group travel support |

---

## 🏗️ Project Structure

```
travel_planner/
├── app.py                  # Flask application entry point
├── agent.py                # IBM watsonx.ai / Granite agent module
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (never commit this)
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       ├── app.js          # Shared JS (loading overlay)
│       └── result.js       # Itinerary page (markdown render + chat)
└── templates/
    ├── index.html          # Travel planning form
    └── result.html         # Itinerary results + chat dashboard
```

---

## ⚙️ Prerequisites

- Python 3.10+
- An **IBM Cloud** account
- A **watsonx.ai** project (free tier available)
- Your **IBM Cloud API Key**

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Enter the Project

```bash
git clone https://github.com/your-username/wander-ai.git
cd wander-ai/travel_planner
```

### 2. Create & Activate a Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file and fill in your credentials:

```dotenv
IBM_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com   # or your region's URL
FLASK_SECRET_KEY=generate-a-random-string-here
FLASK_ENV=development
FLASK_DEBUG=True
APP_PORT=5000
```

> 🔐 **Never commit `.env` to version control.**  
> Add it to your `.gitignore`.

#### How to get your credentials

| Credential | Where to find it |
|---|---|
| `IBM_API_KEY` | IBM Cloud → Manage → Access (IAM) → API keys → Create |
| `WATSONX_PROJECT_ID` | watsonx.ai → Projects → Your project → Manage → General → Project ID |
| `WATSONX_URL` | Region-specific: `us-south`, `eu-de`, `au-syd`, `jp-tok` |

### 5. Run the App

```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## 🌐 Deployment

### Option A – Gunicorn (Linux / macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option B – IBM Code Engine

1. Containerise with the Dockerfile below
2. Push to IBM Container Registry
3. Deploy as a Code Engine application

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
# Build & push
ibmcloud cr build -t us.icr.io/<namespace>/wander-ai:latest .

# Deploy on Code Engine
ibmcloud ce application create \
  --name wander-ai \
  --image us.icr.io/<namespace>/wander-ai:latest \
  --env-from-secret wander-ai-secrets \
  --port 5000
```

### Option C – Heroku / Railway / Render

Create a `Procfile`:

```
web: gunicorn app:app
```

Set environment variables in the platform dashboard and deploy.

---

## 🔧 Customising the Agent

All agent behaviour is controlled by the `AGENT_INSTRUCTIONS` constant in [`agent.py`](agent.py).

```python
# agent.py
AGENT_INSTRUCTIONS = """
You are an expert AI Travel Planner named "WanderAI"…
# Edit persona, tone, output format, constraints here
"""
```

You can also switch to another supported watsonx.ai foundation model:

```python
MODEL_ID = "meta-llama/llama-3-3-70b-instruct"   # change to another supported model
```

Adjust generation parameters:

```python
GENERATION_PARAMS = {
    GenParams.MAX_NEW_TOKENS: 3000,   # increase for longer itineraries
    GenParams.TEMPERATURE:    0.7,    # higher = more creative
    GenParams.TOP_P:          0.9,
}
```

---

## 🔌 Future Integrations

The modular design makes these easy to add:

| Integration | How |
|---|---|
| 🗺️ Google Maps / Mapbox | Embed maps for each attraction |
| 🌦️ OpenWeatherMap | Real-time weather for travel dates |
| ✈️ Amadeus / Skyscanner | Live flight price search |
| 🏨 Booking.com API | Real-time hotel availability |
| 📅 Google Calendar | Export itinerary as calendar events |
| 💳 Currency API | Live exchange rates |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with IBM Bob &nbsp;|&nbsp; Powered by watsonx.ai and Meta Llama 3.3 70B Instruct
</p>
