from .connection import get_db_connection

def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Drop the old tables if they exist
        print("Dropping existing tables...")
        cursor.execute('DROP TABLE IF EXISTS articles')
        cursor.execute('DROP TABLE IF EXISTS magazines')
        cursor.execute('DROP TABLE IF EXISTS authors')

        # Create Authors Table
        print("Creating authors table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE -- Author name must be unique
            )
        ''')

        # Create Magazines Table
        print("Creating magazines table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS magazines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE, -- Magazine name must be unique
                category TEXT NOT NULL CHECK(LENGTH(category) > 0) -- Category cannot be empty
            )
        ''')

        # Create Articles Table
        print("Creating articles table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(LENGTH(title) BETWEEN 5 AND 50), -- Title length constraint
                content TEXT NOT NULL, -- Content is mandatory for articles
                author_id INTEGER NOT NULL, -- Must reference a valid author
                magazine_id INTEGER NOT NULL, -- Must reference a valid magazine
                FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE, -- Delete articles if author is deleted
                FOREIGN KEY (magazine_id) REFERENCES magazines (id) ON DELETE CASCADE -- Delete articles if magazine is deleted
            )
        ''')

        conn.commit()  # Commit changes
        print("Tables recreated successfully.")

    except Exception as e:
        print(f"Error creating tables: {e}")
    
    finally:
        conn.close()  # Ensure the connection is closed