# QA Ops Exam Project

This repository is a small Python HTTP service used for hands-on QA Ops interviews. It has a real test suite, Docker image, and Jenkins pipeline. Candidates use actual Git, Jenkins, and Docker; there is no command simulator.

## Run and test locally

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
python -m app
```

The API listens on http://localhost:5000. Check `GET /health` and `POST /api/sum` with a JSON body such as `{"a": 7, "b": 5}`.

## Build and run the Docker image

```powershell
docker build -t qaops-api:local .
docker run --rm -p 5000:5000 -e QAOPS_ENV=test qaops-api:local
```

## Start the local Jenkins instance

Docker Compose starts a Jenkins controller with Python and the Pipeline/Git plugins. Jenkins does not mount the host Docker socket.

```powershell
docker compose --profile ci up --build -d jenkins
docker compose --profile ci logs -f jenkins
docker compose --profile ci exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080, finish the Jenkins setup wizard, and create a Pipeline job from SCM:

- Repository: `https://github.com/ak-stacy/qaops.git`
- Branch for the Jenkinsfile: `exam`
- Script path: `Jenkinsfile`

Build parameters are defined in the Jenkinsfile: source branch, action, environment, and test suite. For the first regression run, use `feature/autotests`.

## Candidate Git workflow

The assessor selects the task branch and gives the candidate a name for their work branch. Candidates need write access to this repository.

```powershell
git clone https://github.com/ak-stacy/qaops.git
cd qaops
git switch feature/autotests
git switch -c candidate/<name>
```

For the first task, add your surname on a new line in `exam.txt`. The assessor may also assign these branches for focused exercises:

- `exercise/deploy-fails`
- `exercise/dockerfile-broken`
- `exercise/container-exits`
- `exercise/add-runtime-dependency`
- `exercise/merge-candidate` and `exercise/merge-upstream`

After fixing the issue:

```powershell
python -m pytest
git add .
git commit -m "Fix QA Ops regression"
git push -u origin candidate/<name>
```

Open a pull request from `candidate/<name>` to `exam`. In Jenkins, run the pipeline again with `SOURCE_BRANCH=candidate/<name>`.

## Reset Jenkins

Stop the local Jenkins container with `docker compose --profile ci down`. The named `jenkins_home` volume is retained so jobs and configuration survive a restart.
