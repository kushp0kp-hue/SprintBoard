from .database import get_db


class ProjectRepository:
    @staticmethod
    def list_all():
        rows = get_db().execute(
            'SELECT id, name, description, created_at FROM projects ORDER BY id DESC'
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def create(name, description=''):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO projects (name, description) VALUES (?, ?)',
            (name, description),
        )
        db.commit()
        return ProjectRepository.get(cursor.lastrowid)

    @staticmethod
    def get(project_id):
        row = get_db().execute(
            'SELECT id, name, description, created_at FROM projects WHERE id = ?',
            (project_id,),
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete(project_id):
        db = get_db()
        cursor = db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        db.commit()
        return cursor.rowcount > 0


class IssueRepository:
    @staticmethod
    def create(project_id, data):
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO issues
            (project_id, title, description, status, priority, assignee)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                project_id,
                data['title'],
                data.get('description', ''),
                data.get('status', 'todo'),
                data.get('priority', 'medium'),
                data.get('assignee', ''),
            ),
        )
        issue_id = cursor.lastrowid
        IssueRepository.replace_labels(issue_id, data.get('labels', []), commit=False)
        db.commit()
        return IssueRepository.get(issue_id)

    @staticmethod
    def get(issue_id):
        row = get_db().execute(
            '''SELECT id, project_id, title, description, status, priority,
                      assignee, created_at, updated_at
               FROM issues WHERE id = ?''',
            (issue_id,),
        ).fetchone()
        if not row:
            return None
        issue = dict(row)
        issue['labels'] = IssueRepository.labels(issue_id)
        issue['comments'] = CommentRepository.list_for_issue(issue_id)
        return issue

    @staticmethod
    def list_for_project(project_id, filters=None):
        filters = filters or {}
        query = '''
            SELECT id, project_id, title, description, status, priority,
                   assignee, created_at, updated_at
            FROM issues WHERE project_id = ?
        '''
        params = [project_id]

        if filters.get('status'):
            query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('priority'):
            query += ' AND priority = ?'
            params.append(filters['priority'])
        if filters.get('assignee'):
            query += ' AND assignee = ?'
            params.append(filters['assignee'])
        if filters.get('q'):
            query += ' AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)'
            term = f"%{filters['q'].lower()}%"
            params.extend([term, term])

        query += '''
            ORDER BY CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5 END,
                updated_at DESC, id DESC
        '''

        rows = get_db().execute(query, tuple(params)).fetchall()
        result = []
        for row in rows:
            issue = dict(row)
            issue['labels'] = IssueRepository.labels(issue['id'])
            result.append(issue)
        return result

    @staticmethod
    def update(issue_id, updates):
        allowed = {'title', 'description', 'status', 'priority', 'assignee'}
        fields = []
        params = []
        for key, value in updates.items():
            if key in allowed:
                fields.append(f'{key} = ?')
                params.append(value)

        db = get_db()
        if fields:
            fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(issue_id)
            db.execute(f"UPDATE issues SET {', '.join(fields)} WHERE id = ?", tuple(params))

        if 'labels' in updates:
            IssueRepository.replace_labels(issue_id, updates['labels'], commit=False)

        db.commit()
        return IssueRepository.get(issue_id)

    @staticmethod
    def delete(issue_id):
        db = get_db()
        cursor = db.execute('DELETE FROM issues WHERE id = ?', (issue_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def labels(issue_id):
        rows = get_db().execute(
            '''SELECT l.name FROM labels l
               JOIN issue_labels il ON il.label_id = l.id
               WHERE il.issue_id = ? ORDER BY l.name''',
            (issue_id,),
        ).fetchall()
        return [row['name'] for row in rows]

    @staticmethod
    def replace_labels(issue_id, labels, commit=True):
        db = get_db()
        normalized = sorted({label.strip().lower() for label in labels if label.strip()})
        db.execute('DELETE FROM issue_labels WHERE issue_id = ?', (issue_id,))
        for name in normalized:
            db.execute('INSERT OR IGNORE INTO labels (name) VALUES (?)', (name,))
            label_id = db.execute('SELECT id FROM labels WHERE name = ?', (name,)).fetchone()['id']
            db.execute('INSERT INTO issue_labels (issue_id, label_id) VALUES (?, ?)', (issue_id, label_id))
        if commit:
            db.commit()


class CommentRepository:
    @staticmethod
    def list_for_issue(issue_id):
        rows = get_db().execute(
            '''SELECT id, issue_id, author, body, created_at
               FROM comments WHERE issue_id = ? ORDER BY id ASC''',
            (issue_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def create(issue_id, author, body):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO comments (issue_id, author, body) VALUES (?, ?, ?)',
            (issue_id, author, body),
        )
        db.execute('UPDATE issues SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (issue_id,))
        db.commit()
        row = db.execute(
            'SELECT id, issue_id, author, body, created_at FROM comments WHERE id = ?',
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)
