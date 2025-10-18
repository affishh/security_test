pipeline {
    agent any

    environment {
        ZAP_PORT = '8090'
        ZAP_API_KEY = 'changeme'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('Start Node App') {
            steps {
                script {
                    echo 'Starting Node.js app on port 4000'
                    sh '''
                        nohup npm start > node.log 2>&1 &
                        echo $! > nodeapp.pid
                        
                        # Wait for app to start
                        for i in {1..10}; do
                            if curl -s http://localhost:4000 > /dev/null; then
                                echo "Node app is up"
                                break
                            fi
                            echo "Waiting for Node app... (${i}/10)"
                            sleep 2
                        done
                    '''
                }
            }
        }

        stage('Start ZAP in Docker') {
            steps {
                echo "Starting ZAP Docker container on port ${env.ZAP_PORT}"
                sh '''
                    docker rm -f zap || true

                    docker run -u root -d \
                        -p ${ZAP_PORT}:${ZAP_PORT} \
                        --name zap \
                        ghcr.io/zaproxy/zaproxy \
                        zap.sh -daemon -host 0.0.0.0 -port ${ZAP_PORT} -config api.key=${ZAP_API_KEY}

                    echo "Waiting for ZAP to be fully ready..."
                    for i in {1..30}; do
                        if curl -s http://localhost:${ZAP_PORT}/ | grep -q "OWASP ZAP"; then
                            echo "ZAP is fully up and ready!"
                            break
                        fi
                        echo "ZAP not ready yet... (${i}/30)"
                        sleep 2
                    done
                '''
            }
        }

        stage('Setup Python Env and Run ZAP Scan') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet python-owasp-zap-v2.4

                    sleep 5  # ensure ZAP is stable

                    python3 zap_scan.py
                '''
            }
        }

        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'zap_report.html', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo 'Cleaning up Node app and ZAP container'
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
