# Tikaa — CI/CD, Blue-Green Deployment & DevSecOps on Kubernetes

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/k3s-FFC61C?style=for-the-badge&logo=k3s&logoColor=black)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)
![Trivy](https://img.shields.io/badge/Trivy-1904DA?style=for-the-badge&logo=aqua&logoColor=white)

**Tikaa** is a small Flask web app (a child vaccination schedule planner for India) used as the workload for a
DevOps project-based-learning exercise. The interesting part is the delivery pipeline around it:
three independent Jenkins pipelines that build, deploy, release and security-scan the app on a k3s Kubernetes cluster.

## Pipelines

| Pipeline | What it does |
|---|---|
| [`Jenkinsfile`](Jenkinsfile) | **CI/CD** — run the tests, build the Docker image, import it into k3s, roll it out to the `tikaa` Deployment and wait for the rollout |
| [`Jenkinsfile.bluegreen`](Jenkinsfile.bluegreen) | **Blue-green release** — detect the live colour from the Service selector, deploy the other colour (2 replicas, readiness probe on `/health`), test it in-cluster, switch Service traffic, and **automatically roll back** if the live health check fails |
| [`Jenkinsfile.security`](Jenkinsfile.security) | **DevSecOps scan** — Bandit (code), pip-audit (dependencies), Gitleaks (secrets) and Trivy (container image). Bandit, pip-audit and Gitleaks fail the build on findings; all reports are archived. Does not deploy or touch traffic |

```
Source ─► Bandit ─► pip-audit ─► Gitleaks ─► Docker build ─► Trivy ─► security-reports/
                                                  │
                                                  └─► k3s: tikaa-blue ⇄ tikaa-green ─► Service (NodePort 30080)
```

## Security results

See [`security-reports/SECURITY-REPORT.md`](security-reports/SECURITY-REPORT.md). Highlights:
- pip-audit flagged Flask 3.0.3 → upgraded to **3.1.3**, rescan clean
- Bandit: 0 findings · Gitleaks: 0 secrets
- Container runs as a **non-root** user; dev server bound to localhost (gunicorn serves in the container)

## App endpoints

| Route | Response |
|---|---|
| `/` | Tikaa web page (shows the release version and colour) |
| `/health` | `{"status": "ok", "version": ..., "color": ...}` — used by readiness probes and the blue-green switch |

`APP_VERSION` and `APP_COLOR` environment variables identify the running release.

## Run locally

With Docker:

```bash
docker build -t tikaa .
docker run -p 5000:5000 -e APP_COLOR=blue tikaa
# open http://localhost:5000  and  http://localhost:5000/health
```

Without Docker:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest                # 2 tests: /health payload and the home page
python app.py         # http://127.0.0.1:5000
```

## Blue-green: one-time setup

The blue-green pipeline needs a live blue release and a Service that selects by colour. On the k3s host:

```bash
docker build -t tikaa:bootstrap .
docker save tikaa:bootstrap | sudo k3s ctr images import -
kubectl apply -f k8s/tikaa-blue.yaml -f k8s/service-bluegreen.yaml
kubectl rollout status deployment/tikaa-blue
curl http://localhost:30080/health      # {"color": "blue", ...}
```

After that, each run of `Jenkinsfile.bluegreen` deploys the idle colour, tests it inside the cluster, moves the Service to it, and rolls back if the live health check fails.

`Jenkinsfile` and `Jenkinsfile.bluegreen` are two alternative release strategies for the same `tikaa` Service on NodePort 30080. Use one at a time: applying `k8s/deployment.yaml` resets the Service selector to `app: tikaa`.

## Repository layout

```
app.py                     Flask app (/ and /health)
templates/index.html       Tikaa UI
Dockerfile                 python:3.12-slim, gunicorn, non-root user
tests/test_app.py          pytest tests for both routes
k8s/deployment.yaml        Deployment + Service used by the CI/CD pipeline
k8s/tikaa-blue.yaml        Initial blue Deployment for the blue-green flow
k8s/service-bluegreen.yaml Colour-selecting Service for the blue-green flow
Jenkinsfile*               The three pipelines above
security-reports/          Assessment report (raw JSON reports are git-ignored)
```
