# Shopping Agent Quick Start Guide

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

```bash
# Clone or download the project locally
cd examples

# Install dependencies using UV
uv sync
```

### 2. Configure Environment Variables

Create a `.env` file and add the necessary environment variables:

```env
# Google API key (for Gemini model)
GOOGLE_API_KEY=your_google_api_key_here

# A2A server configuration
A2A_SERVER_URL=http://localhost:10000

# MCP server configuration
MCP_HOST=127.0.0.1
MCP_PORT=8015
```

### 3. Start Backend Service

First, start the shopping service:

```bash
# Start FastAPI shopping service (port 8088)
uv run python shopping_service/server.py
```

### 4. Start Main Application

```bash
# Start Google ADK Web interface
uv run adk web
```

Or use the provided script:

```bash
# Linux/Mac
./run.sh

# Windows
uv run adk web
```

## Usage Guide

### Shopping Workflow

1. **Browse Products**: Ask the shopping assistant to display the available product list
2. **Select Product**: Choose a product to purchase by name
3. **Payment Process**: The system will automatically guide you through the payment and settlement process
4. **Order Tracking**: View order status and payment details

### Available Products

The system comes with the following pre-configured product categories:

**Beverages** (Merchant A):
- Beverage: ¥499
- Red wine: ¥99
- Whisky: ¥199
- Brandy: ¥399
- Moutai: ¥1499

**Clothing** (Merchant B):
- Jeans: ¥139
- Coat: ¥299
- Shirt: ¥199
- Suit: ¥599

### Example Conversation

```
User: "Please show all products"
Assistant: [Displays product list]

User: "I want to buy a coat"
Assistant: [Selects Coat product and prepares payment process]

User: [Follows prompts to complete payment information input]
Assistant: [Processes payment and displays order status]
```

## Component Details

### Shopping Agent

The core intelligent assistant with the following capabilities:
- `list_products()`: Display all available products
- `select_product_by_name()`: Select products by name
- `proceed_for_payment()`: Handle payment and settlement processes

### A2A CLI

Agent-to-Agent communication client that supports:
- Asynchronous message sending and receiving
- Context and task state management
- Multi-turn conversation support

### MCP CLI

Model Context Protocol client that provides:
- Server-Sent Events (SSE) connections
- Tool invocation interface
- Session management

### Shopping Service

FastAPI backend service that provides:
- `/notify` - Receive payment notifications
- `/status` - Query order status
- `/reset` - Reset order status

## Development and Debugging

### Running Components Independently

```bash
# Run A2A CLI
uv run python a2a_cli/cli.py

# Run MCP CLI
uv run python mcp_cli/cli.py

# Run shopping service
uv run python shopping_service/server.py
```

### Logging Configuration

All components are configured with detailed logging output to help you understand the system's running status:

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

## Troubleshooting

### Q: A2A server connection failed
**A**: Ensure the A2A server is running on `localhost:10000` and check network connectivity.

### Q: MCP server connection failed
**A**: Ensure the MCP server is running on `localhost:8015` and verify that the SSE endpoint is accessible.

### Q: Google ADK initialization failed
**A**: Check if the `GOOGLE_API_KEY` environment variable is correctly set.

### Q: Product selection not responding
**A**: Ensure the product name is entered correctly. The system uses fuzzy matching (case-insensitive).

## Extension Development

### Adding New Products

Edit the `product_list` in `shopping_agent/agent.py`:

```python
product_list.append({
    "id": 10, 
    "name": "New Product", 
    "price": 299, 
    "payee": "Merchant C"
})
```

### Customizing Payment Flow

Modify the `proceed_for_payment()` function to support different payment methods or business logic.

### Integrating Other Services

You can easily integrate other external services or APIs by adding new tool functions.

## Technology Stack

- **Python 3.13+**: Primary programming language
- **Google ADK**: Agent development framework
- **FastAPI**: Web service framework
- **A2A SDK**: Agent-to-Agent communication
- **MCP**: Model Context Protocol
- **UV**: Modern Python package manager
- **HTTPX**: Asynchronous HTTP client

## Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## License

Please refer to the LICENSE file in the project root directory for license information.

---

For more help, please refer to the project documentation or submit an Issue.