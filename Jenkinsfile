pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        string(
            name: 'SOURCE_BRANCH',
            defaultValue: 'feature/autotests',
            description: 'Branch to check out from the QA Ops repository'
        )
        choice(
            name: 'ACTION',
            choices: ['regression', 'deploy', 'post-deploy'],
            description: 'Run regression tests, deploy the test app, or deploy and test it'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['test', 'dev', 'stage'],
            description: 'Target test environment'
        )
        choice(
            name: 'TEST_SUITE',
            choices: ['all', 'unit', 'api'],
            description: 'Test group for regression runs'
        )
    }

    environment {
        DEPLOY_PORT = '5001'
        REPOSITORY_URL = 'https://github.com/ak-stacy/qaops.git'
    }

    stages {
        stage('Checkout source branch') {
            steps {
                deleteDir()
                git branch: params.SOURCE_BRANCH, url: env.REPOSITORY_URL
                sh 'git status --short --branch'
            }
        }

        stage('Prepare Python environment') {
            steps {
                sh '''
                    set -eu
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Deploy test environment') {
            when {
                expression { params.ACTION in ['deploy', 'post-deploy'] }
            }
            steps {
                sh '''
                    set -eu
                    if [ -f .qaops-app.pid ]; then
                        old_pid=$(cat .qaops-app.pid)
                        if kill -0 "$old_pid" 2>/dev/null; then
                            kill "$old_pid"
                        fi
                        rm -f .qaops-app.pid
                    fi

                    JENKINS_NODE_COOKIE=dontKillMe BUILD_ID=dontKillMe \
                        nohup env \
                            QAOPS_ENV="$ENVIRONMENT" \
                            PORT="$DEPLOY_PORT" \
                            PYTHONPATH="$WORKSPACE/src" \
                            "$WORKSPACE/.venv/bin/python" -m app \
                            > deploy.log 2>&1 < /dev/null &
                    echo $! > .qaops-app.pid

                    for attempt in $(seq 1 20); do
                        if curl --fail --silent "http://127.0.0.1:$DEPLOY_PORT/healthz" > /dev/null; then
                            echo "Application deployed to $ENVIRONMENT and responding on port $DEPLOY_PORT."
                            exit 0
                        fi
                        sleep 1
                    done

                    cat deploy.log
                    echo "ERROR: deployed application did not become healthy."
                    exit 1
                '''
            }
        }

        stage('Verify deployed environment') {
            when {
                expression { params.ACTION in ['deploy', 'post-deploy'] }
            }
            steps {
                sh '''
                    QAOPS_ENV="$ENVIRONMENT" .venv/bin/python -c '
                    import json
                    import os
                    from urllib.request import urlopen

                    with urlopen("http://127.0.0.1:5001/health", timeout=5) as response:
                        health = json.loads(response.read())
                    assert health["status"] == "ok", health
                    assert health["environment"] == os.environ["QAOPS_ENV"], health
                    print(health)
                    '
                '''
            }
        }

        stage('Run autotests') {
            when {
                expression { params.ACTION in ['regression', 'post-deploy'] }
            }
            steps {
                sh '''
                    set -eu
                    mkdir -p reports

                    if [ "$ACTION" = "post-deploy" ]; then
                        QAOPS_BASE_URL="http://127.0.0.1:$DEPLOY_PORT" \
                            .venv/bin/python -m pytest tests \
                            --junitxml=reports/junit.xml
                    else
                        case "$TEST_SUITE" in
                            unit) test_path=tests/test_math.py ;;
                            api) test_path=tests/test_api.py ;;
                            all) test_path=tests ;;
                            *) echo "Unsupported test suite: $TEST_SUITE"; exit 2 ;;
                        esac
                        .venv/bin/python -m pytest "$test_path" \
                            --junitxml=reports/junit.xml
                    fi
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'
            archiveArtifacts allowEmptyArchive: true,
                artifacts: 'reports/junit.xml,deploy.log'
            sh(script: '''
                if [ -f .qaops-app.pid ]; then
                    app_pid=$(cat .qaops-app.pid)
                    if kill -0 "$app_pid" 2>/dev/null; then
                        kill "$app_pid"
                    fi
                    rm -f .qaops-app.pid
                fi
            ''', returnStatus: true)
        }
    }
}
