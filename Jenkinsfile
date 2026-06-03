pipeline {
  agent any

  stages {
    stage('Build test image') {
      steps {
        sh 'docker build --target unit-test -t buscaminas-unit-test .'
      }
    }

    stage('Unit tests') {
      steps {
        sh 'docker run --rm buscaminas-unit-test'
      }
    }

    stage('Build develop image') {
      steps {
        sh 'docker build --target develop -t buscaminas-develop .'
      }
    }
  }
}
