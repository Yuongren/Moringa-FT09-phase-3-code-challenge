
from database.connection import get_db_connection
from models.author import Author
from models.magazine import Magazine

class Article:
    def __init__(self, id=None, title=None, content=None, author_id=None, magazine_id=None):
        """
        Initialize a new Article object or fetch an existing one from the database.
        """
        self._id = None
        self._title = None
        self._content = None
        self._author_id = None
        self._magazine_id = None

        if id is not None:
            self.load_by_id(id)
        else:
            self.create(title, content, author_id, magazine_id)

    def load_by_id(self, article_id):
        """ Fetch an existing article by its ID from the database. """
        result = self.fetch_data("""
            SELECT id, title, content, author_id, magazine_id
            FROM articles
            WHERE id = ?
        """, (article_id,))
        
        if result:
            self._id, self._title, self._content, self._author_id, self._magazine_id = result
        else:
            raise ValueError(f"Article with id {article_id} not found in the database.")

    def create(self, title, content, author_id, magazine_id):
        """ Create a new article in the database. """
        if not (isinstance(title, str) and 5 <= len(title) <= 50):
            raise ValueError("Title must be a string between 5-50 characters.")
        if not (isinstance(content, str) and len(content.strip()) > 0):
            raise ValueError("Content must be a non-empty string.")
        if not (isinstance(author_id, int) and author_id > 0):
            raise ValueError("Author ID must be a positive integer.")
        if not (isinstance(magazine_id, int) and magazine_id > 0):
            raise ValueError("Magazine ID must be a positive integer.")
        
        # Verify that the author and magazine exist
        try:
            author = Author.get(author_id)
        except ValueError:
            raise ValueError(f"Author with id {author_id} does not exist.")
        
        try:
            magazine = Magazine.get(magazine_id)
        except ValueError:
            raise ValueError(f"Magazine with id {magazine_id} does not exist.")
        
        # Insert the article into the database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO articles (title, content, author_id, magazine_id)
                VALUES (?, ?, ?, ?)
            """, (title.strip(), content.strip(), author_id, magazine_id))
            conn.commit()

            # Set attributes after successful insertion
            self._id = cursor.lastrowid
            self._title = title.strip()
            self._content = content.strip()
            self._author_id = author_id
            self._magazine_id = magazine_id

    def fetch_data(self, query, params):
        """ Helper method to fetch data from the database. """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    @property
    def id(self):
        """Return the article's ID."""
        return self._id

    @property
    def title(self):
        """Return the article's title."""
        return self._title

    @property
    def content(self):
        """Return the article's content."""
        return self._content

    @content.setter
    def content(self, new_content):
        """Update the article's content in the database."""
        if not (isinstance(new_content, str) and len(new_content.strip()) > 0):
            raise ValueError("Content must be a non-empty string.")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE articles
                SET content = ?
                WHERE id = ?
            """, (new_content.strip(), self._id))
            conn.commit()
            self._content = new_content.strip()

    @property
    def author(self):
        """Return the Author object associated with this article."""
        return Author.get(self._author_id)

    @property
    def magazine(self):
        """Return the Magazine object associated with this article."""
        return Magazine.get(self._magazine_id)

    def __repr__(self):
        """Return a string representation of the Article."""
        return f"<Article '{self.title}' by Author ID {self._author_id}>"
