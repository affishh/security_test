pipeline {
    agent any

    environment {
        ZAP_PORT = '8090'
        ZAP_API_KEY = 'changeme'
        TARGET_URL = 'http://host.docker.internal:4000'
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

        stage('Start Node App') {
            steps {
                script {
                    echo "🚀 Starting Node.js app on port 4000"
                    sh '''
                        nohup npm start > nodeapp.log 2>&1 &
                        echo $! > nodeapp.pid

                        for i in {1..30}; do
                            if curl -s http://localhost:4000 > /dev/null; then
                                echo "✅ Node app is up"
                                break
                            fi
                            echo "⏳ Waiting for Node app... ($i/30)"
                            sleep 2
                        done
                    '''
                }
            }
        }

        stage('Start ZAP in Docker') {
            steps {
                echo "🚀 Starting ZAP Docker container on port ${env.ZAP_PORT}"
                sh """
                    docker rm -f zap || true

                    docker run -u root -d \
                        --name zap \
                        -p ${ZAP_PORT}:8090 \
                        ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon \
                        -host 0.0.0.0 \
                        -port 8090 \
                        -config api.key=${ZAP_API_KEY} \
                        -config api.addrs.addr=0.0.0.0 \
                        -config api.addrs.addr.regex=true \
                        -config api.disablekey=false \
                        -config api.includelocalhost=true

                    echo "⏳ Waiting for ZAP API to become available..."

                    for i in {1..60}; do
                        STATUS=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${ZAP_PORT}/JSON/core/view/version/)
                        if [ "\$STATUS" = "200" ]; then
                            echo "✅ ZAP is ready!"
                            break
                        fi
                        echo "⏱️ Waiting for ZAP... (\$i/60)"
                        sleep 2
                    done

                    FINAL_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${ZAP_PORT}/JSON/core/view/version/)
                    if [ "\$FINAL_STATUS" != "200" ]; then
                        echo "❌ ZAP failed to become ready. Printing container logs:"
                        docker logs zap
                        exit 1
                    fi
                """
            }
        }

        stage('Setup Python Env and Run ZAP Scan') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet python-owasp-zap-v2.4

                    echo "🕷️ Running ZAP Scan..."
                    TARGET_URL=${TARGET_URL} ZAP_API_KEY=${ZAP_API_KEY} python3 zap_scan.py
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
            echo "🧹 Cleaning up Node app and ZAP container"
            sh '''
                if [ -f nodeapp.pid ]; then
                    kill $(cat nodeapp.pid) || true
                    rm -f nodeapp.pid
                fi

                docker stop zap || true
                docker rm zap || true
            '''
        }
    }
}
