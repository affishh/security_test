pipeline {
    agent any

    environment {
        ZAP_PORT = '8090'
        ZAP_API_KEY = 'changeme'
        TARGET_URL = 'http://nodeapp:4000' // Node app hostname in Docker network
        ZAP_API_HOST = 'zap'              // ZAP container hostname in Docker
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Create Docker Network') {
            steps {
                sh '''
                    docker network inspect zap-net >/dev/null 2>&1 || docker network create zap-net
                '''
            }
        }

        stage('Start Node App in Docker') {
            steps {
                echo "🚀 Starting Node app in Docker"
                sh '''
                    docker rm -f nodeapp || true
                    docker build -t nodeapp-img .
                    docker run -d --name nodeapp --network zap-net -p 4000:4000 nodeapp-img

                    # Wait until app is ready
                    for i in {1..30}; do
                        if docker exec nodeapp curl -s http://localhost:4000 > /dev/null; then
                            echo "✅ Node app is up"
                            break
                        fi
                        echo "⏳ Waiting for Node app... ($i/30)"
                        sleep 2
                    done
                '''
            }
        }

        stage('Start ZAP in Docker') {
            steps {
                echo "🚀 Starting ZAP Docker container"
                sh '''
                    docker rm -f zap || true

                    docker run -d --rm --name zap \
                        --network zap-net \
                        -p 8090:8090 \
                        ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon -host 0.0.0.0 -port 8090 \
                        -config api.key=changeme \
                        -config api.addrs.addr=0.0.0.0  \
                        -config api.addrs.addr.regex=true \
                        -config api.disablekey=false \
                        -config api.includelocalhost=true

                    echo "⏳ Waiting for ZAP API to become available..."
                    for i in {1..60}; do
                        STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://zap:8090/JSON/core/view/version/?apikey=changeme || true)
                        if [ "$STATUS" = "200" ]; then
                            echo "✅ ZAP is ready!"
                            break
                        fi
                        echo "⏱️ Waiting for ZAP... ($i/60)"
                        sleep 2
                    done

                    FINAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://zap:8090/JSON/core/view/version/?apikey=changeme || true)
                    if [ "$FINAL_STATUS" != "200" ]; then
                        echo "❌ ZAP failed to become ready. Printing container logs:"
                        docker logs zap || true
                        exit 1
                    fi
                '''
            }
        }

        stage('Run ZAP Scan') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet python-owasp-zap-v2.4

                    echo "🕷️ Running ZAP Scan..."
                    TARGET_URL=${TARGET_URL} ZAP_API_KEY=${ZAP_API_KEY} ZAP_HOST=${ZAP_API_HOST} python3 zap_scan.py
                '''
            }
        }

        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'zap_report.html', onlyIfSuccessful: true
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up containers"
            sh '''
                docker rm -f nodeapp || true
                docker rm -f zap || true
            '''
        }
    }
}
