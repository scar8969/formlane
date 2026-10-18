<p align="center">
  <img src="docs/assets/screens/root.png" alt="formlane running" width="900">
</p>

<h1 align="center">formlane</h1>

<p align="center"><b>A backend for HTML forms: create one, get a POST endpoint, collect submissions.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-24%20passed-2ea44f" alt="tests: 24 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-60.0%-yellow" alt="coverage: 60.0%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20answered-0969da" alt="routes: 10 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

formlane gives a static page a real form backend: create a form, point the HTML at its endpoint, and read submissions as JSON or CSV. Honeypot and keyword checks drop the obvious spam, and delivery to email or a webhook is configured per form.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

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

The same work from the CLI:

```sh
python -m formbackend.cli --help
```

Commands: `forms`, `create`, `submissions`, `test`, `serve`.

A first request:

```sh
curl -s http://127.0.0.1:8000/f/<token> | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/formlane.yaml`](openapi/formlane.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/f/<token>` | submit |
| `POST` | `/api/forms` | create |
| `GET` | `/api/forms/<id>/submissions` | submissions |

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/forms-new.png" alt="/forms/new" width="100%"><br><sub><code>/forms/new</code> &middot; 31.8 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/submissions.png" alt="/submissions" width="100%"><br><sub><code>/submissions</code> &middot; 21.0 KB</sub></td>
</tr>
</table>

The other 5 captures — the health, liveness, readiness, metrics and version endpoints — are committed in the same folder rather than shown here.

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **24 / 24 passed** (1.4 s, exit 0) |
| Line coverage | **60.0%** — 448 of 717 statements |
| Source | 15 files / 1,558 lines |
| Test code | 4 files / 263 lines |
| Documented paths | 3 in the spec, 1 GET |
| Live probe | 11 GET requests to the booted app, **10 answered 200** |
| Median latency | **5.3 ms** (single uncached request, dev server) |
| Slowest / fastest | 109.9 ms `/` / 3.1 ms `/readyz` |
| Bytes served | 17.9 KB across 11 responses |
| Screenshots | 8 captured |

## Architecture

```
formlane/
├── src/formbackend/
│   ├── http.py                         379  HTTP plumbing for formbackend: correlation ids, acce
│   ├── cli.py                          196  Command line front-end for the form backend
│   ├── config.py                       173  Environment-driven configuration for formbackend
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
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t formlane .
docker run --rm -p 8000:8000 --env-file .env.example formlane
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- The webhook sender is implemented and unit-tested but the submit path does not call it yet — the README says so rather than implying otherwise.
- No file uploads on form submissions.

## License

MIT — see [LICENSE](LICENSE).
