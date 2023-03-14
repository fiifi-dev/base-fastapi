pipeline {
  agent { label 'agent1' }

  environment {
    ANSIBLE_PRIVATE_KEY=credentials('jenkins')
    REGISTRY_CRED=credentials('registry') 
    WORKSPACE="${WORKSPACE}"
    // App Settings
    APP_PORT="$APP_PORT"
    SECRET_KEY="$SECRET_KEY"
    DEBUG="$DEBUG"
    // Database
    DATABASE_URL="mysql://root:testpass123@127.0.0.1:3306/student_management_system"
    // First User
    ROOT_USER_EMAIL="$ROOT_USER_EMAIL"
    ROOT_USER_PASSWORD="$ROOT_USER_PASSWORD"
    // Email
    SMTP_HOST="$SMTP_HOST"
    SMTP_PORT="$SMTP_PORT"
    EMAILS_FROM_EMAIL="$EMAILS_FROM_EMAIL"
    SMTP_USER="$SMTP_USER"
    SMTP_PASSWORD="$SMTP_PASSWORD"
    // Minio
    USE_MINIO="$USE_MINIO"
    MINIO_ACCESS_KEY="$MINIO_ACCESS_KEY"
    MINIO_SECRET_KEY="$MINIO_SECRET_KEY"
    MINIO_ENDPOINT="$MINIO_ENDPOINT"
    MINIO_BUCKET="$MINIO_BUCKET"
  }

  stages {
    stage('build and deploy') {
      steps {
        sh 'ansible-galaxy collection install -r deployment/requirements.yml'
        sh 'ansible-playbook -i deployment/inventory.hosts --private-key=$ANSIBLE_PRIVATE_KEY deployment/playbook.yml'
      }
    }
  }
}