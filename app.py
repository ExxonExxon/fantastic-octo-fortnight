from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'very_secret_key_hello_world_chatgpt_ee'

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS forums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        creator_id INTEGER NOT NULL,
        created_on TIMESTAMP NOT NULL,
        FOREIGN KEY (creator_id) REFERENCES users(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        forum_id INTEGER NOT NULL,
        username TEXT,
        comment_text TEXT,
        timestamp TIMESTAMP,
        likes INTEGER DEFAULT 0,
        FOREIGN KEY (forum_id) REFERENCES forums(id),
        FOREIGN KEY (username) REFERENCES users(username)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment_id INTEGER NOT NULL,
        username TEXT,
        reply_text TEXT,
        timestamp TIMESTAMP,
        likes INTEGER DEFAULT 0,
        FOREIGN KEY (comment_id) REFERENCES comments(id),
        FOREIGN KEY (username) REFERENCES users(username)
    )
''')


conn.close()

def get_forum_id_from_comment(comment_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT forum_id FROM comments WHERE id = ?', (comment_id,))
        forum_id = cursor.fetchone()[0]

    return forum_id


def get_forum(forum_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM forums WHERE id = ?', (forum_id,))
        forum_data = cursor.fetchone()

        if forum_data is None:
            return None

        forum = {
            'id': forum_data[0],
            'title': forum_data[1],
            'description': forum_data[2],
            'views': forum_data[3],
            'likes': forum_data[4],
            'comments': forum_data[5],
            'creator_id': forum_data[6],
            'created_on': forum_data[7]
        }

        cursor.execute('SELECT * FROM users WHERE id = ?', (forum['creator_id'],))
        creator_data = cursor.fetchone()

        if creator_data is not None:
            forum['creator'] = creator_data[1]

        return forum

@app.route('/', methods=['GET', 'POST'])
def index():
    logged_out = session.get('logged_out')
    user = session.get('user')

    if user is None:
        username = 'Welcome, Please Log In!'
    else:
        username = f'Welcome, {user}!'

    if request.method == 'GET':
        btn_stat = session.get('btn-stat')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM forums')
        rows = cursor.fetchall()

        forums_data = []

        for row in rows:
            forum_data = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'views': row[3],
                'likes': row[4],
                'comments': row[5],
                'creator_id': row[6],
                'created_on': row[7],
                'category_id': row[8]  # Add this line for the category_id column
            }
            forums_data.append(forum_data)

        if user is None:
            sign_title = 'Signup'
            sign_link = '/signup'
            login_title = 'Login'
            login_link = '/login'
            check_link = '/help'
            check_title = 'Help'
        else:
            sign_title = 'Settings'
            sign_link = '/settings'
            login_title = 'Logout'
            login_link = '/logout'
            check_link = '/my_forums'
            check_title = 'Your Forums'

        conn.close()

        return render_template(
            'index.html',
            logged_out=logged_out,
            forums_data=forums_data,
            user=username,
            sign_title=sign_title,
            sign_link=sign_link,
            login_title=login_title,
            login_link=login_link,
            check_link=check_link,
            check_title=check_title,
            background_color=background_color,
            btn_color=btn_color,
            container_color=container_color,
            nav_color=nav_color,
            txt_color=txt_color
        )
    else:
        return render_template('index.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        aqua_theme = request.form.get('name-aqua')
        green_theme = request.form.get('name-green')
        red_theme = request.form.get('name-red')
        yellow_theme = request.form.get('name-yellow')

        if aqua_theme == True:
            session['btn-stat'] = 'aqua_theme'
        elif green_theme == True:
            session['btn-stat'] = 'green_theme'
        elif yellow_theme == True:
            session['btn-stat'] = 'yellow_theme'
        elif red_theme == True:
            session['btn-stat'] = 'red_theme'
            
        return redirect(url_for('index'))
    else:
        return render_template('settings.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect('/')


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
            return redirect('/')
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
            session['user'] = username
            return redirect('/')
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


@app.route('/add_forum', methods=['POST'])
def add_forum():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        creator_id = session.get('user_id')

        if title and description and creator_id:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO forums (title, description, views, likes, comments, creator_id, created_on) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (title, description, 0, 0, 0, creator_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()

        return redirect(url_for('index'))
    else:
        return render_template('add_forums.html')


@app.route('/forum/<int:forum_id>', methods=['GET', 'POST'])
def view_forum(forum_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM forums WHERE id = ?',
        (forum_id,)
    )
    forum_data = cursor.fetchone()

    if forum_data is None:
        return 'Forum not found'

    forum = {
        'id': forum_data[0],
        'title': forum_data[1],
        'description': forum_data[2],
        'views': forum_data[3],
        'likes': forum_data[4],
        'comments': forum_data[5],
        'creator_id': forum_data[6],
        'created_on': forum_data[7]
    }

    cursor.execute(
        'SELECT * FROM comments WHERE forum_id = ?',
        (forum_id,)
    )
    comments_data = cursor.fetchall()

    comments = []
    for comment_data in comments_data:
        comment = {
            'id': comment_data[0],
            'forum_id': comment_data[1],
            'username': comment_data[2],
            'comment_text': comment_data[3],
            'likes': comment_data[4]
        }
        comments.append(comment)

    conn.close()

    if request.method == 'POST':
        username = session.get('user')
        comment_text = request.form['comment']

        if username and comment_text:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO comments (forum_id, username, comment_text, likes) VALUES (?, ?, ?, ?)',
                (forum_id, username, comment_text, 0)
            )
            conn.commit()
            conn.close()

            return redirect(url_for('view_forum', forum_id=forum_id))

    return render_template('view_forum.html', forum=forum, comments=comments)


@app.route('/like_forum/<int:forum_id>', methods=['POST'])
def like_forum(forum_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE forums SET likes = likes + 1 WHERE id = ?', (forum_id,))
        connection.commit()

    return redirect(url_for('view_forum', forum_id=forum_id))


@app.route('/like_comment/<int:comment_id>/<int:forum_id>', methods=['POST'])
def like_comment(comment_id, forum_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE comments SET likes = likes + 1 WHERE id = ?', (comment_id,))
        connection.commit()

    return redirect(url_for('view_forum', forum_id=forum_id))


@app.route('/reply_comment/<int:comment_id>', methods=['POST'])
def reply_comment(comment_id):
    reply = request.form.get('reply')
    username = session.get('user')

    if reply and username:
        with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO replies (comment_id, username, reply_text, timestamp) VALUES (?, ?, ?, ?)',
                (comment_id, username, reply, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            connection.commit()

    return redirect(url_for('view_forum', forum_id=get_forum_id_from_comment(comment_id)))


if __name__ == '__main__':
    app.run(debug=True)