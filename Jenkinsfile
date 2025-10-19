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
                      -Dsonar.login=sqa_4db7ef4b8b07959de0a35daf1066ef02d558cbdb
                    """
                }
            }
        }
    }
}
