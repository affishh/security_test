pipeline {
    agent any

    environment {
        ZAP_API_KEY = 'changeme'
        ZAP_API_HOST = 'zap'
        TARGET_URL = 'http://nodeapp:4000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Network') {
            steps {
                sh 'docker network create zap-net || true'
            }
        }

        stage('Build and Run App') {
            steps {
                sh '''
                    echo "🐳 Building and running the app..."
                    export DOCKER_BUILDKIT=0   # 👈 Disable BuildKit to fix buildx error

                    docker rm -f nodeapp || true

                    docker build -t nodeapp-img ./app

                    docker run -d --name nodeapp --network zap-net nodeapp-img

                    echo "⏳ Waiting for the app to start..."
                    for i in {1..60}; do
                        STATUS=$(docker exec zap curl -s -o /dev/null -w "%{http_code}" http://localhost:8090)

                        if [ "$STATUS" = "200" ]; then
                            echo "✅ App is up"
                            break
                        fi
                        echo "⏱️ Waiting for app... ($i/60)"
                        sleep 2
                    done
                '''
            }
        }

        stage('Start ZAP') {
            steps {
                sh '''
                    echo "🕷️ Starting OWASP ZAP container..."

                   

                    docker run -u root -d --name zap --network zap-net \
                        -p 8090:8090 ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon -host 0.0.0.0 -port 8090 \
                        -config api.key=changeme \
                        -config api.addrs.addr=0.0.0.0 \
                        -config api.addrs.addr.regex=true \
                        -config api.disablekey=false \
                        -config api.includelocalhost=true
                    
                    echo "📜 ZAP logs (initial)..."
                    docker logs zap | tail -n 20

                    echo "⏳ Waiting for ZAP to become available..."
                    for i in {1..90}; do
                        STATUS=$(docker exec zap curl -s -o /dev/null -w "%{http_code}" http://localhost:8090)
                        if [ "$STATUS" = "200" ]; then
                            echo "✅ ZAP is ready"
                            break
                        fi
                        echo "⏱️ Waiting for ZAP... ($i/90)"
                        sleep 2
                    done
                '''
            }
        }

        stage('Run ZAP Scan') {
            steps {
                sh '''
                    echo "📦 Setting up Python environment..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet python-owasp-zap-v2.4

                    echo "🚨 Running ZAP scan..."
                    TARGET_URL=${TARGET_URL} ZAP_API_KEY=${ZAP_API_KEY} ZAP_HOST=${ZAP_API_HOST} python3 zap_scan.py
                '''
            }
        }

        stage('Archive Report') {
            steps {
                echo "🗂️ Archiving ZAP report..."
                archiveArtifacts artifacts: 'zap_report.html', onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up..."
            sh '''
                docker rm -f nodeapp || true
                docker rm -f zap || true
                docker network rm zap-net || true

            '''
        }
    }
}
