import sqlite3
from pathlib import Path
from flask import current_app, g

SCHEMA = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'todo',
    priority TEXT NOT NULL DEFAULT 'medium',
    assignee TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS issue_labels (
    issue_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    PRIMARY KEY (issue_id, label_id),
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_issues_project_id ON issues(project_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_priority ON issues(priority);
CREATE INDEX IF NOT EXISTS idx_comments_issue_id ON comments(issue_id);
'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    db_path = Path(app.config['DATABASE'])
    if not db_path.is_absolute():
        db_path = Path(app.root_path).parent / db_path
        app.config['DATABASE'] = str(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(app.config['DATABASE']) as db:
        db.executescript(SCHEMA)
        db.commit()
        count = db.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
        if count == 0 and not app.config.get('TESTING'):
            project_id = db.execute(
                'INSERT INTO projects (name, description) VALUES (?, ?)',
                ('SprintBoard Demo', 'Example project for trying the issue tracker.')
            ).lastrowid
            db.execute(
                '''INSERT INTO issues
                (project_id, title, description, status, priority, assignee)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (project_id, 'Build issue filtering', 'Support status, priority, assignee, and text search.', 'in_progress', 'high', 'Kush')
            )
            db.commit()
    app.teardown_appcontext(close_db)
