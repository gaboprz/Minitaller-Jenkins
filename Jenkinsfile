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
    stage('Validate Environment') {
      agent any
      steps {
        sh '''
          if ! command -v docker > /dev/null 2>&1; then
            echo "ERROR: Docker no está disponible en este agente."
            exit 1
          fi
          if ! docker info > /dev/null 2>&1; then
            echo "ERROR: El daemon de Docker no responde en este agente."
            exit 1
          fi
          echo "Docker OK: $(docker version --format '{{.Server.Version}}')"
        '''
      }
    }

    stage('Checkout') {
      agent any
      steps {
        checkout scm
        script {
          env.GIT_COMMIT_SHORT = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()
          env.CURRENT_BRANCH = sh(script: "git name-rev --name-only HEAD | sed 's|remotes/origin/||'", returnStdout: true).trim()
        }
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

          if ! docker cp "${TEST_CONTAINER}:/app/reports/unit-tests.xml" reports/unit-tests.xml; then
            echo "ERROR: no se pudo copiar el reporte XML. El contenedor no generó el archivo."
            docker rm -f "${TEST_CONTAINER}" || true
            exit 1
          fi
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
        sh '''
          docker build --target develop \
            -t buscaminas-develop:${BUILD_NUMBER} \
            -t buscaminas-develop:${GIT_COMMIT_SHORT} \
            .
        '''
      }
    }

    stage('Push to Registry') {
      agent any
      when {
        expression {
          env.CURRENT_BRANCH == 'main'
        }
      }
      steps {
        deleteDir()
        unstash 'source-code'
        withCredentials([usernamePassword(
          credentialsId: 'ghcr-credentials',
          usernameVariable: 'REGISTRY_USER',
          passwordVariable: 'REGISTRY_TOKEN'
        )]) {
          sh '''
            echo "${REGISTRY_TOKEN}" | docker login ghcr.io -u "${REGISTRY_USER}" --password-stdin

            docker tag buscaminas-develop:${BUILD_NUMBER} ghcr.io/kendarooo/buscaminas:latest
            docker tag buscaminas-develop:${BUILD_NUMBER} ghcr.io/kendarooo/buscaminas:${BUILD_NUMBER}
            docker tag buscaminas-develop:${BUILD_NUMBER} ghcr.io/kendarooo/buscaminas:${GIT_COMMIT_SHORT}

            docker push ghcr.io/kendarooo/buscaminas:latest
            docker push ghcr.io/kendarooo/buscaminas:${BUILD_NUMBER}
            docker push ghcr.io/kendarooo/buscaminas:${GIT_COMMIT_SHORT}
          '''
        }
      }
      post {
        always {
          sh 'docker logout ghcr.io || true'
        }
      }
    }
  }

  post {
    always {
      script {
        node('') {
          sh '''
            docker rmi -f buscaminas-ci-lint:${BUILD_NUMBER}  || true
            docker rmi -f buscaminas-ci-test:${BUILD_NUMBER}  || true
            docker rmi -f buscaminas-develop:${BUILD_NUMBER}  || true
          '''
        }
      }
    }
  }
}
