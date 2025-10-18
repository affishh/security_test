pipeline {
    agent any

    environment {
        ZAP_API_KEY = 'changeme'
        ZAP_PORT = '8080'
        TARGET_URL = 'http://localhost:4000'
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
                    echo "Starting Node.js app"
                    sh 'nohup npm start > app.log 2>&1 &'
                    sleep 5
                }
            }
        }

        stage('Start ZAP in Docker') {
            steps {
                echo "Starting ZAP Docker container"
                sh '''
                    docker run -u root -d \
                      -p 8080:8080 \
                      --name zap \
                      owasp/zap2docker-stable \
                      zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.key=changeme
                    sleep 10
                '''
            }
        }

        stage('Run ZAP Scan') {
            steps {
                sh '''
                    pip install python-owasp-zap-v2.4

                    cat <<EOF > zap_scan.py
import time
from zapv2 import ZAPv2

zap = ZAPv2(apikey='changeme', proxies={'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})

print("Accessing target...")
zap.urlopen("http://localhost:3000")
time.sleep(2)

print("Waiting for passive scan to complete...")
while int(zap.pscan.records_to_scan) > 0:
    print(f"Records to scan: {zap.pscan.records_to_scan}")
    time.sleep(2)

print("Starting active scan...")
scan_id = zap.ascan.scan("http://localhost:3000")

while int(zap.ascan.status(scan_id)) < 100:
    print(f"Active scan progress: {zap.ascan.status(scan_id)}%")
    time.sleep(5)

print("Generating HTML report...")
report = zap.core.htmlreport()
with open("zap_report.html", "w") as f:
    f.write(report)

print("Scan complete.")
EOF

                    python3 zap_scan.py
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
            echo 'Cleaning up'
            sh 'pkill -f node || true'
            sh 'docker stop zap && docker rm zap || true'
        }
    }
}
