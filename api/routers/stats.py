from datetime import date, timedelta

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.db import get_summary

router = APIRouter()


class DailySummary(BaseModel):
    date: str
    total_gb: float


@router.get("/stats/summary", response_model=list[DailySummary])
async def summary(
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
):
    today = date.today()
    _from = from_date or (today - timedelta(days=30))
    _to = to_date or today
    return await get_summary(_from.isoformat(), _to.isoformat())
