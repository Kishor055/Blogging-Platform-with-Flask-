# BlogSphere Deployment Guide

## Configuration

Set these values in the deployment secret manager or `.env` file:

- `SECRET_KEY`: long, random, private value; required in production.
- `APP_ENV=production`: selects secure production configuration.
- `DATABASE_URL`: SQLAlchemy URL, preferably `postgresql+psycopg://...`.
- `UPLOAD_FOLDER`: persistent writable media directory.
- `POSTGRES_PASSWORD`: URL-safe database password for the included Compose service (random hex is suitable because Compose inserts it into the SQLAlchemy URL).

Never commit `.env` or production credentials. Keep HTTPS enabled so secure session cookies are sent only over TLS.
The repository ignores `.env` variants (except the committed `.env.example` template), local secrets directories, and common private-key files.

## Docker Compose

1. Copy `.env.example` to `.env`.
2. Set a random `SECRET_KEY` and strong `POSTGRES_PASSWORD`.
3. Build and launch:

   ```powershell
   docker compose up --build -d
   ```

4. Follow startup logs with `docker compose logs -f web`.
5. Check `http://localhost:8000/health`.
6. Create the first admin with `docker compose exec web flask --app run.py create-admin`.

Compose starts PostgreSQL with a health check, mounts durable database and upload volumes, applies committed Alembic migrations, then starts Gunicorn. Back up the database volume and uploads volume independently.

Scheduled posts require a recurring job; the web app does not start an in-process scheduler. Invoke the idempotent publisher every minute using a platform scheduler or host cron, for example:

```sh
docker compose exec -T web flask --app run.py publish-scheduled
```

Run the command from the Compose project directory and monitor its exit status/log output. It publishes only due posts and can safely be retried after a failure.

The Compose setup is provided but was not validated or built in the development environment because Docker CLI is unavailable there.

## Manual Gunicorn deployment

Install dependencies, configure environment variables (including `APP_ENV=production`), and run migrations:

```powershell
python -m pip install -r requirements.txt
$env:FLASK_APP = "run.py"
flask db upgrade
gunicorn --bind 0.0.0.0:8000 --workers 2 --access-logfile - wsgi:app
```

On Windows, Gunicorn is not the supported local WSGI server; use `flask run` for local development and deploy Gunicorn on Linux or in the supplied Linux container.

## Migration workflow

When models change, create and review a migration before deploying:

```powershell
flask --app run.py db migrate -m "Describe schema update"
flask --app run.py db upgrade
```

Commit the generated migration script. Production startup runs `db upgrade` before Gunicorn starts.

## Production checklist

- [ ] Set unique production secrets and verify `SECRET_KEY` is present.
- [ ] Use PostgreSQL and persistent media storage.
- [ ] Terminate TLS at a trusted reverse proxy and forward HTTPS metadata safely.
- [ ] Restrict inbound database access; expose only the web service.
- [ ] Apply reviewed migrations and verify database backups/restores.
- [ ] Configure log collection, monitoring, rate limits, and resource sizing.
- [ ] Review CDN policy or self-host Bootstrap, Quill, and fonts.
- [ ] Run the test suite against the release candidate.
- [ ] Create the first administrator using the CLI.
- [ ] Confirm uploads and `/health` work after restart.

## Troubleshooting

- **Missing migration table/schema:** run `flask --app run.py db upgrade`.
- **Production refuses to start:** set `SECRET_KEY`; startup intentionally fails without it.
- **Database connection errors:** verify `DATABASE_URL`, DNS/service name, credentials, and PostgreSQL readiness.
- **Upload errors after restart:** verify `UPLOAD_FOLDER` exists, is writable, and backed by persistent storage.
- **Compose cannot read `.env`:** copy `.env.example` to `.env` and set both required secrets.
- **Static/CDN resources missing:** check outbound network policy or vendor the assets locally.
