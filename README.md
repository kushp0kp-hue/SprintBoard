# SprintBoard

SprintBoard is a lightweight Jira/Trello-style issue tracker built as a **pure software engineering portfolio project**. It focuses on API design, relational data modeling, clean architecture, validation, testing, and CI rather than flashy algorithms.

## What it does

- Create projects
- Create and update issues
- Kanban-style status workflow: To Do / In Progress / Blocked / Done
- Priorities and assignees
- Many-to-many labels
- Issue comments
- Search issue titles/descriptions
- Filter by status and priority
- SQLite persistence
- API tests
- GitHub Actions CI

## Tech stack

- Python
- Flask
- SQLite
- HTML/CSS/JavaScript
- unittest
- GitHub Actions

## Architecture

```text
Browser
   |
   v
Flask Routes          app/routes.py
   |
   v
Service Layer         app/services.py
   |
   v
Repository Layer      app/repositories.py
   |
   v
SQLite                app/database.py
```

### Why separate the layers?

**Routes** handle HTTP requests and responses.

**Services** handle business rules and validation.

**Repositories** handle SQL and persistence.

That keeps HTTP logic, business logic, and database logic from becoming one giant file.

## Database model

```text
projects
   |
   | one-to-many
   v
issues -------- issue_labels -------- labels
   |
   | one-to-many
   v
comments
```

`issue_labels` is a join table because issues and labels have a many-to-many relationship.

## REST API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/projects` | List projects |
| POST | `/api/projects` | Create project |
| DELETE | `/api/projects/:id` | Delete project |
| GET | `/api/projects/:id/issues` | List/filter issues |
| POST | `/api/projects/:id/issues` | Create issue |
| GET | `/api/issues/:id` | Get one issue |
| PATCH | `/api/issues/:id` | Update issue |
| DELETE | `/api/issues/:id` | Delete issue |
| POST | `/api/issues/:id/comments` | Add comment |

Example filter:

```text
GET /api/projects/1/issues?status=in_progress&priority=high&q=api
```

## Engineering decisions

### Parameterized SQL

Queries use placeholders instead of concatenating user input, which prevents SQL injection.

### Validation layer

Valid statuses and priorities are enforced in the service layer before data reaches the database.

### Database indexes

Indexes are included on fields commonly used for lookups and filtering: `project_id`, `status`, `priority`, and comment `issue_id`.

### SQLite

SQLite keeps local setup simple while still demonstrating relational database concepts. A production version could move to PostgreSQL without changing the HTTP API.

### Automated tests

The API tests cover:

- issue creation
- filtering
- updates
- invalid input
- comments
- deletion

GitHub Actions runs those tests on every push and pull request.

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/SprintBoard.git
cd SprintBoard
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Interview explanation

> SprintBoard is a lightweight Jira-style issue tracker I built with Flask and SQLite. I designed it as a layered application where routes handle HTTP, services handle validation and business rules, and repositories handle database access. I modeled projects, issues, labels, and comments relationally, including a many-to-many join table for labels. I also implemented search/filtering, RESTful status codes, parameterized SQL, API tests, and a GitHub Actions CI workflow.

## Things I would add next

- Authentication and user accounts
- Pagination
- Due dates
- Audit/activity history
- PostgreSQL
- Docker
- Deployment
- WebSocket live updates
