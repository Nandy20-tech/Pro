def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                );
            ''')
            print("Database initialized.")
if __name__ == '__main__':
    init_db()   # ✅ This line creates the table if not already there
    app.run(debug=True)
