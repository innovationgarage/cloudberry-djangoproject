#!groovy

pipeline {
    agent any
    options {
      timeout(time: 3, unit: 'MINUTES')
    }

    stages {
      stage ('Install dependencies') {
        steps {
            sh './setup-jenkins.sh install-depends'
        }
      }
      stage ('Perform database migration') {
        steps {
            sh './setup-jenkins.sh migrate'
        }
      }
      // TODO: run the server
    }
    // TODO: add post block for Slack.
}
