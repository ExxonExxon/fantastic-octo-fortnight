from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'my secret key'

conn = sqlite3.connect('database.db')
conn.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    );

    CREATE TABLE IF NOT EXISTS forums (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT
    );
''')
conn.commit()
conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    user = session.get('user')

    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, description FROM forums')
        rows = cursor.fetchall()

        forums_data = []
        for row in rows:
            forum_data = {
                'title': row[0],
                'description': row[1]
            }
            forums_data.append(forum_data)
        
        if user == None:
            button_title = 'Signup'
            button_link = '/signup'
        else:
            button_title = 'Add Forum'
            button_link = '/add_forums'

        conn.close()

        return render_template('index.html', forums_data=forums_data, user=user, button_title=button_title, button_link=button_link)
    else:
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        row = cursor.fetchone()

        

        if row is not None:
            allowed = f'Welcome {username}'
            session['user'] = username
        else:
            allowed = 'Wrong password or username'

        conn.close()

        return render_template('login.html', allowed=allowed)
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        row = cursor.fetchone()
        cursor.execute('SELECT COUNT(*) FROM users')
        total = cursor.fetchone()[0]

        if row is None:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            message = 'Sign up successful!'
        else:
            message = 'Username already exists. Please choose a different username.'

        conn.close()

        return render_template('signup.html', message=message, user=username, total=total)
    else:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total = cursor.fetchone()[0]
        conn.close()

        return render_template('signup.html', total=total)
    
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', 'User')
    return redirect(url_for('index'))

@app.route('/add_forums', methods=['POST', 'GET'])
def add_forums():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM forums')
        
        cursor.execute('INSERT INTO forums (title, description) VALUES (?, ?)', (title, desc))
        conn.commit()
        conn.close()
        
        return render_template('add_forums.html')
    else:
        return render_template('add_forums.html')
    

if __name__ == '__main__':
    app.run(debug=True)
