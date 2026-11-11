# Tikaa – DevSecOps Security Assessment

## Project
Tikaa – Child Immunisation Planner

## Security tools
- Bandit – Python source code analysis
- pip-audit – Python dependency vulnerability audit
- Gitleaks – Secret detection
- Trivy – Container image vulnerability scan

## Scan results

| Security check | Findings |
|---|---:|
| Bandit source findings | 0 |
| Dependency vulnerabilities | 0 |
| Gitleaks secret findings | 0 |
| Trivy image vulnerabilities | 234 |
| Trivy HIGH | 58 |
| Trivy CRITICAL | 0 |

## Remediation
- Flask was upgraded from 3.0.3 to 3.1.3 after pip-audit identified a vulnerability.
- The dependency scan was rerun and returned no known vulnerabilities.
- The Flask development server binding was restricted to localhost.
- The Dockerfile retains its non-root application user.

## DevSecOps workflow
Source Code → Bandit → pip-audit → Gitleaks → Docker Build → Trivy → Security Reports

## Conclusion
Security checks are integrated into a separate Jenkins pipeline.
The pipeline is independent of the existing CI/CD and Blue-Green deployment activities.
No Kubernetes deployment or traffic switching is performed by this security pipeline.

## Evidence
Raw JSON reports are stored in the security-reports directory.

## Security Gate Policy

The independent Jenkins pipeline enforces:
- Bandit findings: fail the pipeline
- Dependency vulnerabilities: fail the pipeline
- Gitleaks findings: fail the pipeline
- HIGH or CRITICAL container vulnerabilities: fail the pipeline

Reports are archived after every build, including failed security builds.
The pipeline does not deploy to Kubernetes or change Blue-Green traffic.
