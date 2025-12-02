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

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE idUser = %s", (id,))
    user = cur.fetchone()
    if user is None:
        abort(404) # Not found page
    cur.close()

    return jsonify(user)




if __name__ == '__main__':
    app.run(debug=True)