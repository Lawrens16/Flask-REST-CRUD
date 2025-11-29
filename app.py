from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__) # create the Flask app instance

@app.route('/')
def home():
    return "Hello, Flask!"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lawrence'
app.config['MYSQL_DB'] = 'cs_elec'
mysql = MySQL(app)

if __name__ == '__main__':
    app.run(debug=True)