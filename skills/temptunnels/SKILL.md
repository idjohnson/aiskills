---
name: temptunnels
description: >-
  Add temporary public tunnels (Ngrok or Cloudflare cloudflared sidecar/companion
  containers) to Kubernetes Helm charts or Docker Compose files (docker-compose.yml)
  to expose services quickly for testing, demos, or webhook development. Use this
  skill when the user asks to add a temporary tunnel, Ngrok sidecar/service, or
  Cloudflare (cloudflared) Quick Tunnel option to a Helm chart, Kubernetes
  deployment, or Docker Compose file.
metadata:
  version: "1.2.0"
  tags:
    - helm
    - kubernetes
    - docker
    - docker-compose
    - ngrok
    - cloudflare
    - cloudflared
    - tunnel
    - sidecar
---

# Temporary Tunnels (`temptunnels`) Skill

This skill guides the AI agent in adding temporary public tunnel containers—supporting both **Ngrok (`ngrok`)** and **Cloudflare Quick Tunnels (`cloudflared`)**—to **Kubernetes Helm charts** and **Docker Compose (`docker-compose.yml` / `docker-compose.yaml`)** files so applications can be exposed publicly without requiring DNS, public LoadBalancers, or Ingress controllers.

## When to Use This Skill

Activate this skill when the user wants to:
- Add an **Ngrok** (`ngrok/ngrok`) or **Cloudflare** (`cloudflare/cloudflared`) tunnel sidecar container to a **Helm chart** (`deployment.yaml`, `values.yaml`, `NOTES.txt`, `secret.yaml`).
- Create or update a **Docker Compose file** (`docker-compose.yml` / `docker-compose.yaml` and `.env` / `.env.example`) with an **Ngrok** or **Cloudflare (`cloudflared`)** tunnel companion service.
- Expose a Kubernetes or Docker Compose service temporarily via a public HTTPS URL (`*.ngrok-free.app` / `*.ngrok.app` or `*.trycloudflare.com`).
- Configure tunnel ports, metrics/health probes, target URLs, or authentication tokens/secrets in Helm or Docker Compose.

## Choosing Between Ngrok and Cloudflare (`cloudflared`)

| Feature | Option 1: Ngrok (`ngrok/ngrok`) | Option 2: Cloudflare (`cloudflare/cloudflared`) |
| :--- | :--- | :--- |
| **Public URL Domain** | `*.ngrok-free.app` / `*.ngrok.app` | `*.trycloudflare.com` (Quick Tunnel) |
| **Required Secrets / Tokens** | **Requires `authtoken`** (`--authtoken` or `NGROK_AUTHTOKEN`) | **None required** for Quick Tunnels (optional `TUNNEL_TOKEN` for Named Tunnels) |
| **Target URL (Helm / K8s Pod)** | `http://localhost:<service.targetPort>` | `http://localhost:<service.targetPort>` via `--url` |
| **Target URL (Docker Compose)** | `http://<app-service>:<port>` (or `http://localhost:<port>` with `network_mode: "service:<app-service>"`) | `http://<app-service>:<port>` via `--url` (or `http://localhost:<port>` with `network_mode: "service:<app-service>"`) |
| **Container / Sidecar Ports** | Optional `4040/TCP` (Inspector UI/API) | `2000/TCP` (`cf-metrics`) for `--metrics` & `/ready` `livenessProbe` |
| **Outbound Ports** | `443/TCP` (TLS to Ngrok edge) | `443/TCP` (HTTPS) & `7844/TCP+UDP` (QUIC/HTTP2 to Cloudflare edge) |

> **Important Difference Between Kubernetes `command` and Docker Compose `command`:**
> - In **Kubernetes (`deployment.yaml`)**, `command` overrides the image's `ENTRYPOINT`, so the binary name (`ngrok` or `cloudflared`) **must** be the first element.
> - In **Docker Compose (`docker-compose.yml`)**, `command` overrides the image's `CMD` and is appended to the image's default `ENTRYPOINT` (`["ngrok"]` or `["cloudflared", "--no-autoupdate"]`). Therefore, `command` in `docker-compose.yml` **must start with the subcommand** (`http` for Ngrok, `tunnel` for Cloudflare) rather than repeating the binary name.

---

## Option 1: Ngrok (`ngrok`)

