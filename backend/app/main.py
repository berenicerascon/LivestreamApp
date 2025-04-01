from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from fastapi.middleware.cors import CORSMiddleware
from youtube_utils import schedule_broadcast

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BroadcastRequest(BaseModel):
    title: constr(min_length=1)
    month: int
    day: int
    time: constr(regex=r"^\d{2}:\d{2}$")  # HH:MM format

@app.post("/broadcast")
def create_broadcast(request: BroadcastRequest):
    try:
        print(f"[DEBUG] Got request: {request}")
        broadcast_id, youtube_url = schedule_broadcast(
            title=request.title,
            month=request.month,
            day=request.day,
            time_str=request.time
        )
        print(f"[DEBUG] Result: {broadcast_id}, {youtube_url}")

        if not broadcast_id:
            raise HTTPException(status_code=500, detail="Broadcast creation failed.")

        return {"id": broadcast_id, "url": youtube_url}
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import PlainTextResponse

@app.get("/live_url", response_class=PlainTextResponse)
def get_live_url():
    try:
        with open("live_url.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "No livestream available."
