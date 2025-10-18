pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }

        stage('Start App') {
            steps {
                sh 'nohup node app.js > app.log 2>&1 & echo $! > app.pid'
                sleep 5
            }
        }

        stage('Security Test - ZAP') {
            steps {
                sh '''
                    docker run --rm -u root \
                        -v $(pwd):/zap/wrk/:rw \
                        -t owasp/zap2docker-stable zap-baseline.py \
                        -t http://localhost:3000 \
                        -r zap_report.html
                '''
            }
        }
    }

    post {
        always {
            sh 'if [ -f app.pid ]; then kill $(cat app.pid); fi'
        }
    }
}