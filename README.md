# CyberQuest

[![CI](https://github.com/ranaenbaya/CyberQuest-2/actions/workflows/ci.yml/badge.svg)](https://github.com/ranaenbaya/CyberQuest-2/actions/workflows/ci.yml)

A pixel-art cybersecurity educational platform that teaches offensive and defensive security through interactive lessons and quizzes. Choose Hacking or Defence, complete four stages per track, and unlock the next stage by scoring 80% or more. Accounts and progress are saved in PostgreSQL.

| Choose a stage | Learn | Test your knowledge | See your results |
|---|---|---|---|
| ![Stage selection](docs/screenshots/stages.png) | ![Lesson slide](docs/screenshots/lesson.png) | ![Quiz](docs/screenshots/quiz.png) | ![Results](docs/screenshots/results.png) |

## From group project to cloud deployment

CyberQuest began as a university project (Flask + SQLite). I extended it on my own to make it testable, containerised and deployable:

| Area | What I added |
|---|---|
| Database | Migrated SQLite to PostgreSQL with a persistent Docker volume, plus a `/health` endpoint that returns HTTP 503 when the database is down |
| Security | Secure, HttpOnly and SameSite=Lax session cookies, environment-based secrets, Bandit scanning |
| Testing | pytest tests for authentication, quiz scoring and stage progression, run against a real PostgreSQL database |
| Containers | Dockerfile and Docker Compose for the app and database |
| CI/CD | GitHub Actions running Ruff, pytest, Bandit and a Trivy image scan, then publishing images to GitHub Container Registry |
| Cloud | AWS EC2 deployment defined in Terraform: Gunicorn, Caddy HTTPS and automated first-boot setup |

## Architecture

```mermaid
flowchart LR
    Browser[Browser] -->|HTTPS| Caddy
    subgraph Instance["AWS EC2"]
        Caddy --> App[Flask + Gunicorn]
        App --> DB[(PostgreSQL)]
    end
    Actions[GitHub Actions] -->|Publish image| GHCR[GitHub Container Registry]
    GHCR -->|Pull on first boot| App
```

The AWS demo used Terraform to create an EC2 instance and security group. Only ports 80 and 443 were open (no SSH), the disk was encrypted, IMDSv2 was required, and secrets were generated per deployment. Caddy obtained an HTTPS certificate for an `sslip.io` hostname, which is needed because session cookies are marked `Secure`. It was deployed for a demonstration and then removed with `terraform destroy`.

## Tech stack

| Layer | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3, Flask, Gunicorn |
| Database & auth | PostgreSQL, bcrypt |
| DevOps & cloud | Docker, Docker Compose, GitHub Actions, GHCR, Terraform, AWS EC2, Caddy |
| Quality & security | pytest, Ruff, Bandit, Trivy |

## Gameplay

Each stage has six lesson slides and a five-question quiz. The two tracks progress independently.

| ⚔️ Hacking | 🛡️ Defence |
|---|---|
| 1. Reconnaissance & OSINT | 1. Password Security & MFA |
| 2. Phishing Attacks | 2. Anti-Phishing |
| 3. Password Attacks | 3. Network Defence |
| 4. Network Scanning | 4. Incident Response |

## Limitations and next steps

This was a single-instance demo, not a production deployment.

**Limitations**
- Lesson and quiz content lives in `app.py` rather than separate data files
- No automated backups or autoscaling
- Secrets exist in Terraform state and instance user data
- Deployment is not triggered automatically by CI
- Terraform used an admin-level IAM user

**Next steps**
- Move content into data files so new stages need no code changes
- Add more stages and progress features such as badges
- Move the database to RDS and secrets to AWS Secrets Manager
- Scope IAM down to least privilege and deploy automatically from CI

<details>
<summary><strong>Run locally: Docker Desktop on Windows</strong></summary>

1. If needed, install WSL 2 in an elevated PowerShell window with `wsl --install`, then restart.
2. Install Docker Desktop and enable **Use the WSL 2 based engine** in Settings → General.
3. In PowerShell, from the project folder, create `.env`:

   ```powershell
   $secret = python -c "import secrets; print(secrets.token_hex(32))"
   $dbPassword = python -c "import secrets; print(secrets.token_hex(32))"
   @"
   SECRET_KEY=$secret
   POSTGRES_PASSWORD=$dbPassword
   "@ | Set-Content -Encoding ascii .env
   ```

4. Start it:

   ```powershell
   docker compose up --build -d
   ```

5. Open http://localhost:5000.

```powershell
docker compose down          # Stop without deleting saved progress
docker compose logs -f app   # Follow app logs
```

Data lives in the `postgres_data` volume, so don't use `docker compose down --volumes` unless you want to erase accounts and progress. The app creates its tables on startup and needs `SECRET_KEY` and `DATABASE_URL` (Compose supplies the latter). Data from an old `cyberquest.db` SQLite file is not imported. Use URL-safe characters if you set `POSTGRES_PASSWORD` yourself. For production, use strong credentials, backups and HTTPS.

</details>

<details>
<summary><strong>Run tests and security checks</strong></summary>

```powershell
python -m pip install -r requirements-dev.txt

docker run --rm --name cyberquest-test-db -e POSTGRES_DB=cyberquest_test -e POSTGRES_USER=cyberquest -e POSTGRES_PASSWORD=cyberquest-test-password -p 55432:5432 -d postgres:16-alpine

$env:TEST_DATABASE_URL = "postgresql://cyberquest:cyberquest-test-password@localhost:55432/cyberquest_test"
$env:SECRET_KEY = "pytest-only-secret"

ruff check app.py tests
pytest
bandit -r app.py -ll

docker stop cyberquest-test-db
```

GitHub Actions runs Ruff, pytest, Bandit and a Trivy scan on pull requests and pushes to `main`. Successful `main` builds publish `ghcr.io/ranaenbaya/cyberquest-2:latest` and a `sha-<commit>` tag.

</details>

<details>
<summary><strong>Deploy the demo to AWS</strong></summary>

Requires an AWS account, the AWS CLI configured, Terraform 1.6+ and a public GHCR image. The region is set in `infra/variables.tf` (the demo used `eu-north-1`).

```powershell
cd infra
terraform init
terraform apply
```

Wait about five minutes for first-boot setup, then open the `site_url` output. Remove everything with `terraform destroy`.

**Cost warning:** AWS resources can incur charges until destroyed. **Protect Terraform state:** it can contain generated secrets.

</details>

<details>
<summary><strong>Project structure</strong></summary>

```text
app.py                    Flask application, game logic and content
requirements.txt          Runtime dependencies
requirements-dev.txt      Development and test dependencies
Dockerfile                Application image
docker-compose.yml        Application and PostgreSQL services
.github/workflows/ci.yml  CI, scans and image publishing
tests/                    Automated tests
infra/                    Terraform and first-boot configuration
templates/                HTML pages
static/                   CSS, JavaScript and images
docs/screenshots/         README screenshots
```

</details>

<details>
<summary><strong>Troubleshooting</strong></summary>

| Problem | Fix |
|---|---|
| Docker command missing or daemon unavailable | Start Docker Desktop and enable the WSL 2 engine |
| `SECRET_KEY` not set | Create `.env` as above |
| App won't start | Run `docker compose logs app db` |
| Port 5000 in use | Change the host port, e.g. `"5001:5000"` |
| Login fails on AWS | Use the HTTPS URL, since cookies are `Secure` |
| Terraform "explicit deny" | The account may restrict regions, so set an allowed `region` |

</details>