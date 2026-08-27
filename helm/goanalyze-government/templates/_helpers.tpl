{{- define "goanalyze-government.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default "goanalyze-government" .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}
