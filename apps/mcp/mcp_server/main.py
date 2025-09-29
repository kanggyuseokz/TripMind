from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="TripMind MCP")

class QuoteIn(BaseModel):
    origin: str
    destination: str
    startDate: str
    endDate: str
    pax: int

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/quotes")
def quotes(body: QuoteIn):
    # 실제 연동 전까지는 목 데이터 반환
    nights = 3
    flights = [
        {
            "id": "F1",
            "vendor": "MockAir",
            "route": f"{body.origin}-{body.destination}",
            "depart": "08:30",
            "arrive": "10:55",
            "price": 240000,
            "currency": "KRW",
        }
    ]
    hotels = [
        {
            "id": "H1",
            "name": "Mock Hotel",
            "nights": nights,
            "pricePerNight": 90000,
            "priceTotal": 90000 * nights,
            "currency": "KRW",
        }
    ]
    return {"flights": flights, "hotels": hotels}