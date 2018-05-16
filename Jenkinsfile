#!groovy

pipeline {
    agent any
    options {
      timeout(time: 3, unit: 'MINUTES')
    }

    stages {
      stage ('Install dependencies') {
        steps {
            sh 'make install-depends'
        }
      }
      stage ('Perform database migration') {
        steps {
            sh 'make migrate'
        }
      }
      // TODO: run the server
    }

    post {
      always {
        deleteDir()
      }
      // TODO: add post block for Slack.
    }
}
