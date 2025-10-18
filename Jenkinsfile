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
                echo 'Starting app...'
                sh '''
                    nohup node app.js > app.log 2>&1 &
                    echo $! > app.pid
                '''
                sleep 5
            }
        }

        stage('Security Test - ZAP') {
            steps {
                echo 'Running OWASP ZAP...'
                sh '''
                    /snap/bin/zaproxy.baseline \
                        -t http://localhost:3000 \
                        -r zap_report.html \
                        -d -I
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up app...'
            sh 'if [ -f app.pid ]; then kill $(cat app.pid); fi'

            archiveArtifacts artifacts: 'zap_report.html', onlyIfSuccessful: false
        }
    }
}
