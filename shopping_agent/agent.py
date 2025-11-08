from logging import getLogger, StreamHandler
from google.adk.agents import Agent
from google.adk.tools import ToolContext
import requests

from dotenv import load_dotenv
import os
import json

load_dotenv()

target_server = os.getenv("TARGET_SERVER")

if target_server == "a2a":
    from a2a_cli.cli import request_a2a
elif target_server == "mcp":
    from mcp_cli.cli import init_session

from datetime import timedelta, datetime

logger = getLogger(__name__)
logger.addHandler(StreamHandler())

product_list = [
    {"id": 1, "name": "Beverage", "price": 499, "payee": "Merchant A"},
    {"id": 2, "name": "Red wine", "price": 99, "payee": "Merchant A"},
    {"id": 3, "name": "Whisky", "price": 199, "payee": "Merchant A"},
    {"id": 4, "name": "Brandy", "price": 399, "payee": "Merchant A"},
    {"id": 5, "name": "Moutai", "price": 1499, "payee": "Merchant A"},
    {"id": 6, "name": "Jeans", "price": 139, "payee": "Merchant B"},
    {"id": 7, "name": "Coat", "price": 299, "payee": "Merchant B"},
    {"id": 8, "name": "Shirt", "price": 199, "payee": "Merchant B"},
    {"id": 9, "name": "Suit", "price": 599, "payee": "Merchant B"}
]

user_id = "user_02"
# Leave sign_info empty means will be signed by payment server.
sign_info = {}

payment_info = {
    "chain": os.getenv("CHAIN"),
    "currency": os.getenv("CURRENCY")
}

# Should uses the same timezone setting as the payment server
timezone = os.getenv("TIMEZONE")

def list_products() -> str:
    logger.info(f"List products: {product_list}")
    return json.dumps(product_list)

def select_product_by_name(product_name: str, tool_context: ToolContext) -> dict[str, any]:
    if not product_name:
        logger.error("Product name is unset")
        return {"status": "failed", "message": "product name is unset"}

    res = requests.put(os.getenv("RESET_STATUS_URL"))
    if res.ok:
        data = res.json()
        logger.info(f"Successfully reset the has_finished to: {data["status"]}")

    for product in product_list:
        if product_name.lower() in product["name"].lower():
            tool_context.state["selected_product"] = product
            logger.info(f"Set product: {product} into context.")
            return product
    logger.error(f"None of product match for name: {product_name}")
    return {"status": "failed", "message": f"None of product match for name: {product_name}"}

async def proceed_by_target_server(input_message: str, user_id: str, sign_info: dict[str, any] = {}) -> dict[str, any]:
    if target_server == "a2a":
            status, message = await request_a2a(message=input_message, user_id=user_id, 
                        sign_info=sign_info, payment_info=payment_info, timezone=timezone)
            logger.info(f"Request A2A with status: {status}, message: {message}")
            return {
                "status": "success",
                "message": message
            }
    elif target_server == "mcp":
        mcp_server_host = os.getenv("MCP_SERVER_HOST")
        mcp_server_port = os.getenv("MCP_SERVER_PORT")
        async with init_session(mcp_server_host, int(mcp_server_port)) as session:
            res = await session.call_tool(
                name='proceed_payment_or_settlement_or_order_or_allowance_details',
                arguments={
                    'message': input_message,
                    "user_id": user_id,
                    "sign_info": sign_info,
                    "payment_info": payment_info,
                    "timezone": timezone
                }
            )
            return {
                "status": "success",
                "message": res.content[0]
            }

async def proceed_for_payment(has_finished: bool, input_message: str, tool_context: ToolContext) -> dict[str, any]:
    selected_product = tool_context.state.get("selected_product")
    if not selected_product:
        logger.error("None of selected product found in context")
        return {
            "status": "failed",
            "message": "None of selected product found in context"
        }
    
    turn = tool_context.state.get("turn", None)
    if not turn:
        turn = 1
    else:
        turn += 1
    tool_context.state["turn"] = turn
    try:
        res = requests.get(os.getenv("CHECK_STATUS_URL"))
        if res.ok:
            data = res.json()
            has_finished = data["status"]
            if has_finished:
                tool_context.state["turn"] = None
        
        if not has_finished:
            logger.info(f"Current turn is: {turn}, Proceed payment for the product: {selected_product}")
            if turn == 1:
                expiration_date = datetime.now() + timedelta(days=1)
                expiration_date_str = expiration_date.strftime("%Y-%m-%d")
                currency = "USDC"
                chain = "sepolia"
                input_message = (f"I want to make a payment with order number: A030-{selected_product["id"]},"
                f"spend amount {selected_product["price"] * 100}, budget amount is {selected_product["price"] * 100}, "
                f"expiration date is {expiration_date_str}, currency is {currency}, chain is {chain}")
            logger.info(f"Requested Zen7 payment with message: {input_message}")
            return await proceed_by_target_server(input_message, user_id, sign_info)
    except Exception as e:
        logger.error(f"Failed to get message from A2A MCP: {e}")
        return {
            "status": "failed",
            "message": f"Failed to get message from A2A MCP: {e}"
        }
    return {
        "status": "success",
        "message": f"Proceed payment for the product: {selected_product}"
    }

async def proceed_order_or_allowance_detail(input_message: str) -> dict[str, any]:
    return await proceed_by_target_server(input_message=input_message, user_id=user_id, sign_info=sign_info)


root_agent = Agent(
    name="Shopping_agent",
    model="gemini-2.0-flash-lite",
    description="Help do shopping by selecting product and prepare for settlement or show orders, get allowance separately",
    instruction="""
        Your key roles is to help user show the product list, select one product by name, 
        then take the selected product to invoke 'proceed_for_payment' tool to proceed the settlement;
        invoke 'proceed_order_or_allowance_detail' to get order by order number or get allowance by the owner wallet address.

        **Core Capabilities**
        1. Use 'list_product' tool MUST RETURN the product list in detail to user help select product to buy.
        2. User can select one product by name then store it into context for 'selected_product'
        3. Take this selected product to prepare for creating payment and settlement.
        4. Keep asking step by step via tool 'proceed_for_payment' with 'input_message' while the 'has_finished' parameter is FALSE.
        5. The 'input_message' for tool 'proceed_for_payment' MUST answer by user.
        6. Use 'proceed_order_or_allowance_detail' to get order by the provided order number.
        7. Use 'proceed_order_or_allowance_detail' to get allowance by the owner wallet address.""",
    tools=[list_products, select_product_by_name, proceed_for_payment, proceed_order_or_allowance_detail]
)