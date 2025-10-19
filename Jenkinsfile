pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'MySonarQube'  // Name from Jenkins SonarQube config
        SONAR_TOKEN = credentials('SONARQUBE_TOKEN')
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh 'npm install'
            }
        }

        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    sh """
                    sonar-scanner \
                      -Dsonar.projectKey=nodejs-app \
                      -Dsonar.sources=. \
                      -Dsonar.login=squ_734e65894fd94fad26e9dc9994ea852d9106b224
                    """
                }
            }
        }
    }
}
