# Ngrok Docker Compose Reference Examples

## 1. Standard Service-to-Service Networking (`docker-compose.yml` & `.env`)

This pattern runs `ngrok/ngrok` as a companion service in `docker-compose.yml` on the default Compose bridge network, forwarding public HTTPS traffic (`*.ngrok-free.app` / `*.ngrok.app`) to `http://<app-service>:<port>` (e.g., `http://mncampsiteapp:8000`).

> **Note on `command` vs `entrypoint` in Docker Compose:**
> Unlike Kubernetes (where `command` overrides the image `ENTRYPOINT`), Docker Compose's `command` overrides `CMD` and is appended to the `ngrok/ngrok` image's default `ENTRYPOINT` (`["ngrok"]`). Therefore, `command` in `docker-compose.yml` starts directly with `http` (not `ngrok`).

### `.env.example` (Tunnel Variables)

```dotenv
# --- Ngrok Tunnel Configuration ---
# Obtain your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN=""
NGROK_URL="http://mncampsiteapp:8000"
NGROK_LOG="stdout"
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
  # ngrok Tunnel Sidecar Service
  # ----------------------------------------------------------------------------
  ngrok:
    image: ngrok/ngrok:latest
    container_name: mn-campsite-ngrok
    restart: unless-stopped
    depends_on:
      mncampsiteapp:
        condition: service_healthy
    env_file:
      - path: .env
        required: false
    environment:
      - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN:?NGROK_AUTHTOKEN is required}
    command:
      - "http"
      - "${NGROK_URL:-http://mncampsiteapp:8000}"
      - "--log"
      - "${NGROK_LOG:-stdout}"
    ports:
      # Optional: Expose Ngrok local web inspection UI/API on localhost:4040
      - "127.0.0.1:${NGROK_INSPECTOR_PORT:-4040}:4040"
```

### Retrieving the Public Ngrok URL

```bash
# Start services
docker compose up -d

# Fetch the generated public URL from container logs
docker compose logs ngrok | grep "url="

# Or query the local Ngrok API on port 4040
curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*ngrok[^"]*'
```

---

## 2. Optional: Opt-In via Docker Compose Profiles & Shared Network Namespace (`localhost`)

If you want the tunnel disabled by default (similar to `ngrok.enabled: false` in Helm `values.yaml`) or need the tunnel container to share the application container's `localhost` network namespace (identical to a Kubernetes Pod):

```yaml
  ngrok:
    image: ngrok/ngrok:latest
    profiles:
      - ngrok
      - tunnel
    restart: unless-stopped
    network_mode: "service:mncampsiteapp"
    depends_on:
      mncampsiteapp:
        condition: service_healthy
    environment:
      - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN}
    command:
      - "http"
      - "${NGROK_URL:-http://localhost:8000}"
      - "--log"
      - "${NGROK_LOG:-stdout}"
```

Start with the profile enabled:

```bash
NGROK_AUTHTOKEN="your-token" docker compose --profile ngrok up -d
```
