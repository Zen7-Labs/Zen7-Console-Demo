from logging import getLogger, StreamHandler

from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.sse import sse_client

import asyncio

logger = getLogger(__name__)
logger.addHandler(StreamHandler())

@asynccontextmanager
async def init_session(host: str, port: int):
    """Initializes and manages an MCP ClientSession based on the specified transport.

    This asynchronous context manager establishes a connection to an MCP server
    using either Server-Sent Events (SSE) transport.
    It handles the setup and teardown of the connection and yields an active
    `ClientSession` object ready for communication.

    Args:
        host: The hostname or IP address of the MCP server (used for SSE).
        port: The port number of the MCP server (used for SSE).
    Yields:
        ClientSession: An initialized and ready-to-use MCP client session.

    Raises:
        ValueError: If an unsupported transport type is provided (implicitly,
                    as it won't match 'sse' or 'stdio').
        Exception: Other potential exceptions during client initialization or
                   session setup.
    """
    url = f'http://{host}:{port}/sse'
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(
            read_stream=read_stream, write_stream=write_stream
        ) as session:
            logger.debug('SSE ClientSession created, initializing...')
            await session.initialize()
            logger.info('SSE ClientSession initialized successfully.')
            yield session

async def main_async():
    async with init_session("127.0.0.1", 8015) as session:
        while True:
            input_message = input("You: ")
            res = await session.call_tool(
                name="proceed_payment_and_settlement_and_order_details",
                arguments={
                    "message": input_message,
                    "user_id": "user_02",
                    "sign_info": {
                        "signature": "120394203840",
                        "r": "12234",
                        "s": "458034",
                        "v": "342408"
                    },
                    "owner_wallet_address": ""
                }
            )
            logger.info(f"result: {res.content}")
            
if __name__ == "__main__":
    asyncio.run(main_async())