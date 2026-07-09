from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import query, execute
from app.events import record_interaction

router = APIRouter(prefix="/bookings")


class QuoteRequest(BaseModel):
    listing_id: str
    nights: int = Field(ge=1, le=60)


class ConfirmRequest(BaseModel):
    booking_id: str = Field(min_length=8)       # client-supplied idempotency key
    user_id: str
    listing_id: str
    nights: int = Field(ge=1, le=60)


@router.post("/quote")
async def quote(body: QuoteRequest) -> dict:
    """Price a stay for N nights — read-only, no state written yet."""
    rows = query(
        "SELECT name, price_per_night FROM listings WHERE id = %(id)s",
        {"id": body.listing_id},
    )
    if not rows:
        raise HTTPException(404, "listing not found")
    nightly = float(rows[0]["price_per_night"])
    return {
        "listing_id": body.listing_id,
        "name": rows[0]["name"],
        "nights": body.nights,
        "total_price": round(nightly * body.nights, 2),
    }


@router.post("/confirm")
async def confirm(body: ConfirmRequest) -> dict:
    """Confirm a booking idempotently — a retry with the same id is a no-op."""
    existing = query("SELECT id, status FROM bookings WHERE id = %(id)s",
                     {"id": body.booking_id})
    if existing:
        return {"booking_id": body.booking_id, "status": existing[0]["status"],
                "idempotent": True}            # already confirmed — return as-is

    priced = await quote(QuoteRequest(listing_id=body.listing_id, nights=body.nights))
    execute(
        """INSERT INTO bookings (id, user_id, listing_id, nights, total_price)
           VALUES (%s, %s, %s, %s, %s)""",
        [(body.booking_id, body.user_id, body.listing_id,
          body.nights, priced["total_price"])],
    )
    record_interaction(body.user_id, [body.listing_id], action="book")
    return {"booking_id": body.booking_id, "status": "confirmed", "idempotent": False}
