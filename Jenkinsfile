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

        stage('Create Docker Network') {
            steps {
                sh 'docker network create zap-net || true'
            }
        }

        stage('Build and Run App') {
            steps {
                sh '''
                    echo "🐳 Building and running the app..."
                    docker rm -f nodeapp || true
                    docker build -t nodeapp-img ./app
                    docker run -d --name nodeapp --network zap-net nodeapp-img

                    echo "⏳ Waiting for app to be ready..."
                    for i in {1..30}; do
                        STATUS=$(docker exec nodeapp curl -s -o /dev/null -w "%{http_code}" http://localhost:4000 || true)
                        echo "App HTTP status: $STATUS"
                        if [ "$STATUS" = "200" ]; then
                            echo "✅ App is ready!"
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
                    echo "🕷️ Starting OWASP ZAP container..."
                    docker rm -f zap || true

                    docker run -u root -d --name zap --network zap-net \
                        -p 8090:8090 ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon -host 0.0.0.0 -port 8090 \
                        -config api.key=${ZAP_API_KEY} \
                        -config api.addrs.addr=0.0.0.0 \
                        -config api.addrs.addr.regex=true \
                        -config api.disablekey=false \
                        -config api.includelocalhost=true

                    echo "⏳ Waiting for ZAP to be ready..."
                    for i in {1..60}; do
                        STATUS=$(docker exec zap curl -s -o /dev/null -w "%{http_code}" http://localhost:8090 || true)
                        echo "ZAP HTTP status: $STATUS"
                        if [ "$STATUS" = "200" ]; then
                            echo "✅ ZAP is ready!"
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
                    echo "🚨 Running ZAP Scan inside Docker..."
                    docker run --rm --network zap-net -v $(pwd):/zap/wrk python:3.12-slim bash -c "
                        cd /zap/wrk &&
                        echo "🚨 Running ZAP Scan..."
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
            echo "🧹 Cleaning up..."
            sh '''
                docker rm -f nodeapp || true
                docker rm -f zap || true
                docker network rm zap-net || true
            '''
        }
    }
}
