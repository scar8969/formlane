<p align="center">
  <img src="docs/assets/screens/root.png" alt="formlane running" width="900">
</p>

<h1 align="center">formlane</h1>

<p align="center"><b>A backend for HTML forms: create one, get a POST endpoint, collect submissions.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/formlane/actions/workflows/ci.yml"><img src="https://github.com/scar8969/formlane/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-60.0%-yellow" alt="coverage: 60.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20live-0969da" alt="routes: 10 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

formlane gives a static page a real form backend: create a form, point the HTML at its endpoint, and read submissions as JSON or CSV. Honeypot and keyword checks drop the obvious spam, and delivery to email or a webhook is configured per form.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Static sites still need forms, and the hosted options own your data. This is the small piece in between: one table for forms, one for submissions, a spam filter that runs before the insert, and an export that is a query.

## What it does

| Capability | How it works |
| --- | --- |
| **Form definitions** | Name, target delivery and spam rules per form; the token in the URL is the endpoint. |
| **Submission capture** | Any POST to /f/<token> is validated, filtered and stored with its headers. |
| **Spam filter** | A honeypot field plus keyword rules, both configurable per form. |
| **Delivery config** | Email and webhook targets are stored per form and serialised for the sender. |
| **Export** | Submissions as JSON or CSV for a spreadsheet. |

## Quickstart

```sh
git clone https://github.com/scar8969/formlane.git
cd formlane
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/forms
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/forms-new.png" alt="/forms/new" width="100%"><br><sub><code>/forms/new</code> &middot; 31.8 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/submissions.png" alt="/submissions" width="100%"><br><sub><code>/submissions</code> &middot; 21.0 KB</sub></td>
</tr>
</table>

The other 5 captures — the health, liveness, readiness, metrics and version endpoints — are committed in the same folder rather than shown here.

## API

Every route below is declared in [`openapi/formlane.yaml`](openapi/formlane.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/f/<token>` | submit |
| `GET` | `/api/forms` | list |
| `POST` | `/api/forms` | create |
| `GET` | `/api/forms/<id>/submissions` | submissions |

## CLI

The same operations without an HTTP client. Installed as `formlane`, and runnable from a checkout with no install:

```sh
python -m formbackend.cli --help
```

```text
usage: formbackend [-h] command ...

Form backend CLI

positional arguments:
  command
    forms        list forms with submission counts
    create       create a form endpoint
    submissions  show recent submissions for a form
    test         post a sample submission to a form token
    serve        run the development server

options:
  -h, --help     show this help message and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |
| `FORMBACKEND_SECRET_KEY` | `formbackend-local` | Flask session key; set it in production. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (1.5 s, exit 0) |
| Line coverage | **60.0%** — 448 of 717 statements |
| Source | 15 files / 1,561 lines |
| Test code | 4 files / 263 lines |
| Documented paths | 3 in the spec, 2 GET |
| Live probe | 11 GET requests to the booted app, **10 answered 200** |
| Median latency | **5.3 ms** (single uncached request, dev server) |
| Slowest / fastest | 109.9 ms `/` / 3.1 ms `/readyz` |
| Bytes served | 17.9 KB across 11 responses |
| Screenshots | 8 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ formbackend/app.py:get_app()
                │  reads config once (formbackend/config.py)
                │  registers the `forms` blueprint
                ▼
           route handler
             ├──▶ formbackend/models.py        tables, via Flask-SQLAlchemy
             ├──▶ formbackend/errors.py        raises typed errors → one JSON envelope
             └──▶ formbackend/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
formlane/
├── src/formbackend/
│   ├── http.py                         379  HTTP plumbing for formbackend: correlation ids, acce
│   ├── cli.py                          200  Command line front-end for the form backend
│   ├── config.py                       172  Environment-driven configuration for formbackend
│   ├── observability.py                169  Structured logging and request correlation for formb
│   ├── _app.py                         142  
│   ├── app.py                          119  Application factory for formbackend
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── forms/api.py                     85  
│   ├── forms/deliver.py                 61  
│   ├── paths.py                         52  Filesystem layout for formbackend
│   ├── forms/spam.py                    29  
│   ├── models.py                        27  
├── openapi/formlane.yaml                  the contract of record
├── schema/formlane.sql                    the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `forms/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t formlane .
docker run --rm -p 8000:8000 --env-file .env.example formlane
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- The webhook sender is implemented and unit-tested but the submit path does not call it yet — the README says so rather than implying otherwise.
- No file uploads on form submissions.

## License

MIT — see [LICENSE](LICENSE).
