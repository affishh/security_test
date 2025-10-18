pipeline {
    agent any

    environment {
        ZAP_API_KEY = 'changeme'
        ZAP_PORT = '8090'
        TARGET_URL = 'http://localhost:4000'
        NODE_PORT = '4000'
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
                    echo "Starting Node.js app on port ${env.NODE_PORT}"
                    sh 'nohup npm start > app.log 2>&1 & echo $! > nodeapp.pid'
                    sh '''
                    for i in {1..10}; do
                      if curl -s ${TARGET_URL} > /dev/null; then
                        echo "Node app is up"
                        break
                      else
                        echo "Waiting for Node app..."
                        sleep 3
                      fi
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
                docker run -u root -d \
                  -p ${ZAP_PORT}:${ZAP_PORT} \
                  --name zap \
                  ghcr.io/zaproxy/zaproxy \
                  zap.sh -daemon -host 0.0.0.0 -port ${ZAP_PORT} -config api.key=${ZAP_API_KEY}
                sleep 10
                """
                
            }
        }

        stage('Setup Python Env and Run ZAP Scan') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --quiet python-owasp-zap-v2.4
                '''

                writeFile file: 'zap_scan.py', text: """
import time
import os
from zapv2 import ZAPv2

api_key = os.getenv('ZAP_API_KEY', 'changeme')
target = os.getenv('TARGET_URL', 'http://localhost:4000')
zap_port = os.getenv('ZAP_PORT', '8090')

zap = ZAPv2(apikey=api_key, proxies={
    'http': f'http://localhost:{zap_port}',
    'https': f'http://localhost:{zap_port}'
})

print("Accessing target...")
zap.urlopen(target)
time.sleep(2)

print("Waiting for passive scan to complete...")
while int(zap.pscan.records_to_scan) > 0:
    print(f"Records to scan: {zap.pscan.records_to_scan}")
    time.sleep(2)

print("Starting active scan...")
scan_id = zap.ascan.scan(target)

while int(zap.ascan.status(scan_id)) < 100:
    print(f"Active scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)

print("Generating HTML report...")
report = zap.core.htmlreport()
with open("zap_report.html", "w") as f:
    f.write(report)

print("Scan complete.")
"""

                sh '''
                . venv/bin/activate
                python zap_scan.py
                '''
            }
        }

        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'zap_report.html', allowEmptyArchive: false
                echo 'ZAP report archived. You can download it from Jenkins UI.'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up Node app and ZAP container'
            sh '''
            if [ -f nodeapp.pid ]; then
                kill $(cat nodeapp.pid) || true
                rm nodeapp.pid
            fi
            docker stop zap || true
            docker rm zap || true
            '''
        }
    }
}
