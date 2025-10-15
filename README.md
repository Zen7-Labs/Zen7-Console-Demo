# Shopping Agent Console Demo Guide

## Project Overview

Shopping Agent is an intelligent shopping assistant system built on Google ADK (Agent Development Kit). This project demonstrates how to integrate multiple services together, including A2A (Agent-to-Agent) communication, MCP (Model Context Protocol) client, and FastAPI services, to create a complete shopping and payment workflow.

## System Architecture

The project contains the following main components:

1. **Shopping Agent** (`shopping_agent/agent.py`) - The main intelligent shopping assistant
2. **A2A CLI** (`a2a_cli/cli.py`) - Agent-to-Agent communication client
3. **MCP CLI** (`mcp_cli/cli.py`) - Model Context Protocol client
4. **Shopping Service** (`shopping_service/server.py`) - Backend service API

## Prerequisites

- Python 3.13+
- UV package manager
- Running A2A server (localhost:10000)
- Running MCP server (localhost:8015)

## Quick Start

### 1. Environment Setup

This section guides you through initializing your development environment, including project cloning, virtual environment creation and activation, and dependency installation.

#### 1.1 Clone the Repository

```bash
git clone https://github.com/Zen7-Labs/Zen7-Console-Demo.git
```

#### 1.2 Enter the Project Directory

```bash
cd Zen7-Console-Demo
```

#### 1.3 Create and Activate a Virtual Environment (Recommended)

1. Create the virtual environment:

        ```bash
        uv venv
        ```

2. Activate the virtual environment:

        - **Linux/macOS:**
            ```bash
            source .venv/bin/activate
            ```
        - **Windows (CMD):**
            ```bash
            .venv\Scripts\activate
            ```
        - **Windows (PowerShell):**
            ```powershell
            .venv\Scripts\Activate.ps1
            ```

> After activation, your command prompt should show (venv) at the beginning.

#### 1.4 Install Dependencies

```bash
(venv) $ uv sync
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory with the following content (fill in your actual keys and service addresses):

```dotenv
# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Choose target server to connect with specified A2A or MCP client.
TARGET_SERVER=a2a

# A2A Service Configuration
A2A_SERVER_URL=http://localhost:10000

# MCP Service Configuration
MCP_HOST=127.0.0.1
MCP_PORT=8015

# Provide shopping_service URL to check or reset status to assist proceeding payment and settlement decide whether it has finished.
CHECK_STATUS_URL=http://localhost:8088/status
RESET_STATUS_URL=http://localhost:8088/reset
```

> For blockchain or payment integration, refer to the relevant documentation to add more environment variables as needed.

### 3. Start Backend Service

#### 3.1 Start the Shopping Service (Backend API)
- Provide service to check or reset status to assist proceeding payment and settlement decide whether it has finished.

```bash
(venv) $ uv run python shopping_service/server.py
```

#### 3.2 Start the Main Application (Google ADK Web Interface)

```bash
(venv) $ uv run adk web
```

Or run the script directly:

- **Linux/macOS:**
    ```bash
    ./run.sh
    ```
- **Windows:**
    ```powershell
    uv run adk web
    ```

> For custom ports, protocols, and other parameters, refer to the --help/-Help options in run.sh or run.ps1.

### 4. Start Main Application

---

### 4. Run Components Independently (for Development & Debugging)

You can start each component separately for development and debugging:

```bash
# Start A2A CLI
(venv) $ uv run python a2a_cli/cli.py

# Start MCP CLI
(venv) $ uv run python mcp_cli/cli.py

# Start Shopping Service
(venv) $ uv run python shopping_service/server.py
```

#### Example A2A CLI Conversation

```
You: I want to make a payment with order number: 1568715435, spend amount: 99.0, budget: 129.0, expiration date is: 2025-10-14, currency is: USDC

Agent (TaskState.completed): OK. I have processed your payment details. The settlement process has begun, and the payee agent will be notified upon completion.
```

## Usage Guide

---

## 5. 使用指南

## 5. Usage Guide

### 5.1 Shopping Workflow

1. **Browse Products**: Ask the assistant to display all available products
2. **Select Product**: Choose a product to purchase by name
3. **Payment Process**: The system will guide you through payment and settlement
4. **Order Tracking**: Check order status and payment details

### 5.2 Example Product List

**Beverages (Merchant A):**
- Beverage: ¥499
- Red wine: ¥99
- Whisky: ¥199
- Brandy: ¥399
- Moutai: ¥1499

**Clothing (Merchant B):**
- Jeans: ¥139
- Coat: ¥299
- Shirt: ¥199
- Suit: ¥599

### 5.3 Example Conversation

```
User: Show all products
Assistant: [Displays product list]

User: I want to buy a coat
Assistant: [Selects coat and prepares payment process]

User: [Follows prompts to complete payment information]
Assistant: [Processes payment and displays order status]
```

## Component Details

---

## 6. 主要组件说明

## 6. Component Details

### 6.1 Shopping Agent
The core intelligent assistant, with the following capabilities:
- `list_products()`: Display all products
- `select_product_by_name()`: Select products by name
- `proceed_for_payment()`: Handle payment and settlement

### 6.2 A2A CLI
Agent-to-Agent communication client, supports:
- Asynchronous message sending and receiving
- Context and task state management
- Multi-turn conversation

### 6.3 MCP CLI
Model Context Protocol client, supports:
- SSE connections
- Tool invocation interface
- Session management

### 6.4 Shopping Service
FastAPI backend service, provides:
- `/notify`: Receive payment notifications
- `/status`: Query order status
- `/reset`: Reset order status

## Development and Debugging

---

## 7. 开发与调试

## 7. Development & Debugging

### 7.1 Logging Configuration
All components are configured with detailed logging output to help you track the system status:

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

## Troubleshooting

---

## 8. 常见问题与排查

## 8. Troubleshooting

**Q: A2A service connection failed?**
A: Make sure the A2A service is running on local port 10000 and check network connectivity.

**Q: MCP service connection failed?**
A: Make sure the MCP service is running on local port 8015 and the SSE endpoint is accessible.

**Q: Google ADK initialization failed?**
A: Check if the `GOOGLE_API_KEY` environment variable is set correctly.

**Q: Product selection not responding?**
A: Make sure the product name is entered correctly. The system supports fuzzy (case-insensitive) matching.

## Extension Development

---

## 9. 扩展开发

## 9. Extension Development

### 9.1 Add New Products
Edit the `product_list` in `shopping_agent/agent.py`, for example:

```python
product_list.append({
    "id": 10,
    "name": "New Product",
    "price": 299,
    "payee": "Merchant C"
})
```

### 9.2 Customize Payment Flow
To support different payment methods or business logic, modify the `proceed_for_payment()` method.

### 9.3 Integrate External Services
Extend tool functions to integrate third-party APIs or services.

## Technology Stack

---

## 10. 技术栈

## 10. Technology Stack

- Python 3.13+
- Google ADK
- FastAPI
- A2A SDK
- MCP
- uv
- HTTPX

## Contributing

---

## 11. 贡献指南

## 11. Contributing

1. Fork this project
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## License

---

## 12. License

## 12. License

Please refer to the LICENSE file in the project root directory.

---

For more help, please refer to the project documentation or submit an Issue.