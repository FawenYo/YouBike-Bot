apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
  - name: Prometheus
    type: prometheus
    # Access mode - proxy (server in the UI) or direct (browser in the UI).
    access: proxy
    url: http://prometheus:9090
    jsonData:
      httpMethod: POST
      manageAlerts: true
  - name: Alertmanager
    type: alertmanager
    url: http://alertmanager:9093
    jsonData:
      # Valid options for implementation include mimir, cortex and prometheus
      implementation: prometheus
      # Whether or not Grafana should send alert instances to this Alertmanager
      handleGrafanaManagedAlerts: false
    # optionally
    basicAuth: true
    basicAuthUser: my_user
    secureJsonData:
      basicAuthPassword: test_password
  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    user: FawenYo
    secureJsonData:
      password: ${POSTGRES_PASSWORD} # TODO: Edit this to your password
    jsonData:
      database: youbike
      sslmode: 'disable'
    isDefault: true