import os
import logging
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import session as flask_session
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

load_dotenv()

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = True

CORS(app)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)