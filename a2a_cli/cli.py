import logging
from logging import getLogger, StreamHandler

from uuid import uuid4

from a2a.types import (
    TaskState,
    SendMessageRequest,
    MessageSendParams
)
from a2a.client import A2ACardResolver, A2AClient

import httpx
import asyncio

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(level=logging.INFO)

A2A_SERVER_URL = "http://localhost:10000"

def generate_id() -> str:
    return uuid4().hex

context_id: str | None = None
task_id: str | None = None

async def request_a2a(message: str, user_id: str, sign_info: dict[str, any] = {}) -> tuple[TaskState, str]:
    async with httpx.AsyncClient(timeout=100) as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=A2A_SERVER_URL,
        )
        agent_card = await resolver.get_agent_card()
        logger.info(f"Fetched agent card: {agent_card}")

        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card
        )
        logger.info(f"A2AClient has initialized.")
        send_message_payload: dict[str, any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "message_id": generate_id(),
                "metadata": {
                    "user_id": user_id,
                    "sign_info": sign_info
                }
            }
        }
        global context_id, task_id
        if context_id:
            send_message_payload["message"]["context_id"] = context_id
            logger.info(f"Set context_id: {context_id} to the send_message_payload")
        if task_id:
            send_message_payload["message"]["task_id"] = task_id
        
        request = SendMessageRequest(
            id=generate_id(), 
            params=MessageSendParams(**send_message_payload)
        )

        try:
            response = await client.send_message(request)
            logger.info(f"Response from A2A: {response}")
            root = response.root
            result = root.result
            if result:
                state = result.status.state
                logger.info(f"**result.status.state: {state}")
                if isinstance(state, TaskState) and state == TaskState.completed:
                    # Successful completion
                    for artifact in result.artifacts:
                        for part in artifact.parts:
                            section = part.root
                            if section.kind == "text":
                                logger.info(f"**task state: {state}, data: {section.text}")
                                return (state, section.text)
                            
                elif isinstance(state, TaskState) and (state == TaskState.input_required or state == TaskState.working):
                    context_id = result.context_id
                    task_id = result.id
                    for part in result.status.message.parts:
                        section = part.root
                        if section.kind == "text":
                            logger.info(f"**task state: {state}, text: {section.text}")
                            return (state, section.text)
        except Exception as e:
            logger.error(f"Failed to request a2a: {e}")
        return TaskState.unknown, ""

async def main_async():
    while True:
        input_messge = input("You: ")
        status, message = await request_a2a(input_messge, "user_02")
        logger.info(f"Response - status: {status}, message: {message}")

if __name__ == "__main__":
    asyncio.run(main_async())