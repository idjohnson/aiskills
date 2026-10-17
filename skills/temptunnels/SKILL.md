---
name: temptunnels
description: >-
  Add temporary public tunnels (Ngrok or Cloudflare cloudflared sidecar containers)
  to Kubernetes Helm charts to expose services quickly for testing, demos, or
  webhook development. Use this skill when the user asks to add a temporary tunnel,
  Ngrok sidecar, or Cloudflare (cloudflared) Quick Tunnel option to a Helm chart
  or Kubernetes deployment.
metadata:
  version: "1.1.0"
  tags:
    - helm
    - kubernetes
    - ngrok
    - cloudflare
    - cloudflared
    - tunnel
    - sidecar
---

# Temporary Tunnels (`temptunnels`) Skill

This skill guides the AI agent in adding temporary public tunnel sidecars—supporting both **Ngrok (`ngrok`)** and **Cloudflare Quick Tunnels (`cloudflared`)**—to Kubernetes Helm charts so applications can be exposed publicly without requiring DNS, public LoadBalancers, or Ingress controllers.

## When to Use This Skill

Activate this skill when the user wants to:
- Add an **Ngrok** (`ngrok/ngrok`) or **Cloudflare** (`cloudflare/cloudflared`) tunnel sidecar container to a Helm chart (`deployment.yaml`, `values.yaml`, `NOTES.txt`, `secret.yaml`).
- Expose a Kubernetes service temporarily via a public HTTPS URL (`*.ngrok-free.app` / `*.ngrok.app` or `*.trycloudflare.com`).
- Configure tunnel ports, metrics/health probes, target URLs, or authentication tokens/secrets in Helm.

## Choosing Between Ngrok and Cloudflare (`cloudflared`)

| Feature | Option 1: Ngrok (`ngrok/ngrok`) | Option 2: Cloudflare (`cloudflare/cloudflared`) |
| :--- | :--- | :--- |
| **Public URL Domain** | `*.ngrok-free.app` / `*.ngrok.app` | `*.trycloudflare.com` (Quick Tunnel) |
| **Required Secrets / Tokens** | **Requires `authtoken`** (`--authtoken` or `NGROK_AUTHTOKEN`) | **None required** for Quick Tunnels (optional `TUNNEL_TOKEN` for Named Tunnels) |
| **Target Port** | `http://localhost:<service.targetPort>` | `http://localhost:<service.targetPort>` via `--url` |
| **Sidecar Container Ports** | Optional `4040/TCP` (Inspector UI/API) | `2000/TCP` (`cf-metrics`) for `--metrics` & `/ready` `livenessProbe` |
| **Outbound Ports** | `443/TCP` (TLS to Ngrok edge) | `443/TCP` (HTTPS) & `7844/TCP+UDP` (QUIC/HTTP2 to Cloudflare edge) |

---

## Option 1: Ngrok (`ngrok`) Sidecar for Helm Charts

See [examples/ngrok-helm-sidecar.md](./examples/ngrok-helm-sidecar.md) for complete reference files.

### 1. Port Requirements & Networking (Ngrok)

- **Application Target Port (`service.targetPort`)**:
  - Ngrok shares the Pod's `localhost` network namespace and forwards traffic to `{{ .Values.ngrok.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}`.
- **Ngrok Inspector Port (`4040`, Optional)**:
  - The Ngrok agent listens on `127.0.0.1:4040` for its local inspection UI/API.
- **Outbound Connectivity (`443`)**:
  - Requires outbound TCP/TLS on port `443` to connect to Ngrok edge servers.

### 2. Required Secrets & API Tokens (Ngrok)

- **Ngrok Authtoken (`ngrok.authtoken` / `NGROK_AUTHTOKEN`) — REQUIRED**:
  - Obtained from the [Ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).
  - Passed via `--authtoken` CLI flag or `NGROK_AUTHTOKEN` environment variable.
  - **Best Practice**: Leave `ngrok.authtoken: ""` in `values.yaml` and pass at deploy time (`--set ngrok.authtoken="..."`) or inject from a Kubernetes `Secret`.
- **Ngrok API Key (`NGROK_API_KEY`) — OPTIONAL**:
  - Only needed for REST API operations or automated edge configurations outside standard agent tunneling.

### 3. Helm Changes for Ngrok

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

---

## Option 2: Cloudflare (`cloudflared`) Sidecar for Helm Charts

See [examples/cloudflared-helm-sidecar.md](./examples/cloudflared-helm-sidecar.md) for complete reference files.

### 1. Port Requirements & Networking (Cloudflare)

- **Application Target Port (`service.targetPort`)**:
  - `cloudflared` shares the Pod's `localhost` network namespace and forwards traffic to the main container using `--url {{ .Values.cloudflared.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}`.
- **Metrics & Health Probe Port (`cloudflared.metricsPort`, default `2000/TCP`)**:
  - `cloudflared` exposes a metrics and readiness server via `--metrics "0.0.0.0:{{ .Values.cloudflared.metricsPort }}"`.
  - Expose container port `cf-metrics` (`containerPort: {{ .Values.cloudflared.metricsPort }}`) and configure a Kubernetes `livenessProbe` against `httpGet` path `/ready` on port `cf-metrics`.
- **Outbound Connectivity (`443` & `7844`)**:
  - Requires outbound `443/TCP` (HTTPS to register the tunnel) and `7844/TCP+UDP` (QUIC/HTTP2 connections to the Cloudflare edge).

### 2. Required Secrets & API Tokens (Cloudflare)

- **Ephemeral Quick Tunnels (`*.trycloudflare.com`) — NO SECRETS REQUIRED**:
  - Running `cloudflared tunnel --no-autoupdate --url http://localhost:<port>` requires **zero authentication tokens, secrets, or Cloudflare accounts**. Cloudflare automatically provisions a random `https://<random-words>.trycloudflare.com` URL and logs it to container output.
- **Named Tunnels (Optional `TUNNEL_TOKEN` / `credentials.json`)**:
  - Only required if the user wants a persistent custom hostname on their Cloudflare zone instead of an ephemeral `*.trycloudflare.com` URL (uses `cloudflared tunnel --no-autoupdate run --token <TOKEN>` or `TUNNEL_TOKEN` secret env var).

### 3. Helm Changes for Cloudflare (`cloudflared`)

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

---

## Verification & Usage Commands

After modifying the Helm chart, validate the templates and test rendering:

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
