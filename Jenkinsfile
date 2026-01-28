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
          echo "$PY" > .pybin
          $PY --version
        '''
      }
    }

    stage('Write .paths') {
      steps {
        sh '''
          set -e
          # ТВОИ актуальные пути после упрощения структуры:
          SRC_DIR="qaops/src"
          TEST_DIR="qaops/tests"

          # Создаём служебный файл с путями
          {
            echo "SRC_DIR=$SRC_DIR"
            echo "TEST_DIR=$TEST_DIR"
          } > .paths

          echo "[.paths created]"
          cat .paths
        '''
      }
    }

    stage('Set up venv & deps') {
      steps {
        sh '''
          set -e
          PY=$(cat .pybin)
          . ./.paths

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
          . ./.paths
          . venv/bin/activate

          # Добавляем SRC_DIR в PYTHONPATH, чтобы проходили импорты (from utils.math import add)
          export PYTHONPATH="${WORKSPACE}/${SRC_DIR}"
          echo "PYTHONPATH=$PYTHONPATH"

          # Запускаем ВСЕ тесты, без исключений
          pytest -q "${TEST_DIR}" --junitxml=report.xml
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