- **Helm Chart Reference**: [examples/ngrok-helm-sidecar.md](./examples/ngrok-helm-sidecar.md)
- **Docker Compose Reference**: [examples/ngrok-docker-compose.md](./examples/ngrok-docker-compose.md)

### 1. Port Requirements & Networking (Ngrok)

- **Application Target Port**:
  - **Helm (Kubernetes Pod)**: Ngrok shares the Pod's `localhost` network namespace and forwards traffic to `{{ .Values.ngrok.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}`.
  - **Docker Compose**: By default, Ngrok runs on the shared Compose bridge network and forwards traffic to `http://<app-service>:<port>` (e.g., `${NGROK_URL:-http://<app-service>:8000}`). Alternatively, setting `network_mode: "service:<app-service>"` shares the application container's `localhost` namespace (`http://localhost:<port>`).
- **Ngrok Inspector Port (`4040`, Optional)**:
  - The Ngrok agent listens on port `4040` for its local inspection UI/API (`127.0.0.1:4040:4040` in Docker Compose).
- **Outbound Connectivity (`443`)**:
  - Requires outbound TCP/TLS on port `443` to connect to Ngrok edge servers.

### 2. Required Secrets & API Tokens (Ngrok)

- **Ngrok Authtoken (`ngrok.authtoken` / `NGROK_AUTHTOKEN`) — REQUIRED**:
  - Obtained from the [Ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).
  - Passed via `--authtoken` CLI flag or `NGROK_AUTHTOKEN` environment variable.
  - **Best Practice (Helm)**: Leave `ngrok.authtoken: ""` in `values.yaml` and pass at deploy time (`--set ngrok.authtoken="..."`) or inject from a Kubernetes `Secret`.
  - **Best Practice (Docker Compose)**: Inject `NGROK_AUTHTOKEN` from `.env` (and keep `NGROK_AUTHTOKEN=""` in `.env.example`).
- **Ngrok API Key (`NGROK_API_KEY`) — OPTIONAL**:
  - Only needed for REST API operations or automated edge configurations outside standard agent tunneling.

### 3A. Helm Changes for Ngrok

1. **`values.yaml`**:
   ```yaml
   # ----------------------------------------------------------------------------
   # ngrok Tunnel Sidecar Configuration
   # ----------------------------------------------------------------------------
   ngrok:
     enabled: true
     image:
       repository: ngrok/ngrok
       tag: "latest"
       pullPolicy: IfNotPresent
     # Target URL to tunnel to. Defaults to http://localhost:<service.targetPort> (8000)
     url: ""
     authtoken: ""
     log: "stdout"
     # Optional additional arguments to pass to `ngrok http`
     extraArgs: []
     resources:
       requests:
         cpu: 50m
         memory: 64Mi
       limits:
         cpu: 200m
         memory: 128Mi
   ```

2. **`templates/deployment.yaml`** (under `spec.template.spec.containers`):
   ```yaml
           {{- if .Values.ngrok.enabled }}
           - name: ngrok
             image: "{{ .Values.ngrok.image.repository }}:{{ .Values.ngrok.image.tag }}"
             imagePullPolicy: {{ .Values.ngrok.image.pullPolicy }}
             command:
               - ngrok
               - http
               - {{ .Values.ngrok.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}
               - --authtoken
               - {{ .Values.ngrok.authtoken | quote }}
               {{- if .Values.ngrok.log }}
               - --log
               - {{ .Values.ngrok.log | quote }}
               {{- end }}
               {{- range .Values.ngrok.extraArgs }}
               - {{ . | quote }}
               {{- end }}
             resources:
               {{- toYaml .Values.ngrok.resources | nindent 12 }}
           {{- end }}
   ```

3. **`templates/NOTES.txt`**:
   ```yaml
   {{- if .Values.ngrok.enabled }}

   ngrok Tunnel is enabled!
   To retrieve your generated ngrok URL, run:
     kubectl --namespace {{ .Release.Namespace }} logs deploy/{{ include "<chartname>.fullname" . }} -c ngrok | grep "url="
   {{- end }}
   ```

### 3B. Docker Compose Changes for Ngrok

