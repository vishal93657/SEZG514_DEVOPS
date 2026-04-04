import sys
import os
import unittest
import json

# Force environment variable to use a safe test database before importing app
os.environ["FLASK_DB_NAME"] = "test_aceest_fitness.db"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import app, init_db

class AceestApiTestCase(unittest.TestCase):
    def setUp(self):
        # Create the specific test schema on setup
        init_db()
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        # Delete the test database file to leave no trace
        if os.path.exists("test_aceest_fitness.db"):
            try:
                os.remove("test_aceest_fitness.db")
            except Exception:
                pass # Avoid lock crashes on specific OS handling

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], "ACEest Fitness & Gym API Running")

    def test_get_programs(self):
        response = self.app.get('/programs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("Fat Loss (FL)", data)
        self.assertIn("Muscle Gain (MG)", data)

    def test_save_and_load_client(self):
        client_data = {
            "name": "Jane Doe",
            "age": 28,
            "weight": 65.0,
            "program": "Beginner (BG)"
        }
        # Test Save Client
        response = self.app.post('/client',
                                 data=json.dumps(client_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Test Load Client
        response = self.app.get('/client/Jane Doe')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], "Jane Doe")
        self.assertEqual(data['weight'], 65.0)

    def test_save_and_get_progress(self):
        # Populate dummy client first
        client_data = {"name": "Jane Doe", "program": "Beginner (BG)", "weight": 60}
        self.app.post('/client', data=json.dumps(client_data), content_type='application/json')

        # Test Save Progress
        progress_data = {
            "name": "Jane Doe",
            "adherence": 90
        }
        response = self.app.post('/progress',
                                 data=json.dumps(progress_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Test Get Progress
        response = self.app.get('/progress/Jane Doe')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['adherence'], 90)

    def test_client_not_found(self):
        response = self.app.get('/client/GhostUser')
        self.assertEqual(response.status_code, 404)

    def test_save_client_invalid_program(self):
        client_data = {
        "name": "Invalid Test",
        "program": "Bodybuilder (XX)"
        }
        response = self.app.post('/client',
                             data=json.dumps(client_data),
                             content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_login_invalid(self):
        res = self.app.post('/login',
        data=json.dumps({"username": "admin", "password": "wrong"}),
        content_type='application/json')
        self.assertEqual(res.status_code, 401)
    
    def test_client_missing_name(self):
        res = self.app.post('/client',
            data=json.dumps({"weight": 70}),
            content_type='application/json')
        self.assertEqual(res.status_code, 400)


    def test_client_invalid_program(self):
        res = self.app.post('/client',
            data=json.dumps({
                "name": "TestUser",
                "program": "InvalidProgram"
            }),
            content_type='application/json')
        self.assertEqual(res.status_code, 200)


    def test_progress_no_json(self):
        res = self.app.post('/progress', data="notjson")
        self.assertTrue(res.status_code in [400, 415])


    def test_workout_without_client(self):
        res = self.app.post('/workout',
            data=json.dumps({
                "name": "Ghost",
                "date": "2026-01-01",
                "type": "Cardio",
                "duration": 30
            }),
            content_type='application/json')
        self.assertEqual(res.status_code, 200)


    def test_get_workout_empty(self):
        res = self.app.get('/workout/Unknown')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data), [])


    def test_get_progress_empty(self):
        res = self.app.get('/progress/Unknown')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data), [])


    def test_membership_fields(self):
        self.app.post('/client',
            data=json.dumps({
                "name": "John",
                "membership_status": "Active"
            }),
            content_type='application/json')

        res = self.app.get('/client/John')
        data = json.loads(res.data)

        self.assertEqual(data["membership_status"], "Active")

if __name__ == '__main__':
    unittest.main()
