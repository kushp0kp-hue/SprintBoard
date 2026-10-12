from flask import Blueprint, jsonify, request
from .repositories import ProjectRepository, IssueRepository
from .services import CommentService, IssueService, NotFoundError, ValidationError

api = Blueprint('api', __name__)


def error_response(message, status_code):
    return jsonify({'error': message}), status_code


@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return error_response(str(error), 400)


@api.errorhandler(NotFoundError)
def handle_not_found_error(error):
    return error_response(str(error), 404)


@api.get('/projects')
def list_projects():
    return jsonify(ProjectRepository.list_all())


@api.post('/projects')
def create_project():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get('name', '')).strip()
    if not name:
        return error_response('Project name is required', 400)
    project = ProjectRepository.create(name, str(payload.get('description', '')).strip())
    return jsonify(project), 201


@api.delete('/projects/<int:project_id>')
def delete_project(project_id):
    if not ProjectRepository.delete(project_id):
        return error_response('Project not found', 404)
    return '', 204


@api.get('/projects/<int:project_id>/issues')
def list_issues(project_id):
    if not ProjectRepository.get(project_id):
        return error_response('Project not found', 404)
    filters = {
        'status': request.args.get('status', '').strip(),
        'priority': request.args.get('priority', '').strip(),
        'assignee': request.args.get('assignee', '').strip(),
        'q': request.args.get('q', '').strip(),
    }
    filters = {key: value for key, value in filters.items() if value}
    return jsonify(IssueRepository.list_for_project(project_id, filters))


@api.post('/projects/<int:project_id>/issues')
def create_issue(project_id):
    payload = request.get_json(silent=True) or {}
    return jsonify(IssueService.create(project_id, payload)), 201


@api.get('/issues/<int:issue_id>')
def get_issue(issue_id):
    issue = IssueRepository.get(issue_id)
    if not issue:
        return error_response('Issue not found', 404)
    return jsonify(issue)


@api.patch('/issues/<int:issue_id>')
def update_issue(issue_id):
    payload = request.get_json(silent=True) or {}
    return jsonify(IssueService.update(issue_id, payload))


@api.delete('/issues/<int:issue_id>')
def delete_issue(issue_id):
    if not IssueRepository.delete(issue_id):
        return error_response('Issue not found', 404)
    return '', 204


@api.post('/issues/<int:issue_id>/comments')
def add_comment(issue_id):
    payload = request.get_json(silent=True) or {}
    return jsonify(CommentService.create(issue_id, payload)), 201
