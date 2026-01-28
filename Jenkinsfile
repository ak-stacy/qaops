pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  environment {
    // Чтобы импорт "from utils.math" работал при структуре qaops/src/utils/math.py
    PYTHONPATH = "${WORKSPACE}/qaops/src"
  }

  stages {
    stage('Detect Python') {
      steps {
        sh '''
          set -e
          if command -v python3 >/dev/null 2>&1; then
            PY=python3
          elif command -v python >/dev/null 2>&1; then
            PY=python
          else
            echo "ERROR: Python is not installed on this agent. Install python3 or configure an agent with Python."
            exit 1
          fi
          echo "Using $PY"
          echo $PY > .pybin
          $PY --version
        '''
      }
    }

    stage('Set up venv & deps') {
      steps {
        sh '''
          set -e
          PY=$(cat .pybin)
          $PY -m venv venv
          . venv/bin/activate
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
          set -e
          . venv/bin/activate
          # Запускаем ВСЕ тесты из qaops/tests, без исключений
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