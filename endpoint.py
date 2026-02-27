import os
import sqlite3
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

load_dotenv()
CORS(app)

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/')
def home():
    return render_template('home.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('view_contacts'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')

    return render_template('admin_login.html')

@app.route('/contact', methods=["POST"])
def get_contact():
    try:
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form.get('phone', '')
        message = request.form['message']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_to_database(fullname, email, phone, message, timestamp)

        # with open('contact_submissions.txt', 'a') as f:
        #     f.write(f"{timestamp} | {fullname} | {email} | {phone} | {message}\n")

        return jsonify({"status": "success", "message": "Form submitted successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def save_to_database(name, email, phone, message, timestamp):
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  phone TEXT,
                  message TEXT,
                  timestamp TEXT,
                  status TEXT DEFAULT 'unread')''')

    c.execute("INSERT INTO contacts (name, email, phone, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (name, email, phone, message, timestamp))

    conn.commit()
    conn.close()


@app.route('/admin/contacts')
@admin_required
def view_contacts():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM contacts ORDER BY id DESC")
    contacts = c.fetchall()
    conn.close()

    current_time = datetime.now()

    return render_template('admin_panel.html', contacts=contacts, now=current_time)


@app.route('/admin/contacts/<int:mark_id>/read', methods=['POST'])
@admin_required
def mark_as_read(mark_id):
    try:
        conn = sqlite3.connect('contacts.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(contacts)")

        c.execute("UPDATE contacts SET status='read' WHERE id=?", (mark_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Marked as read"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/contacts/<int:del_id>/delete', methods=['POST'])
@admin_required
def delete_contact(del_id):
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE id=?", (del_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)