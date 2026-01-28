pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
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
            echo "ERROR: Python is not installed on this agent."
            exit 1
          fi
          echo $PY > .pybin
          $PY --version
        '''
      }
    }

    stage('Set up venv & deps') {
      steps {
        dir('qaops') {
          sh '''
            set -e
            PY=$(cat ../.pybin)   # .pybin лежит на уровень выше
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
    }

    stage('Run tests') {
      steps {
        dir('qaops') {
          sh '''
            set -e
            . venv/bin/activate
            # Просто запускаем pytest в каталоге qaops — он сам найдёт qaops/tests
            # PYTHONPATH указываем на qaops/src, потому что там лежат модули
            PYTHONPATH="$(pwd)/qaops/src" pytest -q qaops/tests --junitxml=../report.xml
          '''
        }
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
