import sqlite3
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pipeline import send_email_notification
from Anna_pipeline.query_engine import QueryEngine, RAGConfig
from flask import Flask, render_template, request, jsonify, redirect, url_for, session


app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

load_dotenv()
CORS(app)

query_engine = QueryEngine()

chat_sessions = {}

app.secret_key = RAGConfig.FLASK_APP_PASSWORD

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

@admin_required
@app.route('/api/chat', methods=['POST'])
def chat_api():
    """RAG endpoint that returns context for LLM"""
    try:
        data = request.json
        query = data.get('message', '').lower()
        session_id = data.get('session_id')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'history': [],
                'created_at': datetime.now().isoformat()
            }

        # Store user message
        chat_sessions[session_id]['history'].append({
            'role': 'user',
            'message': query,
            'timestamp': datetime.now().isoformat()
        })

        response = query_engine.search(query)

        chat_sessions[session_id]['history'].append({
            'role': 'bot',
            'message': response[0]["text"],
            'timestamp': datetime.now().isoformat()
        })

        return jsonify({
            'response': response[0]["text"],
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == RAGConfig.ADMIN_USERNAME and password == RAGConfig.ADMIN_PASSWORD:
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

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    if session_id in chat_sessions:
        return jsonify(chat_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)