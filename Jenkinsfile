pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'test', 'stage', 'prod'],
            description: 'Выберите окружение для запуска тестов'
        )
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

        stage('Show Environment') {
            steps {
                echo "Selected environment: ${params.ENVIRONMENT}"
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
                    find . -maxdepth 3 \\( -name src -o -name tests \\) -type d | sed 's|^./||' || true

                    SRC_DIR=""
                    TEST_DIR=""

                    if [ -d "qaops/src" ] && [ -d "qaops/tests" ]; then
                        SRC_DIR="qaops/src"
                        TEST_DIR="qaops/tests"
                    elif [ -d "src" ] && [ -d "tests" ]; then
                        SRC_DIR="src"
                        TEST_DIR="tests"
                    elif [ -d "qaops/qaops/src" ] && [ -d "qaops/qaops/tests" ]; then
                        SRC_DIR="qaops/qaops/src"
                        TEST_DIR="qaops/qaops/tests"
                    fi

                    if [ -z "$SRC_DIR" ] || [ -z "$TEST_DIR" ]; then
                        echo "ERROR: Не удалось найти каталоги src/tests автоматически."
                        find . -maxdepth 3 -type d -print
                        exit 1
                    fi

                    {
                        echo "SRC_DIR=$SRC_DIR"
                        echo "TEST_DIR=$TEST_DIR"
                    } > .paths

                    cat .paths
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
                    fi

                    pip install pytest allure-pytest
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    set -e

                    . ./.paths
                    . venv/bin/activate

                    export PYTHONPATH="${WORKSPACE}/${SRC_DIR}"
                    export TEST_ENV="${ENVIRONMENT}"

                    echo "PYTHONPATH=$PYTHONPATH"
                    echo "TEST_ENV=$TEST_ENV"

                    pytest \
                        -q "${TEST_DIR}" \
                        --alluredir=allure-results \
                        --junitxml=report.xml
                '''
            }

            post {
                always {
                    junit allowEmptyResults: true,
                          testResults: 'report.xml'

                    allure(
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'allure-results']]
                    )
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'report.xml',
                fingerprint: true,
                onlyIfSuccessful