1. **`docker-compose.yml`** (under `services:`):
   ```yaml
     # ----------------------------------------------------------------------------
     # ngrok Tunnel Service
     # ----------------------------------------------------------------------------
     ngrok:
       image: ngrok/ngrok:latest
       container_name: <app-name>-ngrok
       restart: unless-stopped
       depends_on:
         <app-service>:
           condition: service_healthy # Or simple list `depends_on: [<app-service>]` if no healthcheck
       env_file:
         - path: .env
           required: false
       environment:
         - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN:?NGROK_AUTHTOKEN is required}
       command:
         - "http"
         - "${NGROK_URL:-http://<app-service>:8000}"
         - "--log"
         - "${NGROK_LOG:-stdout}"
       ports:
         - "127.0.0.1:${NGROK_INSPECTOR_PORT:-4040}:4040"
   ```
   *(Tip: Add `profiles: ["ngrok", "tunnel"]` if the tunnel should only start when explicitly requested via `docker compose --profile ngrok up -d`.)*

2. **`.env.example`**:
   ```dotenv
   # --- Ngrok Tunnel Configuration ---
   NGROK_AUTHTOKEN=""
   NGROK_URL="http://<app-service>:8000"
   NGROK_LOG="stdout"
   ```

---

## Option 2: Cloudflare (`cloudflared`)

- **Helm Chart Reference**: [examples/cloudflared-helm-sidecar.md](./examples/cloudflared-helm-sidecar.md)
- **Docker Compose Reference**: [examples/cloudflared-docker-compose.md](./examples/cloudflared-docker-compose.md)

### 1. Port Requirements & Networking (Cloudflare)

- **Application Target Port**:
  - **Helm (Kubernetes Pod)**: `cloudflared` shares the Pod's `localhost` network namespace and forwards traffic to the main container using `--url {{ .Values.cloudflared.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}`.
  - **Docker Compose**: By default, `cloudflared` runs on the shared Compose bridge network and forwards traffic using `--url ${CLOUDFLARED_URL:-http://<app-service>:8000}`. Alternatively, setting `network_mode: "service:<app-service>"` allows using `http://localhost:<port>`.
- **Metrics & Health Probe Port (`2000/TCP`)**:
  - `cloudflared` exposes a metrics and readiness server (`/ready`) via `--metrics "0.0.0.0:2000"`.
  - In Kubernetes, expose container port `cf-metrics` (`2000`) and configure a `livenessProbe` against `httpGet` path `/ready` on port `cf-metrics`.
- **Outbound Connectivity (`443` & `7844`)**:
  - Requires outbound `443/TCP` (HTTPS to register the tunnel) and `7844/TCP+UDP` (QUIC/HTTP2 connections to the Cloudflare edge).

### 2. Required Secrets & API Tokens (Cloudflare)

- **Ephemeral Quick Tunnels (`*.trycloudflare.com`) — NO SECRETS REQUIRED**:
  - Running `cloudflared tunnel --no-autoupdate --url http://<target>:<port>` requires **zero authentication tokens, secrets, or Cloudflare accounts**. Cloudflare automatically provisions a random `https://<random-words>.trycloudflare.com` URL and logs it to container output.
- **Named Tunnels (Optional `TUNNEL_TOKEN` / `credentials.json`)**:
  - Only required if the user wants a persistent custom hostname on their Cloudflare zone instead of an ephemeral `*.trycloudflare.com` URL (uses `cloudflared tunnel --no-autoupdate run` with the `TUNNEL_TOKEN` secret/env var).

### 3A. Helm Changes for Cloudflare (`cloudflared`)

1. **`values.yaml`**:
   ```yaml
   # ----------------------------------------------------------------------------
   # Cloudflare Quick Tunnel Sidecar Configuration (Ephemeral *.trycloudflare.com)
   # ----------------------------------------------------------------------------
   cloudflared:
     enabled: true
     image:
       repository: cloudflare/cloudflared
       tag: "latest"
       pullPolicy: IfNotPresent
     # Target URL to tunnel to. Defaults to http://localhost:<service.targetPort> (8000)
     url: ""
     loglevel: info
     metricsPort: 2000
     # Optional additional arguments to pass to `cloudflared tunnel`
     extraArgs: []
     resources:
       requests:
         cpu: 50m
         memory: 64Mi
       limits:
         cpu: 200m
         memory: 128Mi
   ```

