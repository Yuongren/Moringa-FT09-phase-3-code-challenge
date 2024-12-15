from database.connection import get_db_connection

class Magazine:
    def __init__(self, id=None, name=None, category=None):
        """
        Initialize a new Magazine object.
        Either 'id' or 'name' and 'category' must be provided.
        If 'name' and 'category' are provided, the Magazine is inserted into the database, and the ID is set.
        If 'id' is provided, the Magazine is fetched from the database.
        """
        self._id = None
        self._name = None
        self._category = None
        
        if id is not None:
            self.load_by_id(id)
        elif name and category:
            self.create(name, category)
        else:
            raise ValueError("Either 'id' or ('name' and 'category') must be provided to create a Magazine.")
        
    def load_by_id(self, magazine_id):
        """ Load magazine data from the database using its ID. """
        if not isinstance(magazine_id, int) or magazine_id <= 0:
            raise ValueError('ID must be a positive integer.')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, category FROM magazines WHERE id = ?', (magazine_id,))
            result = cursor.fetchone()
            if result:
                self._id, self._name, self._category = magazine_id, result[0], result[1]
            else:
                raise ValueError(f"Magazine with id {magazine_id} not found in the database.")
    
    def create(self, name, category):
        """ Insert a new magazine into the database. """
        if not isinstance(name, str) or not (2 <= len(name) <= 16):
            raise ValueError("Name must be a string between 2-16 characters.")
        if not isinstance(category, str) or len(category) == 0:
            raise ValueError("Category must be a non-empty string.")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM magazines WHERE name = ? AND category = ?', (name, category))
            result = cursor.fetchone()
            if result:
                self._id = result[0]  # Existing magazine found, use its ID
                self._name = name
                self._category = category
            else:
                # Insert new magazine
                cursor.execute('INSERT INTO magazines (name, category) VALUES (?, ?)', (name, category))
                conn.commit()
                self._id = cursor.lastrowid
                self._name = name
                self._category = category

    @property
    def name(self):
        """ Return the magazine's name from the database if not already loaded. """
        if not self._name:
            self.load_by_id(self._id)
        return self._name
    
    @name.setter
    def name(self, new_name):
        """ Update the magazine's name in the database. """
        if not isinstance(new_name, str) or not (2 <= len(new_name) <= 16):
            raise ValueError("Name must be a string between 2-16 characters.")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE magazines SET name = ? WHERE id = ?', (new_name, self._id))
            conn.commit()
            self._name = new_name

    @property
    def category(self):
        """ Return the magazine's category from the database if not already loaded. """
        if not self._category:
            self.load_by_id(self._id)
        return self._category
    
    @category.setter
    def category(self, new_category):
        """ Update the magazine's category in the database. """
        if not isinstance(new_category, str) or len(new_category) == 0:
            raise ValueError("Category must be a non-empty string.")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE magazines SET category = ? WHERE id = ?', (new_category, self._id))
            conn.commit()
            self._category = new_category

    @classmethod
    def get(cls, magazine_id):
        """ Retrieve a Magazine by its ID. """
        if not isinstance(magazine_id, int) or magazine_id <= 0:
            raise ValueError('ID must be a positive integer.')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, category FROM magazines WHERE id = ?', (magazine_id,))
            result = cursor.fetchone()
            if result:
                return cls(id=result[0], name=result[1], category=result[2])
            else:
                raise ValueError(f"Magazine with id {magazine_id} not found.")
    
    def articles(self):
        """ Retrieve all articles published in this magazine. """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT articles.title, articles.content, articles.author_id
                FROM articles 
                WHERE articles.magazine_id = ?               
            """, (self._id,))
            return cursor.fetchall()

    def contributors(self):
        """ Retrieve all authors who have contributed to this magazine. """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT authors.name
                FROM authors
                INNER JOIN articles ON articles.author_id = authors.id
                WHERE articles.magazine_id = ?
            """, (self._id,))
            results = cursor.fetchall()
            from models.author import Author
            return [Author(name=result[0]) for result in results]

    def __repr__(self):
        """ String representation of the Magazine. """
        return f'<Magazine {self._name} of category {self._category}>'