from fastapi import FastAPI
import httpx
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class WebhookPayload(BaseModel):
    url: str
    data: dict

@app.post("/trigger-webhook")
async def trigger_webhook(payload: WebhookPayload):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            payload.url,
            json=payload.data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

    return {"status": "success", "response_status_code": response.status_code}

@app.get("/day")
async def day_of_the_week() -> str:
    return "Tuesday"

@app.get("/favourite_food")
async def favourite_foot() -> str:
    return "Pizza!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
