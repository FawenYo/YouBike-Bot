route:
  receiver: 'mail'

receivers:
  - name: 'mail'
    email_configs:
      - to: ${GMAIL_ACCOUNT}
        from: ${GMAIL_ACCOUNT}
        smarthost: smtp.gmail.com:587
        auth_username: ${GMAIL_ACCOUNT}
        auth_identity: ${GMAIL_ACCOUNT}
        auth_password: ${GMAIL_APPLICATION_PASSWORD}
        send_resolved: true
