import os

import aiosqlite

DB_PATH = os.getenv("DB_PATH", "/data/stats.db")

_SUMMARY_QUERY = """
WITH deltas AS (
    SELECT
        DATE(captured_at) AS day,
        uploaded - LAG(uploaded) OVER (PARTITION BY torrent_hash ORDER BY captured_at) AS delta_bytes
    FROM snapshots
)
SELECT
    day,
    ROUND(SUM(delta_bytes) / (1024.0 * 1024.0 * 1024.0), 2) AS total_gb
FROM deltas
WHERE delta_bytes IS NOT NULL
  AND delta_bytes > 0
  AND day >= ?
  AND day <= ?
GROUP BY day
ORDER BY day
"""


async def get_summary(from_date: str, to_date: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(_SUMMARY_QUERY, (from_date, to_date)) as cursor:
            rows = await cursor.fetchall()
    return [{"date": row["day"], "total_gb": row["total_gb"]} for row in rows]
