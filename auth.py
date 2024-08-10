from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import hashlib

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()

# User class
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

    def is_elevated(self):
        return self.role == 'elevated'

# Load user
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

# Hash password
def hash_password(password, salt="Athena", pepper="Minerva", iterations=41623):
    combined = salt + password + pepper
    hashed = combined.encode('utf-8')
    
    for _ in range(iterations):
        hashed = hashlib.sha512(hashed).digest()
    
    return hashed.hex()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user_data = c.fetchone()
        conn.close()
        if user_data:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            if password == 'owlbear':
                return redirect(url_for('auth.reset_password'))
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.reset_password'))
        hashed_password = hash_password(new_password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, current_user.id))
        conn.commit()
        conn.close()
        flash('Password updated successfully')
        return redirect(url_for('admin'))
    return render_template('reset_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
