import unittest
from unittest.mock import MagicMock, patch
import json
from app import app

class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.app = app.test_client()

    def get_auth_token(self):
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        return data['token']

    # --- Authentication Tests ---

    def test_login_success(self):
        # Test login with correct credentials
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    def test_login_failure(self):
        # Test login with incorrect credentials
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)

    @patch('app.mysql')
    def test_get_users_no_token(self, mock_mysql):
        # Test accessing protected route without token
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 401)

    @patch('app.mysql')
    def test_get_users_invalid_token(self, mock_mysql):
        # Test accessing protected route with invalid token
        response = self.app.get('/users?token=invalidtoken')
        self.assertEqual(response.status_code, 403)

    # --- CRUD Operations Tests ---

    @patch('app.mysql')
    def test_get_users_success(self, mock_mysql):
        # Mock DB response
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{'idUser': 1, 'username': 'test', 'email': 'test@test.com'}]
        mock_mysql.connection.cursor.return_value = mock_cursor

        # Get valid token
        token = self.get_auth_token()

        # Test GET /users
        response = self.app.get(f'/users?token={token}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'test')

    @patch('app.mysql')
    def test_get_users_search(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [] # Mock empty result for search
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()

        # Test GET /users?q=search_term
        self.app.get(f'/users?token={token}&q=search_term')
        
        # Verify SQL query for search
        mock_cursor.execute.assert_called_with("SELECT * FROM user WHERE username LIKE %s", ("%search_term%",))

    @patch('app.mysql')
    def test_get_user_by_id(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'idUser': 1, 'username': 'test', 'email': 'test@test.com'}
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get('/users/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'test')

    @patch('app.mysql')
    def test_get_user_not_found(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get('/users/999')
        self.assertEqual(response.status_code, 404)

    @patch('app.mysql')
    def test_create_user_success(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        payload = {'username': 'newuser', 'email': 'new@test.com', 'password': 'newpassword'}
        response = self.app.post(f'/users?token={token}', json=payload)
        
        self.assertEqual(response.status_code, 201)
        mock_cursor.execute.assert_called()
        # Verify commit was called
        mock_mysql.connection.commit.assert_called()

    @patch('app.mysql')
    def test_create_user_missing_fields(self, mock_mysql):
        token = self.get_auth_token()
        payload = {'username': 'newuser'} # Missing email
        response = self.app.post(f'/users?token={token}', json=payload)
        self.assertEqual(response.status_code, 400)

    @patch('app.mysql')
    def test_update_user_success(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        payload = {'username': 'updated', 'email': 'updated@test.com', 'password': 'updatedpass'}
        response = self.app.put(f'/users/1?token={token}', json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_mysql.connection.commit.assert_called()

    @patch('app.mysql')
    def test_update_user_not_found(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0 # Simulate no rows affected
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        payload = {'username': 'updated', 'email': 'updated@test.com', 'password': 'updatedpass'}
        response = self.app.put(f'/users/999?token={token}', json=payload)
        
        self.assertEqual(response.status_code, 404)

    @patch('app.mysql')
    def test_delete_user_success(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        response = self.app.delete(f'/users/1?token={token}')
        self.assertEqual(response.status_code, 200)
        mock_mysql.connection.commit.assert_called()

    @patch('app.mysql')
    def test_delete_user_not_found(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        response = self.app.delete(f'/users/999?token={token}')
        self.assertEqual(response.status_code, 404)

    # --- Formatting Tests ---

    @patch('app.mysql')
    def test_xml_format(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{'idUser': 1, 'username': 'test'}]
        mock_mysql.connection.cursor.return_value = mock_cursor

        token = self.get_auth_token()
        
        # Request XML format
        response = self.app.get(f'/users?token={token}&format=xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/xml')
        self.assertIn(b'<?xml', response.data)

if __name__ == '__main__':
    unittest.main()


