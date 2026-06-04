pipeline {
  agent none

  options {
    skipDefaultCheckout(true)
    timestamps()
  }

  environment {
    TEST_CONTAINER = "buscaminas-unit-test-${BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      agent any
      steps {
        checkout scm
        stash(
          name: 'source-code',
          includes: '**/*',
          excludes: '.git/**,reports/**,__pycache__/**,*.pyc'
        )
      }
    }

    stage('Static Analysis') {
      agent any
      steps {
        deleteDir()
        unstash 'source-code'
        sh '''
          docker build --target lint -t buscaminas-ci-lint:${BUILD_NUMBER} .
          docker run --rm buscaminas-ci-lint:${BUILD_NUMBER}
        '''
      }
    }

    stage('Unit Tests') {
      agent any
      steps {
        deleteDir()
        unstash 'source-code'
        sh '''
          mkdir -p reports
          rm -f reports/unit-tests.xml || true
          docker build --target unit-test -t buscaminas-ci-test:${BUILD_NUMBER} .
          docker rm -f "${TEST_CONTAINER}" || true

          set +e
          docker run --name "${TEST_CONTAINER}" buscaminas-ci-test:${BUILD_NUMBER}
          TEST_STATUS=$?

          docker cp "${TEST_CONTAINER}:/app/reports/unit-tests.xml" reports/unit-tests.xml || true
          docker rm -f "${TEST_CONTAINER}" || true

          exit "${TEST_STATUS}"
        '''
      }
      post {
        always {
          junit testResults: 'reports/unit-tests.xml', allowEmptyResults: false
        }
      }
    }

    stage('Build App Image') {
      agent any
      steps {
        deleteDir()
        unstash 'source-code'
        sh 'docker build --target develop -t buscaminas-develop:${BUILD_NUMBER} .'
      }
    }
  }
}
