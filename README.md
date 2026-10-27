# GhostWriter 👻 — Offline AI Horror Story Generator

> *"Every shadow has a story. Every story has a ghost."*

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026%20Open%20Source%20AI-orange?style=for-the-badge&logo=hacktoberfest)](https://hacktoberfest.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Local AI: Ollama](https://img.shields.io/badge/AI%20Runtime-Ollama-black?style=for-the-badge&logo=ollama)](https://ollama.ai/)
[![Privacy: 100% Offline](https://img.shields.io/badge/Privacy-100%25%20Offline-emerald?style=for-the-badge)](https://github.com/)

GhostWriter is an atmospheric, offline-first horror story generator designed for the **Hacktoberfest Open-Source AI Challenge: "Ghost in the Machine"**. 

Powered entirely by local, open-weight language models running through [Ollama](https://ollama.com/), GhostWriter manifests spine-chilling fiction directly on your hardware without sending a single character over the internet.

---

## 1. The Problem GhostWriter Solves

Traditional generative AI writing tools suffer from four critical flaws:
1. **Surveillance & Data Harvesting:** Cloud AI vendors log user prompts and creative stories for model training, analytics, and content moderation.
2. **Recurring Subscriptions & Token Invoices:** Writers face monthly cloud subscription fees and meter-draining API bills.
3. **Fragile Internet Dependence:** If Wi-Fi drops, planes takeoff, or corporate API servers experience outages, writing completely halts.
4. **Censorship & Creative Guardrails:** Corporate cloud models routinely refuse dark or unsettling creative fiction prompts, mistaking literary suspense for policy violations.

**GhostWriter liberates the creative process.** It provides an unmetered, privacy-preserving, and completely offline horror fiction studio that belongs entirely to the writer.

---

## 2. Core Features

- 🏚️ **Atmospheric Narrative Generator:** Customize eerie settings (Abandoned Mansions, Haunted Forests, Forgotten Hospitals, Deserted Railway Stations, or custom locations), tragic or skeptical protagonists, and tailored horror subgenres.
- 🩸 **5 Distinct Horror Subgenres:**
  - *Psychological Horror:* Creeping dread, paranoia, claustrophobia, and unreliable perception.
  - *Supernatural Ghost Story:* Spectral hauntings, cold spots, cursed relics, and restless spirits.
  - *Gothic Horror:* Decaying lineage, stormy melancholy, crumbling architecture, and ancestral guilt.
  - *Mystery and Suspense:* Macabre investigations, ticking clocks, and shocking narrative revelations.
  - *Funny Horror:* Absurd supernatural encounters colliding with dark comedy and sarcastic banter.
- ⚡ **Real-Time Token Streaming:** Watch prose manifest line by line through live local LLM streaming.
- 📜 **The Haunted Grimoire (Local SQLite Archive):** Persist your favorite nightmares locally in an ACID-compliant SQLite database with instant keyword search, subgenre filtering, and one-click bookmarking.
- 📥 **Zero-Friction Export:** Download stories as clean `.txt` files with formatted titles, atmospheric metadata, and word counts.
- 🕯️ **Immersive Halloween UI:** Dark midnight-purple and charcoal interface, subtle floating fog animations, glowing ghost iconography, and gothic typography via Google Fonts.
- 🔍 **Live AI Health Telemetry:** Real-time Ollama connectivity diagnostics, ping latency monitor, and dynamic model discovery right in the sidebar.

---

## 3. Architecture & Data Flow

GhostWriter uses a strictly separated, modular architecture ensuring zero network leakage:

```
+-------------------------------------------------------------+
|                      GhostWriter UI                         |
|             (Streamlit Dark Atmospheric Frontend)           |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Story Generator Engine                  |
|          (Input Validation & Dynamic Prompt Engineering)    |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                    Local Ollama Client                      |
|       (HTTP POST /api/generate & Streaming Token Parser)    |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                 Locally Hosted Open LLM                     |
|           (e.g., Qwen 2.5 3B / Llama 3.2 3B in VRAM)        |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Local Story Storage                     |
|               (SQLite Database: data/ghostwriter.db)        |
+-------------------------------------------------------------+
```

---

## 4. Hardware Requirements & Model Guide

GhostWriter runs smoothly on modern consumer hardware without enterprise cloud GPUs:

| Model | Parameters | Download Size | Minimum Hardware | Literary Profile |
| :--- | :--- | :--- | :--- | :--- |
| **Qwen 2.5 3B** *(Default)* | 3.09B | ~1.9 GB | 4 GB VRAM / 8 GB RAM | **Recommended:** Exceptional descriptive dread, rapid inference, and high coherence. |
| **Llama 3.2 3B** | 3.21B | ~2.0 GB | 4 GB VRAM / 8 GB RAM | Sharp dialogue, crisp pacing, very low latency. |
| **Qwen 2.5 1.5B** | 1.54B | ~986 MB | 2 GB VRAM / 4 GB RAM | Ultra-lightweight; runs fast even on older laptops or pure CPU. |
| **Gemma 2 2B** | 2.61B | ~1.6 GB | 3 GB VRAM / 6 GB RAM | Poetic vocabulary and rich world-building. |

> **Note on Operating Costs:** While local inference requires zero API subscriptions, running local models consumes local computing resources (CPU/GPU wattage and battery life).

---

## 5. Quickstart Installation (Windows PowerShell)

Follow these exact steps to launch GhostWriter on Windows:

### Step 1: Install & Start Ollama
1. Download and install Ollama from [ollama.com/download/windows](https://ollama.com/download/windows).
2. Open PowerShell and start the Ollama background daemon:
   ```powershell
   ollama serve
   ```
3. In a new PowerShell window, pull your chosen open-weight horror model:
   ```powershell
   ollama pull qwen2.5:3b
   ```
   *(Download size is ~1.9 GB. This requires internet only once during initial pull.)*

### Step 2: Clone or Navigate to GhostWriter
```powershell
cd D:\PIYUSH\GhostWriter
```

### Step 3: Create & Activate Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Configure Environment
Copy the example environment configuration:
```powershell
Copy-Item .env.example .env
```

### Step 6: Launch GhostWriter
```powershell
streamlit run app.py
```
Open your browser to **`http://localhost:8501`** and summon your first nightmare!

---

## 6. Offline Operation Guide

Once you have completed the initial installation and model pull:
1. Disconnect your internet connection or switch your computer to **Airplane Mode**.
2. Run `streamlit run app.py`.
3. GhostWriter will detect the locally installed model and generate full horror stories with **zero network connectivity**.

---

## 7. Automated Testing Suite

GhostWriter includes a comprehensive automated test suite testing prompt construction, input sanitization, SQLite persistence, and mocked Ollama error responses:

```powershell
pytest tests -v
```

### What is tested:
- ✅ **Prompt Engineering:** Verification of horror subgenre personas, formatting constraints, and parameter injection.
- ✅ **Input Validation:** Guarding against empty inputs, missing characters, invalid subgenres, and oversized prompts.
- ✅ **Title & Body Extraction:** Parsing clean story titles and separating markdown metadata.
- ✅ **SQLite Grimoire:** Database initialization, story insertion, text search, subgenre filtering, favorite toggling, and record deletion.
- ✅ **Ollama Network Fault Tolerance:** Mocked tests for Ollama offline, missing models (404), connection timeouts, and streaming token yields.

---

## 8. Why Open-Source AI Matters

GhostWriter was built to champion open-weight models and the open-source AI ecosystem:
- **Digital Sovereignty:** You own your model weights and your generation pipeline. No third party can revoke your access or alter the model underneath your application.
- **Auditable Safety & Integrity:** The entire source code is transparent Python. There are no covert analytics scripts, telemetry pings, or background tracking pixels.
- **Democratizing Creative Computing:** Anyone with a standard laptop can run a state-of-the-art 3-billion-parameter LLM at home.

---

## 9. Licensing & Attribution

- **GhostWriter Application:** Released under the [MIT License](LICENSE).
- **Ollama Engine:** Released by the Ollama team under the [MIT License](https://github.com/ollama/ollama/blob/main/LICENSE).
- **Qwen2.5 Models:** Developed by Alibaba Cloud, released under the [Apache 2.0 License](https://huggingface.co/Qwen/Qwen2.5-3B).
- **Llama 3.2 Models:** Developed by Meta, released under the [Llama 3.2 Community License](https://llama.meta.com/llama3/license/).
- **Gemma 2 Models:** Developed by Google, released under the [Gemma Terms of Use](https://ai.google.dev/gemma/terms).

---

## 10. Known Limitations & Roadmap

### Current Limitations:
- **Single-Turn Generation:** Generates standalone stories rather than branching interactive "choose-your-own-adventure" sagas.
- **Pure Text Output:** Does not generate companion horror audio or illustrations yet.

### Highest-Value Future Improvements:
1. 🎧 **Offline Text-to-Speech (TTS):** Integrate a local neural voice engine (e.g. Kokoro or Piper TTS) to narrate generated stories with eerie voice effects.
2. 📖 **Multi-Chapter Interactive Fiction Mode:** Allow readers to make choices at the end of each scene and generate branching sequels.
3. 🖼️ **Offline Cover Art Synthesis:** Connect a lightweight local image model (e.g., SDXL-Turbo) to generate vintage pulp horror cover art for saved tales.

---

## 11. Contributing

Contributions are welcome! Please open an issue or submit a pull request.
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/SpookyNewFeature`).
3. Commit your Changes (`git commit -m 'Add SpookyNewFeature'`).
4. Push to the Branch (`git push origin feature/SpookyNewFeature`).
5. Open a Pull Request.

