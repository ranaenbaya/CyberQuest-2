# CyberQuest
A pixel-art cybersecurity educational game that teaches both offensive and defensive security skills through interactive lessons and quizzes.

---

## Stack
| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3 + Flask |
| Database | PostgreSQL (persistent Docker volume) |
| Password Hashing | bcrypt |

---

## Project Structure
```
cyberquest\
  app.py                  ← Main application (all game logic + content)
  requirements.txt        ← Python packages to install
  Dockerfile              ← Application container image
  docker-compose.yml      ← Application and PostgreSQL services
  templates\
    base.html             ← Shared page layout
    index.html            ← Login / Sign Up page
    stages.html           ← Stage selection
    lesson.html           ← Lesson slide viewer
    quiz.html             ← Multiple choice quiz
  static\
    css\
      style.css           ← All styling
    js\
      main.js             ← Shared util
      auth.js             ← Login / register logic
      stages.js           ← Stage grid
      lesson.js           ← Slide nav
      quiz.js             ← Quiz logic + results
    images\
      logo.png            ← CyberQuest logo
```

---

## Run with Docker Desktop on Windows

1. Install WSL2 from an elevated PowerShell prompt if it is not installed:

   ```powershell
   wsl --install
   ```

   Restart Windows if prompted.

2. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/). In Docker Desktop, enable **Use the WSL 2 based engine** under **Settings > General**. If you use a WSL distribution, enable it under **Settings > Resources > WSL Integration**.

3. Open PowerShell in the project folder, generate a session secret, and save it to the local `.env` file:

   ```powershell
   $secret = python -c "import secrets; print(secrets.token_hex(32))"
   $dbPassword = python -c "import secrets; print(secrets.token_hex(32))"
   @"
   SECRET_KEY=$secret
   POSTGRES_PASSWORD=$dbPassword
   "@ | Set-Content -Encoding ascii .env
   ```

4. Build and start the app and database:

   ```powershell
   docker compose up --build -d
   ```

5. Open **http://localhost:5000**. Check service status or view logs with `docker compose ps` and `docker compose logs -f`.

PostgreSQL data is stored in the named `postgres_data` volume, so it survives container replacement and normal redeploys. `docker compose down` preserves this volume; **do not** use `docker compose down --volumes` unless you intend to erase all accounts and progress. The generated hexadecimal database password is URL-safe. If you set `POSTGRES_PASSWORD` yourself, use URL-safe characters or URL-encode reserved characters because Compose builds the database connection URL from it. The default database password in Compose is for local development only.

The application creates the PostgreSQL tables automatically at startup. It requires `DATABASE_URL` and `SECRET_KEY`; when using Compose, the database URL is configured to connect to the `db` service. Existing data in a previous `cyberquest.db` SQLite file is not imported automatically.

For production, set a unique `SECRET_KEY` and strong PostgreSQL credentials, back up the PostgreSQL volume, and terminate TLS at a trusted web server or proxy. Session cookies are marked Secure, HttpOnly, and SameSite=Lax, so use HTTPS in production. The `/health` endpoint checks the application database and returns HTTP 503 if PostgreSQL is unavailable.

## Development Checks

Install development tools:

```powershell
python -m pip install -r requirements-dev.txt
```

Tests use a separate PostgreSQL database. Start one locally:

```powershell
docker run --rm --name cyberquest-test-db -e POSTGRES_DB=cyberquest_test -e POSTGRES_USER=cyberquest -e POSTGRES_PASSWORD=cyberquest-test-password -p 55432:5432 -d postgres:16-alpine
```

In PowerShell, set the test connection and run the checks:

```powershell
$env:TEST_DATABASE_URL = "postgresql://cyberquest:cyberquest-test-password@localhost:55432/cyberquest_test"
$env:SECRET_KEY = "pytest-only-secret"
ruff check app.py tests
pytest
bandit -r app.py -ll
```

Stop the test database afterward with `docker stop cyberquest-test-db`. GitHub Actions runs Ruff, pytest, Bandit, and a Trivy scan of the built image on pull requests and pushes to `main`. After checks pass, pushes to `main` publish `ghcr.io/<owner>/<repository>:latest` and a commit-specific `sha-<commit>` tag. Ensure GitHub Actions is allowed to write packages for the repository.

---

## Running It After First Setup

Start the services:

```
docker compose up -d
```

Stop the services without deleting saved progress:

```
docker compose down
```

To follow the app logs: `docker compose logs -f app`. Use `docker compose up --build -d` after changing the application code.

---

## Game Content

### ⚔️ Hacking Track
| Stage | Topic |
|---|---|
| 1 | Reconnaissance & OSINT |
| 2 | Phishing Attacks |
| 3 | Password Attacks |
| 4 | Network Scanning |

### 🛡️ Defence Track
| Stage | Topic |
|---|---|
| 1 | Password Security & MFA |
| 2 | Anti-Phishing |
| 3 | Network Defence |
| 4 | Incident Response |

Each stage has **6 lesson slides** followed by a **5-question quiz**.
Pass mark is **80%** (4/5 correct) to unlock the next stage.
Both paths are independent — you can play them in any order.

---

## Troubleshooting
| Problem | Fix |
|---|---|
| `docker` not found or daemon unavailable | Start Docker Desktop and ensure the WSL2 engine is enabled |
| `SECRET_KEY` is not set | Create `.env` as described above, or set `SECRET_KEY` in the shell before running Compose |
| App is unhealthy or won't start | Check `docker compose logs app db`; confirm the database health check succeeds |
| Port 5000 is already in use | Change the host side of the `ports` entry in `docker-compose.yml`, for example to `"5001:5000"`, and visit `localhost:5001` |
