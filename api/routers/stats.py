from datetime import date, timedelta

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.db import get_summary, get_by_day

router = APIRouter()


class DailySummary(BaseModel):
    date: str
    total_gb: float


class TorrentDelta(BaseModel):
    name: str
    uploaded_gb: float


@router.get("/stats/summary", response_model=list[DailySummary])
async def summary(
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
):
    today = date.today()
    _from = from_date or (today - timedelta(days=30))
    _to = to_date or today
    return await get_summary(_from.isoformat(), _to.isoformat())


@router.get("/stats/by-day", response_model=list[TorrentDelta])
async def by_day(date: date = Query(...)):
    return await get_by_day(date.isoformat())
