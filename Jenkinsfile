pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
    ansiColor('xterm')
  }

  environment {
    // Делаем так, чтобы Python видел модули из qaops/src
    PYTHONPATH = "${WORKSPACE}/qaops/src"
  }

  stages {
    stage('Set up Python') {
      steps {
        sh '''
          python -V
          python -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt
          else
            # Минимально необходимое для запуска
            pip install pytest
          fi
        '''
      }
    }

    stage('Run tests') {
      steps {
        sh '''
          . venv/bin/activate
          # Запускаем ВСЕ тесты из qaops/tests, без исключений
          pytest -q qaops/tests --junitxml=report.xml
        '''
      }
      post {
        always {
          // Публикуем JUnit-отчёт даже если тесты упали
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
