# Blockchain Intelligence Sharing Module

A decentralized, tamper-proof threat intelligence sharing system built using **Ethereum**, **Hardhat**, and **FastAPI**.
It enables secure, transparent, and immutable cross-organization intelligence sharing as part of the **AI-Powered Threat Detection System**.

---

## 🎯 Overview

This module ensures that threat data shared between global organizations remains **verifiable**, **trustless**, and **immutable**.
Using blockchain guarantees an auditable record of every submission, preventing data tampering or unauthorized modification.

### ✨ Key Features

* **Immutable Ledger** – Data permanently recorded on Ethereum blockchain
* **Transparent Audit Trail** – Includes timestamp and submitter wallet address
* **Decentralized System** – No single controlling authority
* **REST API Ready** – Seamless integration via FastAPI backend
* **Local Dev Network** – Built-in Hardhat blockchain for instant testing

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend/API   │
└────────┬────────┘
         │  REST
         ▼
┌────────────────────────────┐
│ FastAPI Backend (Port 8003)│
│  /share   - Add threat     │
│  /threat/{id} - Retrieve   │
│  /stats   - Statistics     │
└────────┬──────────────────┘
         │ Web3.py
         ▼
┌────────────────────────────┐
│ Hardhat Local Blockchain   │
│ http://127.0.0.1:8545      │
│ 20 prefunded test accounts │
└────────┬──────────────────┘
         ▼
┌────────────────────────────┐
│ ThreatIntelligence.sol     │
│  logThreat()               │
│  getThreat()               │
│  getThreatCount()          │
└────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer           | Technology                             |
| --------------- | -------------------------------------- |
| **Blockchain**  | Solidity `^0.8.20`, Hardhat, Ethers.js |
| **Backend**     | FastAPI, Python 3.9+, Web3.py          |
| **Server**      | Uvicorn                                |
| **Data Models** | Pydantic                               |

---

## 🧩 Project Structure

```
intelligence-sharing/
├── contracts/
│   └── ThreatIntelligence.sol
├── scripts/
│   ├── deploy.js
│   └── start.sh
├── app/
│   ├── main.py
│   ├── blockchain/web3_client.py
│   └── schemas/intelligence.py
├── hardhat.config.js
├── requirements.txt
├── package.json
└── README.md
```

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
# Node.js
npm install

# Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Start Hardhat Local Network

```bash
npx hardhat node
```

Keep this running.

### 3️⃣ Deploy Smart Contract

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

**Example Output**

```
Deploying ThreatIntelligence contract...
Deployed to: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
```

### 4️⃣ Start FastAPI Backend

```bash
uvicorn app.main:app --port 8003 --reload
```

---

## 📡 API Endpoints

| Method   | Endpoint       | Description            |
| -------- | -------------- | ---------------------- |
| **POST** | `/share`       | Store new threat intel |
| **GET**  | `/threat/{id}` | Retrieve threat by ID  |
| **GET**  | `/stats`       | Blockchain stats       |
| **GET**  | `/health`      | Health check           |

### Example – POST `/share`

```bash
curl -X POST "http://localhost:8003/share" \
-H "Content-Type: application/json" \
-d '{"text": "AI phishing campaign", "entities": "{\"organizations\": [\"FakeBank\"]}"}'
```

**Response**

```json
{
  "transaction_hash": "0xabc123...",
  "threat_id": 0,
  "status": "Successfully logged to blockchain"
}
```

---

## 🔐 Smart Contract Summary

**File:** `contracts/ThreatIntelligence.sol`

```solidity
struct Threat {
    string text;
    string entities;
    uint256 timestamp;
    address submitter;
}

event ThreatLogged(
    uint256 indexed threatId,
    string text,
    address indexed submitter,
    uint256 timestamp
);
```

### Core Functions

| Function                                    | Description                |
| ------------------------------------------- | -------------------------- |
| `logThreat(string _text, string _entities)` | Store new threat data      |
| `getThreat(uint256 _id)`                    | Retrieve a specific threat |
| `getThreatCount()`                          | Get total count            |

---

## ⚙️ Configuration

### `hardhat.config.js`

```js
module.exports = {
  solidity: "0.8.20",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 1337
    }
  }
};
```

### `.env` (example)

```
HARDHAT_NETWORK_URL=http://127.0.0.1:8545
PRIVATE_KEY=<test-private-key>
CONTRACT_ADDRESS=<deployed-contract-address>
API_PORT=8003
```

---

## 🔗 Integration Example

**Python**

```python
import requests, json

def share_to_blockchain(text, entities):
    r = requests.post("http://localhost:8003/share", json={
        "text": text,
        "entities": json.dumps(entities)
    })
    return r.json()
```

**JavaScript**

```js
import axios from 'axios';

export async function shareThreat(text, entities) {
  const res = await axios.post('http://localhost:8003/share', {
    text,
    entities: JSON.stringify(entities)
  });
  return res.data;
}
```

---

## 🧪 Testing Commands

```bash
# Health
curl http://localhost:8003/health

# Add a threat
curl -X POST "http://localhost:8003/share" \
-H "Content-Type: application/json" \
-d '{"text": "Test threat", "entities": "{}"}'

# Retrieve by ID
curl http://localhost:8003/threat/0
```

---
---
---

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/Lock.js
```
