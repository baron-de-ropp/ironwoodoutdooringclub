from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import sqlite3
from auth import hash_password

user_mgmt_bp = Blueprint('user_mgmt', __name__)

@user_mgmt_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_elevated():
        flash('You do not have permission to add users')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        hashed_password = hash_password('owlbear')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
        conn.commit()
        conn.close()
        flash('User added successfully')
        return redirect(url_for('admin'))
    return render_template('add_user.html')

@user_mgmt_bp.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_elevated():
        flash('You do not have permission to manage users')
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

@user_mgmt_bp.route('/remove_user/<int:user_id>')
@login_required
def remove_user(user_id):
    if not current_user.is_elevated():
        flash('You do not have permission to remove users')
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash('User removed successfully')
    return redirect(url_for('user_mgmt.manage_users'))

@user_mgmt_bp.route('/reset_user_password/<int:user_id>')
@login_required
def reset_user_password(user_id):
    if not current_user.is_elevated():
        flash('You do not have permission to reset user passwords')
        return redirect(url_for('admin'))

    hashed_password = hash_password('owlbear')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()
    flash('User password reset to default successfully')
    return redirect(url_for('user_mgmt.manage_users'))
