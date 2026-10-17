# Cloudflare (`cloudflared`) Helm Sidecar Reference Examples

## 1. Ephemeral Quick Tunnel (`*.trycloudflare.com`) — No Secrets Required

This pattern matches the `mncampsiteapp` Helm chart implementation where `cloudflare/cloudflared` runs as a sidecar container, exposing `http://localhost:<service.targetPort>` on an ephemeral `*.trycloudflare.com` URL and serving health metrics on port `2000` (`cf-metrics`).

### `values.yaml`

```yaml
service:
  type: ClusterIP
  port: 80
  targetPort: 8000

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

### `templates/deployment.yaml` (Sidecar Snippet)

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

### `templates/NOTES.txt`

```yaml
{{- if .Values.cloudflared.enabled }}

Cloudflare Ephemeral Quick Tunnel is enabled!
To retrieve your generated *.trycloudflare.com URL, run:
  kubectl --namespace {{ .Release.Namespace }} logs deploy/{{ include "mychart.fullname" . }} -c cloudflared | grep trycloudflare.com
{{- end }}
```

---

## 2. Optional: Cloudflare Named Tunnel (With `TUNNEL_TOKEN` Secret)

If a user wants a persistent hostname managed in the Cloudflare Zero Trust dashboard instead of a random `*.trycloudflare.com` Quick Tunnel, `cloudflared` requires a `TUNNEL_TOKEN`:

### `templates/deployment.yaml` (Named Tunnel Variant)

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
            {{- if .Values.cloudflared.tunnelToken }}
            - run
            {{- else }}
            - --url
            - {{ .Values.cloudflared.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}
            {{- end }}
          {{- if .Values.cloudflared.tunnelToken }}
          env:
            - name: TUNNEL_TOKEN
              valueFrom:
                secretKeyRef:
                  name: {{ include "mychart.secretName" . }}
                  key: CLOUDFLARE_TUNNEL_TOKEN
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
