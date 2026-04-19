You are a senior full-stack engineer and AI integration expert.

Your task is to integrate local AI capabilities into an existing GRC platform (CISO Assistant Community), which uses:

* Backend: Django (Python)
* Frontend: SvelteKit
* Infrastructure: Docker

The goal is to add practical AI features (NOT just a chatbot) using a local LLM via Ollama.

---

## 🧠 AI Architecture Requirements

* Use Ollama as the local LLM runtime
* Default model: llama3 (fallback: mistral or phi3)
* All AI interactions must go through a backend API (Django)
* Do NOT call external APIs (no OpenAI or paid services)

---

## 🧩 Features to Implement

### 1. Risk AI Assistant (HIGH PRIORITY)

Location:

* Risk creation/edit page

UI:

* Add button: "Analyze Risk"

Behavior:

* User enters a short risk title or description
* AI generates:

  * Risk Description
  * Threat Scenario
  * Impact
  * Likelihood (Low/Medium/High + justification)
  * Risk Level
  * Recommended Mitigations
  * Security Domains

Backend:

* Create endpoint: POST /api/ai/analyze-risk
* Call Ollama API: http://ollama:11434/api/generate

---

### 2. Smart Auto-Fill

Location:

* All forms (Risk, Controls, Policies)

UI:

* Button: "Expand with AI"

Behavior:

* Takes short input and expands it into structured professional text

Backend:

* Endpoint: POST /api/ai/expand-text

---

### 3. Control Generator

Location:

* Controls module

UI:

* Button: "Generate Controls from Risk"

Behavior:

* Input: risk description
* Output:

  * List of controls
  * Description
  * Implementation guidance
  * Control type

Backend:

* Endpoint: POST /api/ai/generate-controls

---

### 4. Audit Finding Generator

Location:

* Audit module

UI:

* Button: "Generate Finding"

Behavior:

* Input: observation text
* Output:

  * Finding title
  * Description
  * Impact
  * Recommendation
  * Severity

Backend:

* Endpoint: POST /api/ai/generate-finding

---

### 5. Dashboard Insights

Location:

* Main dashboard

Behavior:

* Analyze system data (risks, controls, compliance)
* Output:

  * Top risks
  * Compliance gaps
  * Recommended actions
  * Summary

Backend:

* Endpoint: POST /api/ai/dashboard-insights

---

## ⚙️ Backend Implementation Details

* Create a new Django app: "ai"
* Centralize AI logic in a service file (ai_service.py)
* Use Python requests to call Ollama

Example:

```python
def call_ollama(prompt, model="llama3"):
    import requests
    response = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

---

## 🧠 Prompt Engineering

Each feature must use structured prompts.

Example for Risk:

"You are a cybersecurity risk expert. Generate a professional structured risk analysis for the following input: {{input}}"

Ensure outputs are clean and structured (prefer JSON format when possible).

---

## 🐳 Docker Requirements

* Add Ollama service to docker-compose
* Ensure backend can access Ollama via internal network

Example:

ollama:
image: ollama/ollama
ports:
- "11434:11434"

---

## 🎨 Frontend Requirements (Svelte)

* Add buttons for each AI feature
* Show loading state while AI is processing
* Autofill form fields with AI response
* Display results in structured format

---

## ⚠️ Constraints

* No external APIs
* Keep responses deterministic and structured
* Handle errors gracefully
* Avoid hallucinated data where possible

---

## ✅ Deliverables

* Working Django endpoints for all AI features
* Integrated Svelte UI buttons
* Docker setup with Ollama
* Clean, maintainable code
* Basic documentation in README

---

Focus on clean architecture, modular code, and production-ready implementation.
