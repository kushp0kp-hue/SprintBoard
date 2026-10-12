import tempfile
import unittest
from pathlib import Path
from app import create_app


class SprintBoardApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / 'test.db'
        self.app = create_app({'TESTING': True, 'DATABASE': str(db_path)})
        self.client = self.app.test_client()
        response = self.client.post('/api/projects', json={'name': 'Interview Prep', 'description': 'Test project'})
        self.project = response.get_json()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_issue(self):
        response = self.client.post(
            f"/api/projects/{self.project['id']}/issues",
            json={'title': 'Add validation', 'description': 'Validate API input', 'priority': 'high', 'labels': ['backend', 'api']},
        )
        self.assertEqual(response.status_code, 201)
        issue = response.get_json()
        self.assertEqual(issue['title'], 'Add validation')
        self.assertEqual(issue['priority'], 'high')
        self.assertEqual(issue['labels'], ['api', 'backend'])

    def test_filter_issues_by_status(self):
        pid = self.project['id']
        self.client.post(f'/api/projects/{pid}/issues', json={'title': 'Todo issue', 'status': 'todo'})
        self.client.post(f'/api/projects/{pid}/issues', json={'title': 'Done issue', 'status': 'done'})
        response = self.client.get(f'/api/projects/{pid}/issues?status=done')
        issues = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['title'], 'Done issue')

    def test_update_issue_status(self):
        create = self.client.post(f"/api/projects/{self.project['id']}/issues", json={'title': 'Move me'})
        issue_id = create.get_json()['id']
        response = self.client.patch(f'/api/issues/{issue_id}', json={'status': 'in_progress'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'in_progress')

    def test_invalid_priority_returns_400(self):
        response = self.client.post(
            f"/api/projects/{self.project['id']}/issues",
            json={'title': 'Bad priority', 'priority': 'super-important'},
        )
        self.assertEqual(response.status_code, 400)

    def test_add_comment(self):
        create = self.client.post(f"/api/projects/{self.project['id']}/issues", json={'title': 'Commentable issue'})
        issue_id = create.get_json()['id']
        response = self.client.post(f'/api/issues/{issue_id}/comments', json={'author': 'Kush', 'body': 'I can explain this endpoint.'})
        self.assertEqual(response.status_code, 201)
        issue = self.client.get(f'/api/issues/{issue_id}').get_json()
        self.assertEqual(len(issue['comments']), 1)

    def test_delete_issue(self):
        create = self.client.post(f"/api/projects/{self.project['id']}/issues", json={'title': 'Delete me'})
        issue_id = create.get_json()['id']
        self.assertEqual(self.client.delete(f'/api/issues/{issue_id}').status_code, 204)
        self.assertEqual(self.client.get(f'/api/issues/{issue_id}').status_code, 404)


if __name__ == '__main__':
    unittest.main()
