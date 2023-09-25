import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify

app = Flask(__name__)

# Specify the full path to the database file (e.g., in the current directory)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path  # Use SQLite as the database
db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

# with open, check if db exist - else -> create db
def create_book_author_database():
    if not os.path.exists('library.db'):
        with app.app_context():
            db.create_all()
            print("Database created.")
    else:
        print("Database already exists.")

# get all books
@app.route('/books', methods=['GET'])
def get_books():
    # Query all books and construct the list of dictionaries
    books = Book.query.all()
    books_list = [
        {
            'id': book.id,
            'name': book.name,
            'genre': book.genre,
            'author': book.author.name
        }
        for book in books
    ]

    return jsonify(books_list), 200

# get specific book with id
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Check if a book with the specified book_id exists in the database
    book = Book.query.get(book_id)

    if book is not None:
        return jsonify({'id': book.id, 'name': book.name, 'genre': book.genre, 'author': book.author.name}), 200
    else:
        return jsonify({'error': 'Book with the specific id not found'}), 404

# add book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    name = data.get('name')
    genre = data.get('genre')
    author_id = data.get('author_id')
    
    # First validation - if name, genre and authorid hasn't been entered
    if not name or not genre or not author_id:
        author_ids = [author.id for author in Author.query.all()] # gets all author ids
        return jsonify({'error': f'Book name, genre and author id is required. Possible author IDs: {author_ids}'}), 400

    # Second validation - check if the author with the given id exists
    author = Author.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
    new_book = Book(name=name, genre=genre, author_id=author_id)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201

# update book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    new_name = data.get('name')
    new_genre = data.get('genre')
    new_author_id = data.get('author_id')

    if not new_name or not new_genre or new_author_id is None:
        author_ids = [author.id for author in Author.query.all()] # gets all author ids
        return jsonify({'error': f'Book name, genre, or author ID is required. Possible author IDs: {author_ids}'}), 400

    # Check if the book with the specified ID exists
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book with the specified ID does not exist'}), 404

    # Update book attributes if provided
    if new_name: book.name = new_name
    if new_genre: book.genre = new_genre
    if new_author_id is not None:
        # Check if the new_author_id corresponds to an existing author
        author = Author.query.get(new_author_id)
        if author:
            book.author = author
        else:
            return jsonify({'error': 'Author with the specified ID does not exist'}), 400

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Book updated successfully'}), 200

# get all authors
@app.route('/authors', methods=['GET'])
def get_authors():
    # Query the database to get all authors
    authors = Author.query.all()

    # Create a list of dictionaries with author information
    authors_list = [
        {
            'id': author.id,
            'name': author.name,
        }
        for author in authors
    ]

    return jsonify(authors_list), 200

# get specific author with id
@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    # Check if an author with the specified author_id exists in the database
    author = Author.query.get(author_id)

    if author is not None:
        return jsonify({'id': author.id, 'name': author.name}), 200
    else:
        return jsonify({'error': 'Author with the specific id not found'}), 404

# add author
@app.route('/authors', methods=['POST'])
def add_author():
    data = request.json
    name = data.get('name')
    # First validation - if name, genre and authorid hasn't been entered
    if not name :
        return jsonify({'error': 'Author name is required'}), 400
    
    new_author = Author(name=name)
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'message': 'Author added successfully'}), 201

# update author
@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({'error': 'Author name is required.'}), 400

    # Check if the author with the specified ID exists
    author = Author.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 404

    # Update author attributes if provided
    if new_name: author.name = new_name
    db.session.commit()
    return jsonify({'message': 'Author updated successfully'}), 200

if __name__ == '__main__':
    create_book_author_database()
    app.run(debug=True)

