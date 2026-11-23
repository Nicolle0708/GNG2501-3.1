from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from event_parser import parse_class_event

app = FastAPI(title="WatchOS Class Event Parser")

# 1. Define the exact JSON shape your teammates' Apple Watch must send
class EventPayload(BaseModel):
    title: str
    location: Optional[str] = ""
    start_time_iso: str
    notes: Optional[str] = ""

# 2. Health-check route (lets you verify the server is awake in a browser)
@app.get("/")
def home():
    return {"status": "online", "message": "WatchOS Event Parser API is running!"}

# 3. The main endpoint your teammates' Swift app will call
@app.post("/parse-event")
def parse_event_endpoint(payload: EventPayload):
    pages = parse_class_event(
        title=payload.title,
        location=payload.location or "",
        start_time=payload.start_time_iso,
        notes=payload.notes or ""
    )
    return pages
