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
                    docker rm -f nodeapp || true
                    docker build -t nodeapp-img ./app
                    docker run -d --name nodeapp --network zap-net -p 4000:4000 nodeapp-img

                    for i in {1..30}; do
                        if curl -s http://localhost:4000 > /dev/null; then
                            echo "✅ App is up"
                            break
                        fi
                        sleep 2
                    done
                '''
            }
        }

        stage('Start ZAP') {
            steps {
                sh '''
                    docker rm -f zap || true
                    docker run -u root -d --name zap --network zap-net \
                        -p 8090:8090 ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon -host 0.0.0.0 -port 8090 \
                        -config api.key=${ZAP_API_KEY}

                    echo "⏳ Waiting for ZAP..."
                    for i in {1..60}; do
                        STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://zap:8090)
                        if [ "$STATUS" = "200" ]; then
                            echo "✅ ZAP is ready"
                            break
                        fi
                        sleep 2
                    done
                '''
            }
        }

        stage('Run ZAP Scan') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet python-owasp-zap-v2.4
                    python3 zap_scan.py
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
            echo "🧹 Cleaning up..."
            sh '''
                docker rm -f nodeapp || true
                docker rm -f zap || true
                docker network rm zap-net || true
            '''
        }
    }
}
