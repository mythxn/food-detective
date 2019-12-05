import sqlite3

from flask import Flask, redirect, request, url_for, render_template

# create an app
app = Flask(__name__)  # our Flask app
DB_FILE = 'mydb.db'  # file for our Database


# set-up index page
@app.route('/')
def root():
    return render_template('index.html')


# setup posts
@app.route('/posts/1')
def post1():
    return render_template('posts/1.html')


@app.route('/posts/2')
def post2():
    return render_template('posts/2.html')


@app.route('/posts/3')
def post3():
    return render_template('posts/3.html')


# guestbook
def _insert(name, email, age):
    params = {'name': name, 'email': email, 'age': age}
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("insert into guestbook VALUES (:name, :email, :age)", params)
    connection.commit()
    cursor.close()


@app.route('/guestbook', methods=['POST', 'GET'])
def gb():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM guestbook")
    rv = cursor.fetchall()
    cursor.close()
    return render_template('guestbook.html', entries=rv)


@app.route('/sign', methods=['POST'])
def sign():
    _insert(request.form['name'], request.form['email'], request.form['age'])
    return redirect(url_for('gb'))


if __name__ == '__main__':
    app.run()
