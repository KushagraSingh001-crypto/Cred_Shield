# 🛡️ CredShield – AI-Powered LLM Threat Intelligence Platform

**CredShield** is a multi-layered cybersecurity framework designed to **detect, analyze, and mitigate the misuse of Large Language Models (LLMs)** in malicious information operations such as phishing, disinformation, and propaganda.  

It combines **AI-driven text forensics**, **stylometric analysis**, **graph-based disinformation mapping**, and **blockchain-backed intelligence sharing**, aligning with the **Smart India Hackathon (SIH) Problem Statement *“Mitigating National Security Risks Posed by Large Language Models (LLMs) in AI-Driven Malign Information Operations.”*

---

## 🌍 Problem Statement

Malicious actors leverage advanced LLMs (like GPT, Claude, Gemini, and Perplexity) to:
- Generate human-like phishing content
- Spread coordinated misinformation
- Fabricate extremist propaganda
- Influence public sentiment at scale

**CredShield** detects, attributes, and prevents such operations by analyzing text patterns, tracking propagation clusters, and providing immutable blockchain audit trails.
---

## 🧩 Core Modules

| Module                                           | Technology                          | Description                                                                                                                            |
| ------------------------------------------------ | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Text Analysis Engine**                      | Python, FastAPI, Transformers       | Detects AI-generated content, extracts keywords, and evaluates toxicity using models like `chatgpt-detector-roberta` and `toxic-bert`. |
| **2. Visualization Dashboard**                   | HTML, Plotly.js, TailwindCSS        | Displays AI vs. human probability, toxicity, keywords, and core sentence insights interactively.                                       |
| **3. Graph Intelligence**                        | PyTorch Geometric (planned)         | Maps and identifies disinformation clusters and propagation paths.                                                                     |
| **4. Blockchain Intelligence Sharing**           | Solidity, Hardhat, Web3.py, FastAPI | Logs threats immutably and enables cross-agency data sharing through smart contracts.                                                  |
| **5. Backend Integration Layer**                 | Node.js, Express, MongoDB           | Acts as a secure data hub between components.                                                                                          |
| **6. Frontend Dashboard (Full Stack Extension)** | React.js                            | Real-time risk analytics, alerts, and reporting for SOC teams.                                                                         |

---

## 🏗️ Project Structure

```
credshield/
├── text-analysis/
│   ├── script.py              # NLP + ML model inference
│   ├── input.txt              # Sample input text
│   ├── output.json            # Analysis results
│   ├── index.html             # Dashboard visualization
│   └── README.md              # Local module doc
│
├── blockchain-sharing/
│   ├── contracts/
│   │   └── ThreatIntelligence.sol  # Solidity smart contract
│   ├── scripts/deploy.js           # Hardhat deployment script
│   ├── app/main.py                 # FastAPI blockchain backend
│   ├── hardhat.config.js
│   ├── requirements.txt
│   └── package.json
│
└── README.md                      # (This file)
```

---

## 🚀 Setup and Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/credshield.git
cd credshield
```

### 2️⃣ Backend (Python – Text Analysis)

```bash
cd text-analysis
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python script.py
```

### 3️⃣ Blockchain Intelligence Sharing

```bash
cd blockchain-sharing
npm install
npx hardhat node
npx hardhat run scripts/deploy.js --network localhost

# In a new terminal
uvicorn app.main:app --port 8003 --reload
```

### 4️⃣ Dashboard

```bash
python -m http.server 8000
# Access at http://localhost:8000
```

---

## 📡 API Endpoints Testing (Blockchain)

```bash
curl -X POST "http://localhost:8003/share" \
-H "Content-Type: application/json" \
-d '{"text": "AI phishing campaign", "entities": "{\"organizations\": [\"FakeBank\"]}"}'
```

---

## 🧠 Model Details

| Task                   | Model                          | Description                                     |
| ---------------------- | ------------------------------ | ----------------------------------------------- |
| **AI Detection**       | `roberta-base-openai-detector` | Determines if text was AI-generated             |
| **Toxicity Detection** | `unitary/toxic-bert`           | Flags harmful or manipulative content           |
| **Entity Extraction**  | `spacy/en_core_web_sm`         | Identifies organizations, people, and locations |
| **Keyword Extraction** | SpaCy noun-chunk frequency     | Extracts semantic keywords from text            |

---

## 🧰 Dependencies

| Layer          | Dependencies                                                       |
| -------------- | ------------------------------------------------------------------ |
| **Python**     | `spacy`, `transformers`, `torch`, `pydantic`, `fastapi`, `uvicorn` |
| **Node.js**    | `hardhat`, `ethers`, `dotenv`                                      |
| **Frontend**   | `plotly.js`, `tailwindcss`                                         |
| **Blockchain** | `solidity ^0.8.20`, Hardhat local network                          |

---

## 🧱 Future Improvements

* Integrate **GNN-based disinformation mapping**
* Add **federated learning** for cross-agency collaboration
* Implement **Explainable AI (XAI)** module
* Expand to **multilingual LLM detection**
* Build **real-time API integration** for SOC dashboards

---

## 📜 License

This project is released under the **MIT License**.

---

> ⚔️ *“Protecting truth in the age of intelligent deception.”*
