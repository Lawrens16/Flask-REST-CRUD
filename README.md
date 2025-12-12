# Flask REST API with MySQL & JWT

A comprehensive Flask RESTful API providing CRUD functionality for Users, Posts, and Comments. This project demonstrates authentication using JWT, database integration with MySQL, and support for multiple output formats (JSON/XML).

## 📋 Prerequisites

- Python 3.x
- MySQL Server
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask_project
   ```

2. **Create and activate a virtual environment**
   
   *Windows (PowerShell):*
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate
   ```
   
   *macOS/Linux:*
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🗄️ Database Setup

1. Ensure your MySQL server is running.
2. Create a database named `cs_elec`.
3. Execute the following SQL commands to create the required tables:

```sql
USE cs_elec;

CREATE TABLE user (
    idUser INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    content TEXT,
    FOREIGN KEY (user_id) REFERENCES user(idUser)
);

CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    content TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
```

4. Update the database configuration in `app.py` if your credentials differ:
   ```python
   app.config['MYSQL_USER'] = 'root'
   app.config['MYSQL_PASSWORD'] = 'your_password'
   ```

## 🚀 Running the Application

Start the Flask development server:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`.

## 📖 API Documentation

### Authentication

| Method | Endpoint | Description | Body (Form Data) |
|--------|----------|-------------|------------------|
| POST   | `/login` | Get JWT Token | `username`, `password` |

*Note: Default password for testing is `password123`.*

### Users

| Method | Endpoint | Description | Auth Required | Query Params |
|--------|----------|-------------|---------------|--------------|
| GET    | `/users` | Get all users | Yes | `q` (search), `format` (xml/json) |
| GET    | `/users/<id>` | Get user by ID | No | `format` (xml/json) |
| POST   | `/users` | Create user | No | JSON Body: `username`, `email` |
| PUT    | `/users/<id>` | Update user | No | JSON Body: `username`, `email` |
| DELETE | `/users/<id>` | Delete user | No | - |

### Posts & Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/posts` | Get all posts |
| GET    | `/comments` | Get all comments |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/public` | Public test route |
| GET    | `/auth` | Protected test route (requires `?token=<jwt>`) |

## 🧪 Running Tests

This project includes a unit test suite using `unittest` and `unittest.mock` to test endpoints without a live database connection.

Run the tests using:

```bash
python test_app.py
```

## 📦 Features

- **JWT Authentication**: Secure endpoints with JSON Web Tokens.
- **CRUD Operations**: Full Create, Read, Update, Delete support for Users.
- **Search**: Filter users by username using `?q=search_term`.
- **Format Negotiation**: Support for XML output via `?format=xml`.
- **Error Handling**: Proper HTTP status codes and error messages.
