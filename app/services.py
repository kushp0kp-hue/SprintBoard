from .repositories import ProjectRepository, IssueRepository, CommentRepository

VALID_STATUSES = {'todo', 'in_progress', 'blocked', 'done'}
VALID_PRIORITIES = {'low', 'medium', 'high', 'critical'}


class ValidationError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


class IssueService:
    @staticmethod
    def create(project_id, payload):
        if not ProjectRepository.get(project_id):
            raise NotFoundError('Project not found')

        title = str(payload.get('title', '')).strip()
        if not title:
            raise ValidationError('Issue title is required')

        status = payload.get('status', 'todo')
        priority = payload.get('priority', 'medium')
        if status not in VALID_STATUSES:
            raise ValidationError('Invalid issue status')
        if priority not in VALID_PRIORITIES:
            raise ValidationError('Invalid issue priority')

        labels = payload.get('labels', [])
        if not isinstance(labels, list):
            raise ValidationError('labels must be a list')

        clean = {
            'title': title,
            'description': str(payload.get('description', '')).strip(),
            'status': status,
            'priority': priority,
            'assignee': str(payload.get('assignee', '')).strip(),
            'labels': labels,
        }
        return IssueRepository.create(project_id, clean)

    @staticmethod
    def update(issue_id, payload):
        if not IssueRepository.get(issue_id):
            raise NotFoundError('Issue not found')
        updates = {}

        if 'title' in payload:
            title = str(payload['title']).strip()
            if not title:
                raise ValidationError('Issue title cannot be empty')
            updates['title'] = title
        if 'description' in payload:
            updates['description'] = str(payload['description']).strip()
        if 'assignee' in payload:
            updates['assignee'] = str(payload['assignee']).strip()
        if 'status' in payload:
            if payload['status'] not in VALID_STATUSES:
                raise ValidationError('Invalid issue status')
            updates['status'] = payload['status']
        if 'priority' in payload:
            if payload['priority'] not in VALID_PRIORITIES:
                raise ValidationError('Invalid issue priority')
            updates['priority'] = payload['priority']
        if 'labels' in payload:
            if not isinstance(payload['labels'], list):
                raise ValidationError('labels must be a list')
            updates['labels'] = payload['labels']

        return IssueRepository.update(issue_id, updates)


class CommentService:
    @staticmethod
    def create(issue_id, payload):
        if not IssueRepository.get(issue_id):
            raise NotFoundError('Issue not found')
        author = str(payload.get('author', '')).strip()
        body = str(payload.get('body', '')).strip()
        if not author:
            raise ValidationError('Comment author is required')
        if not body:
            raise ValidationError('Comment body is required')
        return CommentRepository.create(issue_id, author, body)
