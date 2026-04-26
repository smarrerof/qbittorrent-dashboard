# qBittorrent Dashboard

Dashboard de estadísticas de upload para clientes torrent.

## Configuración

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales.

## Desarrollo local

```bash
docker compose build
docker compose up -d collector

# Ver logs
docker compose logs -f collector

# Forzar una colección manualmente
docker compose run --rm collector python -m collector.main --now
```

## Publicar una nueva versión

La imagen se publica automáticamente en `ghcr.io` al crear un tag semver:

```bash
git tag 1.0.0
git push origin 1.0.0
```

## Despliegue en NAS / servidor

Usa este `docker-compose.yml` directamente en Container Manager (Synology), Arcane, Portainer o similar — sin necesidad de clonar el repositorio.

```yaml
services:
  collector:
    image: ghcr.io/smarrerof/qbittorrent-dashboard:latest
    environment:
      - QB_HOST=http://192.168.1.x:8080
      - QB_USER=admin
      - QB_PASS=your_password
    volumes:
      - /path/to/data:/data
    restart: unless-stopped
```

### Variables de entorno

| Variable | Obligatoria | Descripción | Por defecto |
|---|---|---|---|
| `QB_HOST` | Sí | URL del Web UI de qBittorrent | — |
| `QB_USER` | Sí | Usuario del Web UI | — |
| `QB_PASS` | Sí | Contraseña del Web UI | — |
| `DB_PATH` | No | Ruta del fichero SQLite dentro del contenedor | `/data/stats.db` |
