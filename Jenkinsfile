pipeline {
  agent {
    docker {
      image 'python:3.11-slim'   // можно 'python:3.12-slim' или 'python:3.11-alpine'
      args '-u 0:0'              // чтобы не было проблем с правами на workspace
      reuseNode true
    }
  }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    // при желании можно добавить wrap(AnsiColor...), если плагин установлен
  }

  environment {
    PYTHONPATH = "${WORKSPACE}/qaops/src"
  }

  stages {
    stage('Set up Python deps') {
      steps {
        sh '''
          python --version
          pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            pip install pytest
          fi
        '''
      }
    }

    stage('Run tests') {
      steps {
        sh '''
          pytest -q qaops/tests --junitxml=report.xml
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'report.xml'
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'report.xml', fingerprint: true, onlyIfSuccessful: false
    }
  }
}
