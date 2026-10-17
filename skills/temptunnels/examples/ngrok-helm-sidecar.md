# Ngrok Helm Sidecar Reference Examples

## 1. Direct `values.yaml` & `deployment.yaml` Pattern (Reference Implementation)

This pattern matches the `mncampsiteapp` Helm chart implementation where the Ngrok sidecar tunnels `http://localhost:<service.targetPort>` using `--authtoken` and logs to `stdout`.

### `values.yaml`

```yaml
service:
  type: ClusterIP
  port: 80
  targetPort: 8000

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
  authtoken: "" # Pass via --set ngrok.authtoken="<YOUR_NGROK_AUTHTOKEN>"
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

### `templates/deployment.yaml` (Sidecar Snippet)

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

### `templates/NOTES.txt`

```yaml
{{- if .Values.ngrok.enabled }}

ngrok Tunnel is enabled!
To retrieve your generated ngrok URL, run:
  kubectl --namespace {{ .Release.Namespace }} logs deploy/{{ include "mychart.fullname" . }} -c ngrok | grep "url="
{{- end }}
```

---

## 2. Storing `NGROK_AUTHTOKEN` in the Chart's `templates/secret.yaml`

If you want to store the Ngrok authtoken inside the Helm chart's Kubernetes `Secret` instead of passing it directly on the container command line (which is visible in `kubectl describe pod`):

### `templates/secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "mychart.secretName" . }}
type: Opaque
stringData:
  {{- if .Values.ngrok.enabled }}
  NGROK_AUTHTOKEN: {{ .Values.ngrok.authtoken | quote }}
  {{- end }}
```

### `templates/deployment.yaml` (Using `NGROK_AUTHTOKEN` Env Var)

The official `ngrok/ngrok` image automatically reads the `NGROK_AUTHTOKEN` environment variable when `--authtoken` is omitted from `command`:

```yaml
        {{- if .Values.ngrok.enabled }}
        - name: ngrok
          image: "{{ .Values.ngrok.image.repository }}:{{ .Values.ngrok.image.tag }}"
          imagePullPolicy: {{ .Values.ngrok.image.pullPolicy }}
          command:
            - ngrok
            - http
            - {{ .Values.ngrok.url | default (printf "http://localhost:%v" .Values.service.targetPort) | quote }}
            {{- if .Values.ngrok.log }}
            - --log
            - {{ .Values.ngrok.log | quote }}
            {{- end }}
            {{- range .Values.ngrok.extraArgs }}
            - {{ . | quote }}
            {{- end }}
          env:
            - name: NGROK_AUTHTOKEN
              valueFrom:
                secretKeyRef:
                  name: {{ include "mychart.secretName" . }}
                  key: NGROK_AUTHTOKEN
          resources:
            {{- toYaml .Values.ngrok.resources | nindent 12 }}
        {{- end }}
```
