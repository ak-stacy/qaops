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

    stage('Inspect workspace & locate project paths') {
      steps {
        sh '''
          echo "== Workspace root =="
          pwd
          echo "== Top-level =="
          ls -la || true

          echo "== Try listing qaops =="
          ls -la qaops || true
          echo "== Try listing qaops/qaops =="
          ls -la qaops/qaops || true

          echo "== Find candidate src/tests =="
          # Ищем src и tests на глубину до 3 каталогов
          find . -maxdepth 3 -type d -name src -o -name tests | sed 's|^./||' || true

          # Определяем SRC_DIR и TEST_DIR
          set -e
          SRC_DIR=""
          TEST_DIR=""

          # Порядок проверки: двойная папка, одиночная папка, корень
          if [ -d "qaops/qaops/src" ] && [ -d "qaops/qaops/tests" ]; then
            SRC_DIR="qaops/qaops/src"
            TEST_DIR="qaops/qaops/tests"
          elif [ -d "qaops/src" ] && [ -d "qaops/tests" ]; then
            SRC_DIR="qaops/src"
            TEST_DIR="qaops/tests"
          elif [ -d "src" ] && [ -d "tests" ]; then
            SRC_DIR="src"
            TEST_DIR="tests"
          fi

          if [ -z "$SRC_DIR" ] || [ -z "$TEST_DIR" ]; then
            echo "ERROR: Не удалось автоматически найти каталоги src/tests."
            echo "Пожалуйста, проверь структуру репозитория в workspace."
            echo "Список каталогов (глубина до 3):"
            find . -maxdepth 3 -type d -print
            exit 1
          fi

          echo "SRC_DIR=$SRC_DIR" > .paths
          echo "TEST_DIR=$TEST_DIR" >> .paths

          echo "Detected SRC_DIR=$SRC_DIR"
          echo "Detected TEST_DIR=$TEST_DIR"
        '''
      }
    }

    stage('Set up venv & deps') {
      steps {
        sh '''
          set -e
          PY=$(cat .pybin)
          . .paths
          echo "Using interpreter: $PY"
          echo "Using SRC_DIR=$SRC_DIR, TEST_DIR=$TEST_DIR"

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
          . .paths
          . venv/bin/activate

          # Добавляем найденный SRC_DIR в PYTHONPATH, чтобы работал import из utils.math
          export PYTHONPATH="${WORKSPACE}/$SRC_DIR"
          echo "PYTHONPATH=$PYTHONPATH"

          # Запуск ВСЕХ тестов без исключений
          pytest -q "$TEST_DIR" --junitxml=report.xml
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