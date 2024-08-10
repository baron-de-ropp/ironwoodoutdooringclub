import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create users table with role column
c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')

# Insert a default admin user
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'password', 'elevated'))

# Create collections table
c.execute('''CREATE TABLE collections (id INTEGER PRIMARY KEY, name TEXT)''')

# Create invitees table
c.execute('''CREATE TABLE invitees (id INTEGER PRIMARY KEY, name TEXT, collection_id INTEGER, 
            FOREIGN KEY(collection_id) REFERENCES collections(id))''')

conn.commit()
conn.close()
