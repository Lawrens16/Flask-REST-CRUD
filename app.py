from flask import Flask, jsonify, request, abort
from flask_mysqldb import MySQL

app = Flask(__name__) # create the Flask app instance

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lawrence'
app.config['MYSQL_DB'] = 'cs_elec'
mysql = MySQL(app)
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

@app.route('/')
def home():
    return "Hello, Flask!"

#Routes 
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