# AegisChain-Hybrid-Web3-AI-Pharmaceutical-Supply-Chain
## Main Challenge

Global supply chains suffer from a lack of verifiable transparency, fragmented data silos, and an inability to detect environmental or logistical tampering in real time. Traditional tracking mechanisms rely on centralized databases that are vulnerable to retroactive alterations, making it difficult to verify the integrity of sensitive cargo such as pharmaceuticals or high-value components during transit.

## Track Alignment

AegisChain aligns with Web3 and Artificial Intelligence integration tracks by combining decentralized ledger immutability with automated machine learning analytics. It bridges off-chain sensor telemetry and on-chain verification to establish an automated, tamper-proof audit framework.

## Project Description

### Problem

Supply chain networks lack cryptographic proof of custody and condition monitoring. When cold-chain failures, unauthorized route deviations, or handling discrepancies occur, stakeholders often discover them only after the product has been delivered or compromised, leading to significant financial losses and compliance failures.

### Solution

AegisChain provides a hybrid architecture that logs immutable batch registrations and transit checkpoints on the Ethereum blockchain via smart contracts, while a backend intelligence engine continuously evaluates telemetry data against historical baselines to flag logistical anomalies.

### Target Users

* Supply chain quality assurance and compliance managers
* Pharmaceutical and cold-chain logistics operators
* Regulatory auditors requiring verifiable historical ledgers
* Enterprise stakeholders tracking high-value inventory

### Impact

The platform eliminates reliance on mutable central databases, provides automated risk assessments for every transit milestone, and ensures absolute transparency for end consumers and auditors through a permanent cryptographic audit trail.

---

## Key Results

* Deployed and verified core Solidity smart contracts on the Ethereum Sepolia testnet.
* Implemented an automated backend analysis pipeline capable of evaluating temperature and environmental anomalies with confidence scoring.
* Developed a responsive, low-latency frontend interface providing real-time timeline rendering and verification audits without page reloads.

---

## Tech Stack

* **Smart Contract Layer:** Solidity, Ethereum Sepolia Testnet, Infura RPC
* **Blockchain Integration:** Web3.py
* **Backend Services:** Python, FastAPI, Uvicorn
* **Artificial Intelligence Engine:** OpenAI API / LLM-based anomaly detection adapters
* **Frontend Interface:** HTML5, CSS3 (Glassmorphism design system), Vanilla JavaScript (ES Modules)

---

## Project Structure

```text
aegischain/
│
├── backend/
│   ├── main.py              # FastAPI application entry point and routing
│   ├── web3_client.py       # Blockchain interaction and smart contract wrappers
│   ├── ai_engine.py         # Telemetry anomaly detection and audit logic
│   └── requirements.txt     # Python dependency manifest
│
├── contracts/
│   └── SupplyChain.sol      # Immutable ledger and transit tracking smart contract
│
└── frontend/
    ├── index.html           # Single-page application dashboard
    ├── styles.css           # Layout and glassmorphism styling
    └── app.js               # Asynchronous API integration and UI routing

```

---

## Prerequisites

Before running the application locally, ensure you have the following installed and configured:

* Python 3.9 or higher
* Node.js (optional, for static file serving via http-server) or Python HTTP module
* An active Ethereum Sepolia RPC provider URL (via Infura or Alchemy)
* A funded Sepolia testnet wallet private key for transaction signing
* An OpenAI or compatible LLM API key

---

## Local Setup Instructions

### 1. Configure Environment Variables

Navigate to the backend directory and create a configuration file named `.env` containing your private keys and endpoints:

```env
WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
CONTRACT_ADDRESS=0xYourDeployedSmartContractAddress
PRIVATE_KEY=0xYourWalletPrivateKey
AI_API_KEY=your_api_key_here

```

### 2. Run the FastAPI Backend

Open a terminal window, navigate to the backend folder, establish a virtual environment, and start the development server:

```bash
cd backend
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS / Linux)
# source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000

```

### 3. Launch the Frontend Interface

Open a second terminal window, navigate to the frontend directory, and spin up a lightweight local web server to prevent CORS issues:

```bash
cd frontend
python -m http.server 3000

```
