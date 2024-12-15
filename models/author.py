

from database.connection import get_db_connection
from models.magazine import Magazine

class Author:
    def __init__(self, id=None, name=None):
        """
        Initialize a new Author object. Either 'id' or 'name' must be provided.
        If 'name' is provided, the Author is inserted into the database, and the ID is set.
        If 'id' is provided, the Author is fetched from the database.
        """
        self._id = None
        self._name = None
        
        if id is not None:
            self.load_by_id(id)
        elif name:
            self.create(name)
        else:
            raise ValueError("Either 'id' or 'name' must be provided to create an Author.")

    def load_by_id(self, author_id):
        """ Load author data from the database using their ID. """
        if not isinstance(author_id, int) or author_id <= 0:
            raise ValueError('ID must be a positive integer.')

        result = self.fetch_data('SELECT name FROM authors WHERE id = ?', (author_id,))
        if result:
            self._id, self._name = author_id, result[0]
        else:
            raise ValueError(f"Author with id {author_id} not found in the database.")

    def create(self, name):
        """ Insert a new author into the database. """
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Name must be a non-empty string.")
        
        result = self.fetch_data('SELECT id FROM authors WHERE name = ?', (name.strip(),))
        if result:
            self._id = result[0]  # Existing author found, use its ID
            self._name = name.strip()
        else:
            # Insert new author
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO authors (name) VALUES (?)', (name.strip(),))
                conn.commit()
                self._id = cursor.lastrowid
                self._name = name.strip()

    def fetch_data(self, query, params):
        """ Helper method to fetch data from the database. """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    @property
    def name(self):
        """ Return the author's name. If it's not already loaded, fetch it from the database. """
        if not self._name:
            result = self.fetch_data('SELECT name FROM authors WHERE id = ?', (self._id,))
            if result:
                self._name = result[0]
            else:
                raise ValueError("Author not found in the database.")
        return self._name
    
    @name.setter
    def name(self, new_name):
        """ Update the author's name in the database, if it's valid. """
        if not isinstance(new_name, str) or len(new_name.strip()) == 0:
            raise ValueError("Name must be a non-empty string.")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE authors SET name = ? WHERE id = ?', (new_name.strip(), self._id))
            conn.commit()
            self._name = new_name.strip()

    @property
    def id(self):
        """ Return the author's ID. """
        return self._id
    
    @id.setter
    def id(self, new_id):
        """ Update the author's ID, ensuring it is a valid positive integer. """
        if not isinstance(new_id, int) or new_id <= 0:
            raise ValueError('ID must be a positive integer.')
        self._id = new_id

    @classmethod
    def get(cls, author_id):
        """ Retrieve an Author by their ID. """
        if not isinstance(author_id, int) or author_id <= 0:
            raise ValueError('ID must be a positive integer.')
        
        result = cls.fetch_data('SELECT id, name FROM authors WHERE id = ?', (author_id,))
        if result:
            return cls(id=result[0], name=result[1])  # Return Author object
        else:
            raise ValueError(f"Author with id {author_id} not found.")
    
    def articles(self):
        """ Retrieve all articles written by this author. """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT articles.title, articles.content, articles.author_id, articles.magazine_id
                    FROM articles 
                    WHERE articles.author_id = ?               
                """, (self._id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching articles for author {self._id}: {e}")
            return []

    def magazines(self):
        """ Retrieve all magazines where this author has articles. """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT magazines.id, magazines.name, magazines.category
                    FROM magazines
                    INNER JOIN articles ON articles.magazine_id = magazines.id
                    WHERE articles.author_id = ?
                """, (self._id,))
                results = cursor.fetchall()
                return [Magazine(id=result[0], name=result[1], category=result[2]) for result in results]
        except Exception as e:
            print(f"Error fetching magazines for author {self._id}: {e}")
            return []

    def __repr__(self):
        """ String representation of the Author. """
        return f'<Author {self._name}>'
