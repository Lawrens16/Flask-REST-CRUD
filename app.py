from flask import Flask, jsonify, request, abort, make_response, render_template, session, flash
import jwt
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__) # create the Flask app instance

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lawrence'
app.config['MYSQL_DB'] = 'cs_elec'
app.config['SECRET_KEY'] = 'b786a8c232db4e56b306feb599cf8a00'
mysql = MySQL(app)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

#Routes
@app.route('/public')
def public():
    return 'For public, anyone can view'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified, you can view this'

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username and password == 'password123':
        session['logged_in'] = True

        token = jwt.encode({
            'user' : username,
            'expiration': datetime.utcnow() + timedelta(minutes=5)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})
    else:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/')
def home():
    if not session.get('loged_in'):
        return render_template('login.html')
    else:
        return 'You are logged in!'


@app.route('/users', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user")
    users = cur.fetchall()
    cur.close()
    return jsonify(users)

@app.route('/comments', methods=['GET'])
def get_comments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM comments")
    comments = cur.fetchall()
    cur.close()
    return jsonify(comments)

@app.route('/posts', methods=['GET'])
def get_posts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    cur.close()
    return jsonify(posts)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE idUser = %s", (id,))
    user = cur.fetchone()
    if user is None:
        abort(404) # Not found page
    cur.close()

    return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('username')
    email = data.get('email')

    if not name or not email:
        abort(400) # Bad request

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user (username, email) VALUES (%s, %s)", (name, email))
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.close()

    return jsonify({'id': new_id, 'username': name, 'email': email}), 201

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    name = data.get('username')
    email = data.get('email')

    # Basic validation
    if not name or not email:
        abort(400) 

    cur = mysql.connection.cursor()
    
    cur.execute("UPDATE user SET username = %s, email = %s WHERE idUser = %s", (name, email, id))
    mysql.connection.commit()

    # Check if a row was modified
    rows_affected = cur.rowcount
    cur.close()

    if rows_affected == 0:
        abort(404) # User not found

    return jsonify({'id': id, 'username': name, 'email': email, 'message': 'User updated successfully'})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    cur = mysql.connection.cursor()
    
    # Delete logic
    cur.execute("DELETE FROM user WHERE idUser = %s", (id,))
    mysql.connection.commit()
    
    
    rows_affected = cur.rowcount
    cur.close()

    if rows_affected == 0:
        abort(404)

    return jsonify({'message': 'User deleted successfully', 'id': id}), 200


if __name__ == '__main__':
    app.run(debug=True)