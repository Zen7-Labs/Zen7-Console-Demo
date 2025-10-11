from logging import getLogger, StreamHandler
from google.adk.agents import Agent
from google.adk.tools import ToolContext
import requests

from a2a_cli.cli import request_a2a
from mcp_cli.cli import init_session

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

def list_products() -> list[dict[str, any]]:
    logger.info(f"List products: {product_list}")
    return product_list

def select_product_by_name(product_name: str, tool_context: ToolContext) -> dict[str, any]:
    if not product_name:
        logger.error("Product name is unset")
        return {"status": "failed", "message": "product name is unset"}

    res = requests.put("http://localhost:8088/reset")
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
        res = requests.get("http://localhost:8088/status")
        if res.ok:
            data = res.json()
            has_finished = data["status"]
            if has_finished:
                tool_context.state["turn"] = None
        
        if not has_finished:
            logger.info(f"Current turn is: {turn}, Proceed payment for the product: {selected_product}")
            if turn == 1:
                input_message = f"I want to make a payment with order number: A030-{selected_product["id"]}, spend amount {selected_product["price"]}"
            logger.info(f"Requested Zen7 payment with message: {input_message}")
            
            sign_info = {
                "signature": "120394203840",
                "r": "12234",
                "s": "458034",
                "v": "342408"
            }

            # status, message = await request_a2a(message=input_message, user_id="user_02", sign_info=sign_info)
            # logger.info(f"Request A2A with status: {status}, message: {message}")
            # return {
            #     "status": "success",
            #     "message": message
            # }
        
            async with init_session("127.0.0.1", 8015) as session:
                res = await session.call_tool(
                    name='proceed_payment_and_settlement_detail_info',
                    arguments={
                        'message': input_message,
                        "user_id": "user_02",
                        "sign_info": sign_info
                    }
                )
                return {
                    "status": "success",
                    "message": res.content[0]
                }
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

root_agent = Agent(
    name="Shopping_agent",
    model="gemini-2.0-flash-lite",
    description="Help do shopping by selecting product and prepare for settlement and show orders",
    instruction="""
        Your key roles is to help user show the product list, select one product by name, 
        then take the selected product to invoke 'proceed_for_payment' tool to proceed the settlement,
        and show orders.

        **Core Capabilities**
        1. Use 'list_product' tool show product list for user that available to buy.
        2. User can select one product by name then store it into context for 'selected_product'
        3. Take this selected product to prepare for creating payment and settlement.
        4. Keep asking step by step via tool 'proceed_for_payment' with 'input_message' while the 'has_finished' parameter is FALSE.
        5. The 'input_message' for tool 'proceed_for_payment' MUST answer by user.
        6. Use 'proceed_for_payment' tool to proceed order related issue.""",
    tools=[list_products, select_product_by_name, proceed_for_payment]
)