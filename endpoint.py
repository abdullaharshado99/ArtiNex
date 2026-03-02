import os
import re
import sqlite3
import smtplib
from pathlib import Path
import socket

from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

load_dotenv()
CORS(app)

SENDER_KEY = os.environ.get('SENDER_KEY')
Sender_Email = os.environ.get('SENDER_EMAIL')
Receiver_Email = os.environ.get('RECEIVE_EMAIL')
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

        send_email_notification(fullname, email, phone, message, timestamp)

        # with open('contact_submissions.txt', 'a') as f:
        #     f.write(f"{timestamp} | {fullname} | {email} | {phone} | {message}\n")

        return jsonify({"status": "success", "message": "Form submitted successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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

def send_email_notification(name, email, phone, message, timestamp):
    socket.setdefaulttimeout(10)

    sender_email = Sender_Email
    sender_password = SENDER_KEY
    receiver_email = Receiver_Email

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Contact Form Submission from {name}"

    template_path = Path(__file__).parent / 'templates' / 'contact_notification.html'

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        html_content = html_template
        html_content = html_content.replace('__NAME__', name)
        html_content = html_content.replace('__EMAIL__', email)
        html_content = html_content.replace('__DATE__', timestamp)
        html_content = html_content.replace('__MESSAGE__', message.replace('\n', '<br>'))

        if phone and phone.strip():
            html_content = html_content.replace('__PHONE__', phone)
            html_content = html_content.replace('<!--PHONE_SECTION_START-->', '')
            html_content = html_content.replace('<!--PHONE_SECTION_END-->', '')
        else:
            pattern = r'<!--PHONE_SECTION_START-->.*?<!--PHONE_SECTION_END-->'
            html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)

    except Exception as e:
        print(f"Error reading template: {e}")
        html_content = f"""
        <h1>New Contact from {name}</h1>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        <p><small>Received: {timestamp}</small></p>
        """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")
        return True
    except socket.timeout:
        print("❌ Connection timeout - SMTP may be blocked")
        return False
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False
    finally:
        socket.setdefaulttimeout(None)

if __name__ == '__main__':
    app.run(debug=True)