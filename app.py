from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import sqlite3
from auth import auth_bp, User, hash_password
from user_management import user_mgmt_bp
from create_app import create_app
from auth import login_manager

app = create_app()
app.secret_key = 'your_secret_key'
login_manager.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@login_required
def admin():
    recent_collection = None
    if current_user.is_elevated():
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM collections ORDER BY id DESC LIMIT 1")
        recent_collection = c.fetchone()
        conn.close()
    return render_template('admin.html', recent_collection=recent_collection)

@app.route('/create_collection', methods=['GET', 'POST'])
@login_required
def create_collection():
    if not current_user.is_elevated():
        flash('You do not have permission to create collections')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO collections (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        flash('Collection created successfully')
        return redirect(url_for('manage_collections'))
    return render_template('create_collection.html')

@app.route('/manage_collections')
@login_required
def manage_collections():
    if not current_user.is_elevated():
        flash('You do not have permission to manage collections')
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM collections")
    collections = c.fetchall()
    conn.close()
    return render_template('manage_collections.html', collections=collections)

@app.route('/add_invitee/<int:collection_id>', methods=['GET', 'POST'])
@login_required
def add_invitee(collection_id):
    if not current_user.is_elevated():
        flash('You do not have permission to add invitees')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO invitees (name, collection_id) VALUES (?, ?)", (name, collection_id))
        conn.commit()
        conn.close()
        flash('Invitee added successfully')
        return redirect(url_for('view_collection', collection_id=collection_id))
    return render_template('add_invitee.html', collection_id=collection_id)

@app.route('/view_collection/<int:collection_id>', methods=['GET', 'POST'])
@login_required
def view_collection(collection_id):
    if not current_user.is_elevated():
        flash('You do not have permission to view collections')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        invitee_id = request.form['invitee_id']
        vote = request.form['vote']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO votes (user_id, invitee_id, vote) VALUES (?, ?, ?)", (current_user.id, invitee_id, vote))
        conn.commit()
        conn.close()
        flash('Your vote has been recorded')
        return redirect(url_for('view_collection', collection_id=collection_id))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name FROM collections WHERE id = ?", (collection_id,))
    collection = c.fetchone()
    c.execute("SELECT id, name FROM invitees WHERE collection_id = ?", (collection_id,))
    invitees = c.fetchall()
    c.execute("SELECT invitee_id, vote FROM votes WHERE user_id = ?", (current_user.id,))
    votes = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return render_template('view_collection.html', collection=collection, invitees=invitees, votes=votes, collection_id=collection_id)

@app.route('/remove_collection/<int:collection_id>')
@login_required
def remove_collection(collection_id):
    if not current_user.is_elevated():
        flash('You do not have permission to remove collections')
        return redirect(url_for('admin'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    c.execute("DELETE FROM invitees WHERE collection_id = ?", (collection_id,))
    c.execute("DELETE FROM votes WHERE invitee_id IN (SELECT id FROM invitees WHERE collection_id = ?)", (collection_id,))
    conn.commit()
    conn.close()
    flash('Collection removed successfully')
    return redirect(url_for('manage_collections'))

if __name__ == '__main__':
    app.run(debug=True)
