from logging import getLogger
from fastapi import FastAPI, Request

import uvicorn

logger = getLogger(__name__)
app = FastAPI()

has_finished = False

@app.post("/notify")
async def notify(request: Request):
    data = await request.json()
    global has_finished
    has_finished = True
    print(f"Received notification: {data}")
    return {"status": has_finished}

@app.get("/status")
def get_status():
    global has_finished
    return {"status": has_finished}

@app.put("/reset")
def reset():
    global has_finished
    has_finished = False
    return {"status": has_finished}

if __name__ == "__main__":
    uvicorn.run(app, port=8088)
