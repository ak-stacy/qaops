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

    stage('Locate src/tests & write .paths') {
      steps {
        sh '''
          set -e
          echo "== Workspace root =="
          pwd
          echo "== Top-level =="
          ls -la || true

          echo "== Candidate dirs (depth<=3) =="
          find . -maxdepth 3 -type d -name src -o -name tests | sed 's|^./||' || true

          SRC_DIR=""
          TEST_DIR=""

          # 1) Предпочтительно: qaops/src + qaops/tests
          if [ -d "qaops/src" ] && [ -d "qaops/tests" ]; then
            SRC_DIR="qaops/src"
            TEST_DIR="qaops/tests"
          # 2) Альтернатива: просто src + tests в корне
          elif [ -d "src" ] && [ -d "tests" ]; then
            SRC_DIR="src"
            TEST_DIR="tests"
          # 3) На случай старой структуры: qaops/qaops/src + qaops/qaops/tests
          elif [ -d "qaops/qaops/src" ] && [ -d "qaops/qaops/tests" ]; then
            SRC_DIR="qaops/qaops/src"
            TEST_DIR="qaops/qaops/tests"
          fi

          if [ -z "$SRC_DIR" ] || [ -z "$TEST_DIR" ]; then
            echo "ERROR: Не удалось найти каталоги src/tests автоматически."
            echo "Дерево каталогов (depth<=3):"
            find . -maxdepth 3 -type d -print
            exit 1
          fi

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
			pip install allure-pytest
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

          # Указываем src в PYTHONPATH — это позволит импортам вида: from utils.math import add
          export PYTHONPATH="${WORKSPACE}/${SRC_DIR}"
          echo "PYTHONPATH=$PYTHONPATH"

          # Запускаем ВСЕ тесты, без исключений
          pytest -q "${TEST_DIR}" --alluredir=allure-results --junitxml=report.xm
        '''
      }
      post {
        always {
			junit allowEmptyResults: true, testResults: 'report.xml'
			allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]

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
