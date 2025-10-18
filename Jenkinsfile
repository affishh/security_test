pipeline {
    agent any

    environment {
        ZAP_PORT = '8090'
        ZAP_API_KEY = 'changeme'
        TARGET_URL = 'http://host.docker.internal:4000'  // Use host.docker.internal for Docker container access
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
                    echo "Starting Node.js app on port 4000"
                    sh '''
                        nohup npm start > nodeapp.log 2>&1 &
                        echo $! > nodeapp.pid

                        for i in {1..30}; do
                            if curl -s http://localhost:4000 > /dev/null; then
                                echo "Node app is up"
                                break
                            fi
                            echo "Waiting for Node app... ($i/30)"
                            sleep 2
                        done
                    '''
                }
            }
        }

        stage('Start ZAP in Docker') {
            steps {
                echo "Starting ZAP Docker container on port ${env.ZAP_PORT}"
                sh """
                    docker rm -f zap || true

                    # Uncomment this line if Jenkins runs on Linux to fix localhost networking issues
                    # docker run -u root -d --network=host --name zap ghcr.io/zaproxy/zaproxy zap.sh -daemon -host 0.0.0.0 -port ${ZAP_PORT} -config api.key=${ZAP_API_KEY}

                    # For Mac/Windows or other OSes, use port mapping instead
                    docker run -u root -d -p ${ZAP_PORT}:${ZAP_PORT} --name zap ghcr.io/zaproxy/zaproxy zap.sh -daemon -host 0.0.0.0 -port ${ZAP_PORT} -config api.key=${ZAP_API_KEY}

                    echo "Waiting for ZAP API to become available..."
                    for i in \$(seq 1 30); do
                        status=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${ZAP_PORT}/JSON/core/view/version/)
                        if [ "\$status" = "200" ]; then
                            echo "✅ ZAP is ready!"
                            break
                        fi
                        echo "⏳ Waiting for ZAP... (\$i/30)"
                        sleep 2
                    done

                    # Final check
                    status=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${ZAP_PORT}/JSON/core/view/version/)
                    if [ "\$status" != "200" ]; then
                        echo "❌ ZAP did not start properly. Container logs:"
                        docker logs zap || true
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

                    echo "Running ZAP Scan..."
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
            echo "Cleaning up Node app and ZAP container"
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
