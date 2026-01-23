import os
import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for, flash

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'dev'
app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')

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
            # In a real deployed app, we might use flash messages, but let's keep it simple for now
            return redirect(url_for('contact')) # Ideally show a success message

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
