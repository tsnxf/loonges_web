import os
import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for, flash, Response
from flask_mail import Mail, Message
from functools import wraps

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'dev'
app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')

# Mail Configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# Admin Authentication Helpers
def check_auth(username, password):
    return username == 'admin' and password == os.environ.get('ADMIN_PASSWORD', 'admin')

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Ensure instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    print('Initialized the database.')

# Initialize DB on first run (helper for dev)
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # In a real app, fetch from DB. For now, we'll placeholder it.
    return render_template('product_detail.html', product_id=product_id)

@app.route('/factory')
def factory():
    return render_template('factory.html')

@app.route('/admin/messages')
@requires_auth
def admin_messages():
    db = get_db()
    messages = db.execute('SELECT * FROM contact_messages ORDER BY timestamp DESC').fetchall()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/messages/delete/<int:message_id>', methods=['POST'])
@requires_auth
def delete_message(message_id):
    db = get_db()
    db.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
    db.commit()
    return redirect(url_for('admin_messages'))

@app.route('/contact', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        error = None

        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required.'
        elif not message:
            error = 'Message is required.'

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)',
                (name, email, message)
            )
            db.commit()
            db.commit()
            
            # Send Email Notification
            try:
                msg = Message(f"New Contact from {name}",
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[app.config['MAIL_USERNAME']])
                msg.body = f"Name: {name}\nEmail: {email}\nMessage: \n{message}"
                mail.send(msg)
            except Exception as e:
                print(f"Failed to send email: {e}")

            return redirect(url_for('contact'))

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
