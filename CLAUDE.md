# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common commands

```bash
# Build images (uses Dockerfile.dev)
docker compose build

# Run collector 24/7 (production)
docker compose up -d collector

# Trigger a manual collection (development)
docker compose run --rm collector python -m collector.main --now

# Logs
docker compose logs -f collector
```

## Architecture

This is a torrent stats dashboard. The long-term goal is: **collector → SQLite → API → frontend**.

Current state: collector + inspection scripts only.

```
collector/          Python package — runs 24/7 via APScheduler
  main.py           Entry point. Scheduler fires collect() at 00:00 UTC daily.
                    --now flag skips scheduler and runs once immediately.
  db.py             SQLite helpers. DB_PATH defaults to /data/stats.db (bind-mounted from ./data/)
  clients/
    qbittorrent.py  Fetches upload stats from qBittorrent Web API v2

api/                (planned) FastAPI
frontend/           (planned) Angular
data/               SQLite database (gitignored, bind-mounted into containers)
```

## Key design decisions

- **One snapshot per client per day**: `already_collected_today()` guards against duplicate inserts on container restart.
- **`uploaded` is cumulative**: qBittorrent's `uploaded` field is total bytes since the torrent was added. Daily deltas are computed by diffing consecutive snapshots at query time, not at write time.
- **SQLite over PostgreSQL**: no concurrent writes in practice; simpler ops.
- **Two Dockerfiles**: `Dockerfile.dev` copies local sources (used by docker-compose and CI). `Dockerfile` (prod) clones from GitHub at build time — for end users deploying without the source.
- **Releases**: push a semver tag (`git tag 1.0.0 && git push origin 1.0.0`) → GitHub Actions builds and pushes to `ghcr.io/smarrerof/qbittorrent-dashboard`. On the NAS: `docker compose pull && docker compose up -d collector`.

## Environment variables

See `.env.example`. Key vars:
- `QB_HOST`, `QB_USER`, `QB_PASS` — qBittorrent Web UI
- `DB_PATH` — SQLite path inside container (default `/data/stats.db`)

## Project instructions

- Always ask for permission before creating, editing, or deleting any file.
- Keep README.md bilingual: any change to the Spanish section must be mirrored in the English section, and vice versa.
- Commit messages must follow Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`.
- Do NOT add "Co-Authored-By: XXX" or any similar co-author trailer to commit messages.
- When pushing, always use the user's own git credentials — never override or inject different author/committer identity.