2. **`templates/deployment.yaml`** (under `spec.template.spec.containers`):
   ```yaml
           {{- if .Values.cloudflared.enabled }}
           - name: cloudflared
             image: "{{ .Values.cloudflared.image.repository }}:{{ .Values.cloudflared.image.tag }}"
             imagePullPolicy: {{ .Values.cloudflared.image.pullPolicy }}
             command:
               - cloudflared
               - tunnel
               - --no-autoupdate
               - --loglevel
               - {{ .Values.cloudflared.loglevel | quote }}
               - --metrics
               - "0.0.0.0:{{ .Values.cloudflared.metricsPort }}"
               - --url
               - {{ .Values.cloudflared.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}
               {{- range .Values.cloudflared.extraArgs }}
               - {{ . | quote }}
               {{- end }}
             ports:
               - name: cf-metrics
                 containerPort: {{ .Values.cloudflared.metricsPort }}
                 protocol: TCP
             livenessProbe:
               httpGet:
                 path: /ready
                 port: cf-metrics
               failureThreshold: 3
               initialDelaySeconds: 10
               periodSeconds: 10
             resources:
               {{- toYaml .Values.cloudflared.resources | nindent 12 }}
           {{- end }}
   ```

3. **`templates/NOTES.txt`**:
   ```yaml
   {{- if .Values.cloudflared.enabled }}

   Cloudflare Ephemeral Quick Tunnel is enabled!
   To retrieve your generated *.trycloudflare.com URL, run:
     kubectl --namespace {{ .Release.Namespace }} logs deploy/{{ include "<chartname>.fullname" . }} -c cloudflared | grep trycloudflare.com
   {{- end }}
   ```

### 3B. Docker Compose Changes for Cloudflare (`cloudflared`)

1. **`docker-compose.yml`** (under `services:`):
   ```yaml
     # ----------------------------------------------------------------------------
     # Cloudflare Quick Tunnel Service (Ephemeral *.trycloudflare.com)
     # ----------------------------------------------------------------------------
     cloudflared:
       image: cloudflare/cloudflared:latest
       container_name: <app-name>-cloudflared
       restart: unless-stopped
       depends_on:
         <app-service>:
           condition: service_healthy # Or simple list `depends_on: [<app-service>]` if no healthcheck
       command:
         - "tunnel"
         - "--no-autoupdate"
         - "--loglevel"
         - "${CLOUDFLARED_LOGLEVEL:-info}"
         - "--metrics"
         - "0.0.0.0:${CLOUDFLARED_METRICS_PORT:-2000}"
         - "--url"
         - "${CLOUDFLARED_URL:-http://<app-service>:8000}"
   ```
   *(Tip: Add `profiles: ["cloudflared", "tunnel"]` if the tunnel should only start when explicitly requested via `docker compose --profile cloudflared up -d`.)*

2. **`.env.example`** (Optional overrides):
   ```dotenv
   # --- Cloudflare Quick Tunnel Configuration (Optional) ---
   CLOUDFLARED_URL="http://<app-service>:8000"
   CLOUDFLARED_LOGLEVEL="info"
   CLOUDFLARED_METRICS_PORT=2000
   ```

---

## Verification & Usage Commands

### Helm Chart Verification

After modifying a Helm chart, validate the templates and test rendering:

```bash
# 1. Lint the Helm chart
helm lint ./helm/<chartname>

# 2a. Verify template rendering with Ngrok enabled
helm template test-release ./helm/<chartname> \
  --set ngrok.enabled=true \
  --set ngrok.authtoken="test-token"

# 2b. Verify template rendering with Cloudflare Quick Tunnel enabled
helm template test-release ./helm/<chartname> \
  --set cloudflared.enabled=true

# 3a. Retrieve the public Ngrok URL from the sidecar logs
kubectl logs deploy/<release-fullname> -c ngrok | grep "url="

# 3b. Retrieve the public Cloudflare (*.trycloudflare.com) URL from the sidecar logs
kubectl logs deploy/<release-fullname> -c cloudflared | grep trycloudflare.com
```

### Docker Compose Verification

After creating or modifying `docker-compose.yml`, validate syntax and inspect tunnel URLs:

```bash
# 1. Validate docker-compose.yml syntax and interpolated configuration
NGROK_AUTHTOKEN="test-token" docker compose config

# 2. Start the application and tunnel services
docker compose up -d

# 3a. Retrieve the public Ngrok URL from container logs
docker compose logs ngrok | grep "url="

# 3b. Retrieve the public Cloudflare (*.trycloudflare.com) URL from container logs
docker compose logs cloudflared | grep trycloudflare.com
```
