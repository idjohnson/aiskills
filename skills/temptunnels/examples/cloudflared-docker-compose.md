# Cloudflare (`cloudflared`) Docker Compose Reference Examples

## 1. Ephemeral Quick Tunnel (`*.trycloudflare.com`) — No Secrets Required

This pattern runs `cloudflare/cloudflared` as a companion service in `docker-compose.yml` on the default Compose bridge network, exposing `http://<app-service>:<port>` (e.g., `http://mncampsiteapp:8000`) on an ephemeral `*.trycloudflare.com` URL and serving readiness/metrics on port `2000`.

> **Note on `command` vs `entrypoint` in Docker Compose:**
> Unlike Kubernetes (where `command` overrides the image `ENTRYPOINT`), Docker Compose's `command` overrides `CMD` and is appended to the `cloudflare/cloudflared` image's default `ENTRYPOINT` (`["cloudflared", "--no-autoupdate"]`). Therefore, `command` in `docker-compose.yml` starts directly with `tunnel` (not `cloudflared`).

### `.env.example` (Optional Tunnel Variables)

```dotenv
# --- Cloudflare Quick Tunnel Configuration (Optional) ---
# Ephemeral *.trycloudflare.com tunnels require no token or account.
CLOUDFLARED_URL="http://mncampsiteapp:8000"
CLOUDFLARED_LOGLEVEL="info"
CLOUDFLARED_METRICS_PORT=2000
```

### `docker-compose.yml`

```yaml
services:
  mncampsiteapp:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mn-campsite-explorer
    ports:
      - "${APP_PORT:-8000}:8000"
    env_file:
      - path: .env
        required: false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

  # ----------------------------------------------------------------------------
  # Cloudflare Quick Tunnel Sidecar Service (Ephemeral *.trycloudflare.com)
  # ----------------------------------------------------------------------------
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: mn-campsite-cloudflared
    restart: unless-stopped
    depends_on:
      mncampsiteapp:
        condition: service_healthy
    command:
      - "tunnel"
      - "--no-autoupdate"
      - "--loglevel"
      - "${CLOUDFLARED_LOGLEVEL:-info}"
      - "--metrics"
      - "0.0.0.0:${CLOUDFLARED_METRICS_PORT:-2000}"
      - "--url"
      - "${CLOUDFLARED_URL:-http://mncampsiteapp:8000}"
```

### Retrieving the Public `*.trycloudflare.com` URL

```bash
# Start services
docker compose up -d

# Retrieve the generated *.trycloudflare.com URL from container logs
docker compose logs cloudflared | grep trycloudflare.com
```

---

## 2. Optional: Cloudflare Named Tunnel (With `TUNNEL_TOKEN` Secret)

If a user wants a persistent hostname managed in the Cloudflare Zero Trust dashboard instead of a random `*.trycloudflare.com` Quick Tunnel, pass `TUNNEL_TOKEN` via `.env` or environment variables and use `run`:

### `docker-compose.yml` (Named Tunnel Variant)

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: mn-campsite-cloudflared
    restart: unless-stopped
    depends_on:
      mncampsiteapp:
        condition: service_healthy
    env_file:
      - path: .env
        required: false
    environment:
      - TUNNEL_TOKEN=${TUNNEL_TOKEN:?TUNNEL_TOKEN is required for named tunnels}
    command:
      - "tunnel"
      - "--no-autoupdate"
      - "--loglevel"
      - "${CLOUDFLARED_LOGLEVEL:-info}"
      - "--metrics"
      - "0.0.0.0:${CLOUDFLARED_METRICS_PORT:-2000}"
      - "run"
```

---

## 3. Optional: Opt-In via Docker Compose Profiles & Shared Network Namespace (`localhost`)

If you want the tunnel disabled by default (similar to `cloudflared.enabled: false` in Helm `values.yaml`) or need the tunnel container to share the application container's `localhost` network namespace (identical to a Kubernetes Pod):

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    profiles:
      - cloudflared
      - tunnel
    restart: unless-stopped
    network_mode: "service:mncampsiteapp"
    depends_on:
      mncampsiteapp:
        condition: service_healthy
    command:
      - "tunnel"
      - "--no-autoupdate"
      - "--loglevel"
      - "${CLOUDFLARED_LOGLEVEL:-info}"
      - "--metrics"
      - "0.0.0.0:${CLOUDFLARED_METRICS_PORT:-2000}"
      - "--url"
      - "${CLOUDFLARED_URL:-http://localhost:8000}"
```

Start with the profile enabled:

```bash
docker compose --profile cloudflared up -d
```
