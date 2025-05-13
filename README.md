# Web3 Trust Guard MCP Server

Introducing Web3 Trust Guard An MCP Server with 8 tools that help AI detect scams, verify donations, and protect users across blockchains.

A fully functional **Model Context Protocol (MCP)** server that allows AI agents to verify Web3 data in real-time — including token security, wallet risk, NFT authenticity, URL phishing detection, Solana transaction simulation, and on-chain donation validation.

Hosted at: [https://mcp.fundmesolana.com](https://mcp.fundmesolana.com)
Swagger Docs: [https://mcp.fundmesolana.com/swagger/](https://mcp.fundmesolana.com/swagger/)

Built for the [DeMCP Side Track](https://modelcontextprotocol.io/quickstart/server) challenge to empower AI x Crypto innovation.

---

## What This MCP Server Does

This server exposes 8 powerful tools that AI agents can use to analyze data on Ethereum, BNB, and Solana blockchains:

| Tool Name              | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| `check_token`          | Scan EVM token contracts for honeypot or scam risks              |
| `check_wallet`         | Detect if a wallet is malicious, blacklisted, or risky           |
| `check_nft`            | Analyze NFT contract + token ID for authenticity and risk        |
| `check_url`            | Check if a dApp or website is flagged as phishing                |
| `simulate_sol_tx`      | Simulate a Solana transaction to detect hidden dangers           |
| `check_sol_token`      | Inspect Solana SPL tokens for scam indicators                    |
| `verify_donation`      | Confirm if a tx hash represents a donation to a verified address |
| `list_verified_causes` | Return all trusted donation addresses (on-chain proof)           |

---

## MCP Tool Manifest Endpoint

AI agent platforms that support the **Model Context Protocol (MCP) standard** can dynamically discover and invoke these tools in real-time.

```
GET https://mcp.fundmesolana.com/api/mcp.json
```

This manifest allows any MCP-compatible AI system to call this server using structured, schema-defined functions.

---

## How to Use This MCP Server With an AI Agent

> Use any AI agent platform that supports **external tools built with the MCP standard** (e.g., LangChain, Auto-GPT, OpenAgents, etc).

1. **Load the Manifest**

```http
GET https://mcp.fundmesolana.com/api/mcp.json
```

2. **Prompt Example:**

> “Check if token `0x880bce9321c79cac1d290de6d31dde722c606165` on BNB (chain\_id 56) is a scam.”

3. **Agent Automatically Calls:**

```http
POST /check_token/
{
  "address": "0x880bce9321c79cac1d290de6d31dde722c606165",
  "chain_id": 56
}
```

4. **Receives Response:**

```json
{
  "success": true,
  "data": {
    "scam_risk": "0",
    "raw": {...}
  }
}
```

5. **Agent Interprets the Response:**

> “This token appears safe based on the analysis.”

---

## Supported Chains

* Ethereum Mainnet (chain\_id: `1`)
* BNB Smart Chain (chain\_id: `56`)
* Solana (native, no chain ID)

---

## Example Test Payloads

### 1. `check_token`

```json
{ "address": "0x880bce9321c79cac1d290de6d31dde722c606165", "chain_id": 56 }
```

* Token: `$FREE`

```json
{ "address": "0x64c37c3d6b5ff0fdea26eec0c8b6de487105291c", "chain_id": 56 }
```

* Token: `ITHEUM`

### 2. `check_nft`

```json
{
  "contract": "0xee24b9872022c7770CCC828d856224416CBa005f",
  "token_id": "1",
  "chain_id": 56
}
```

* NFT: Tribalpunk Hero

### 3. `check_wallet`

```json
{ "address": "0x7bd75b1b8f2cfce01bd97b3661c0a2b78a4c6ca0", "chain_id": 56 }
```

* Includes approval & threat indicators

### 4. `check_url`

```json
{ "url": "http://uniswap-swap.com" }
```

### 5. `simulate_sol_tx`

```json
{ "tx_base64": "<your_encoded_transaction>" }
```

### 6. `verify_donation`

```json
{
  "tx_hash": "<tx_hash>",
  "chain": "solana"
}
```

---

## Donation Verification Protocol

We support real-time verification of donations made on-chain to verified causes, across multiple platforms.

To standardize participation, **we have established a format external platforms must follow to integrate with this MCP server**.

### Accepted External Standard

Platforms wishing to integrate must expose a public endpoint like:

```
GET /api/verified-causes/
```

And return:

```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": [
    {
      "name": "Ali Surgery",
      "address": "Gh9Z...",
      "chain": "solana",
      "chain_id": null,
      "type": "emergency"
    },
    {
      "name": "Flood Aid",
      "address": "0x123...",
      "chain": "evm",
      "chain_id": 1,
      "type": "emergency"
    }
  ]
}
```

### Current Accepted Partner

* FundMeSolana:
  [https://fundmesolana.com/api/emergency/verified\_causes](https://fundmesolana.com/api/emergency/verified_causes)

Our server automatically fetches and indexes donation addresses from approved sources like the one above.

---

## External APIs Used

* [GoPlus Labs API](https://docs.gopluslabs.io/reference/api-overview)
* [Covalent API](https://www.covalenthq.com/docs/api/)
* [Solana JSON-RPC](https://docs.solana.com/api/http)

---

## How to Run Locally

```bash
git clone https://github.com/yourname/web3-mcp-server.git
cd web3-mcp-server
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
```

Create `.env` file:

```bash
GOPLUS_BASE=https://api.gopluslabs.io
COVALENT_KEY=your_covalent_api_key
VERIFIED_CAUSE_SOURCES=https://fundmesolana.com/api/emergency/verified_causes
```

Then run:

```bash
python manage.py migrate
python manage.py runserver
```

Access Swagger API Docs:

```
http://127.0.0.1:8000/swagger/
```

---

## References & Protocol Sources

### MCP Protocol & Examples

* [MCP Quickstart Guide](https://modelcontextprotocol.io/quickstart/server)
* [MCP Client Tool Usage Tutorial](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms)
* [DeMCP GitHub Example](https://github.com/demcp/demcp-defillama-mcp)

### API Providers

* [GoPlus Labs API](https://docs.gopluslabs.io/reference/api-overview)
* [Covalent API](https://www.covalenthq.com/docs/api/)
* [Solana JSON-RPC](https://docs.solana.com/api/http)
* [FundMeSolana Verified Causes JSON](https://mcp.fundmesolana.com/api/emergency/verified_causes)
---

## Built With ❤️ by Bolaji M.L

Building public-good AI agents that trust on-chain data.

Follow: [@DeMCP\_AI](https://twitter.com/DeMCP_AI),
[@Fundmesolaa](https://twitter.com/Fundmesolana)

Website: [https://demcp.ai](https://demcp.ai),
[https://fundmesolana.com](https://fundmesolana)

License: MIT
