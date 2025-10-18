pipeline {
    agent any

    environment {
        TARGET_URL = 'http://nodeapp:4000'
        ZAP_API_KEY = 'changeme'
        ZAP_API_HOST = 'zap'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Network') {
            steps {
                sh '''
                    docker network create zap-net || true
                '''
            }
        }

        stage('Build and Run App') {
            steps {
                sh '''
                    echo "🐳 Building and running the app..."

                    docker rm -f nodeapp || true

                    docker build -t nodeapp-img ./app

                    docker run -d --name nodeapp --network zap-net nodeapp-img

                    echo "⏳ Waiting for the app to start..."
                    for i in {1..20}; do
                        STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:4000)
                        if [ "$STATUS" = "200" ]; then
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
                    echo "🕷️ Starting OWASP ZAP container..."

                    docker rm -f zap || true

                    docker run -u root -d --name zap --network zap-net -p 8090:8090 \
                        ghcr.io/zaproxy/zaproxy zap.sh -daemon \
                        -host 0.0.0.0 -port 8090 \
                        -config api.key=${ZAP_API_KEY} \
                        -config api.addrs.addr=0.0.0.0 \
                        -config api.addrs.addr.regex=true \
                        -config api.disablekey=false \
                        -config api.includelocalhost=true

                    echo "⏳ Waiting for ZAP to be ready..."
                    for i in {1..30}; do
                        STATUS=$(docker exec zap curl -s -o /dev/null -w "%{http_code}" http://localhost:8090)
                        echo "ZAP HTTP status: $STATUS"
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
                    echo "🚨 Running ZAP Scan inside Docker..."

                    docker run --rm --network zap-net \
                        -v $(pwd):/zap/wrk \
                        -e TARGET_URL=${TARGET_URL} \
                        -e ZAP_API_KEY=${ZAP_API_KEY} \
                        -e ZAP_HOST=${ZAP_API_HOST} \
                        python:3.12-slim bash -c "
                            cd /zap/wrk && \
                            pip install --quiet python-owasp-zap-v2.4 && \
                            echo '🚨 Starting ZAP Scan...' && \
                            python3 zap_scan.py
                        "
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
