pipeline {
    agent any
    environment {
        ZAP_API_KEY = 'changeme'
        ZAP_PORT = '8090'
        APP_PORT = '4000'
        TARGET_URL = "http://localhost:${APP_PORT}"
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
                    echo "Starting Node.js app on port ${env.APP_PORT}"
                    sh '''
                        nohup npm start &
                        echo $! > nodeapp.pid

                        # Wait until app is up
                        for i in {1..10}; do
                          if curl -s http://localhost:${APP_PORT} > /dev/null; then
                            echo "Node app is up"
                            break
                          fi
                          echo "Waiting for Node app to start..."
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

                    echo "Waiting for ZAP API to become available..."
                    for i in {1..30}; do
                        if curl -s http://localhost:${ZAP_PORT}/JSON/core/view/version/ | grep -q version; then
                            echo "ZAP is ready!"
                            break
                        else
                            echo "Waiting for ZAP... (${i}/30)"
                            sleep 2
                        fi
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

                    cat <<EOF > zap_scan.py
from zapv2 import ZAPv2

target = '${TARGET_URL}'
apikey = '${ZAP_API_KEY}'
zap = ZAPv2(apikey=apikey, proxies={'http': 'http://localhost:${ZAP_PORT}', 'https': 'http://localhost:${ZAP_PORT}'})

print("Accessing target...")
zap.urlopen(target)

print("Spidering target...")
zap.spider.scan(target)
while int(zap.spider.status()) < 100:
    print("Spider progress: " + zap.spider.status() + "%")
    import time; time.sleep(1)

print("Spider complete. Scanning target...")
zap.ascan.scan(target)
while int(zap.ascan.status()) < 100:
    print("Scan progress: " + zap.ascan.status() + "%")
    import time; time.sleep(5)

print("Scan complete.")
alerts = zap.core.alerts(baseurl=target)
print("Number of alerts: ", len(alerts))

with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())
EOF

                    . venv/bin/activate
                    python3 zap_scan.py
                '''
            }
        }

        stage('Archive Report') {
            steps {
                archiveArtifacts artifacts: 'zap_report.html', fingerprint: true
            }
        }
    }

    post {
        always {
            echo 'Cleaning up Node app and ZAP container'
            sh '''
                [ -f nodeapp.pid ] && kill $(cat nodeapp.pid) || true
                rm -f nodeapp.pid

                docker stop zap || true
                docker rm zap || true
            '''
        }
    }
}
