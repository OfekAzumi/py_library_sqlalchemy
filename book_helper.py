import json
import sqlite3
from flask import jsonify, request
from flask import Blueprint
from app import db, Book, Author

app_books = Blueprint('books', __name__,url_prefix='/books')

# get all books
@app_books.route('/books', methods=['GET'])
def get_books():
    # Query the database to get all books with author information
    books_data = Book.query.join(Author).add_columns(
        Book.id, Book.name, Book.genre, Author.name
    ).all()

    # Create a list of dictionaries with book information
    books_list = [
        {
            'id': book.id,
            'name': book.name,
            'genre': book.genre,
            'author': book[3]  # Author name from the query result
        }
        for book in books_data
    ]

    return jsonify(books_list), 200


# get specific book with id
@app_books.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Check if a book with the specified book_id exists in the database
        book = Book.query.get(book_id)

        if book is not None:
            return jsonify({'id': book.id, 'name': book.name, 'genre': book.genre, 'author': book.author.name}), 200
        else:
            return jsonify({'error': 'Book with the specific id not found'}), 404

@app_books.route('/books', methods=['POST'])
def add_book():
    data = request.json
    name = data.get('name')
    genre = data.get('genre')
    author_id = data.get('author_id')
    
    # First validation - if name hasn't been entered
    if not name:
        return jsonify({'error': 'Book name is required'}), 400

    # Second validation - if author_id is missing
    if author_id is None:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM authors')
        author_ids_data = [row[0] for row in cursor.fetchall()] # gets all author ids
        author_ids = json.dumps(author_ids_data) # makes the data readable
        conn.close()
        return jsonify({'error': f'Author ID is required. Possible author IDs: {author_ids}'}), 400

    # Third validation - check if the author with the given id exists
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM authors WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    conn.close()
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO books (name, genre, author_id) VALUES (?, ?, ?)', (name, genre, author_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book added successfully'}), 201


# #add book
# @books.route('/books', methods=['POST'])
# def add_book():
#     data = request.json
#     name = data.get('name')
#     genre = data.get('genre')
#     author_id = data.get('author_id')
#     #first validation - if name hasn't been entered
#     if not name :
#         return jsonify({'error': 'Book name is required'}), 400

#     #second validation - if author id hasn't been entered , display possible authors.
#     conn = sqlite3.connect('library.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT id FROM authors')
#     author_ids_data = [row[0] for row in cursor.fetchall()] # gets all author id's
#     author_ids = json.dumps(author_ids_data) # makes the data readble
#     print(author_ids)
#     if author_id not in author_ids:
#         conn.close()
#         return jsonify({'error': f'Invalid author ID. Possible author IDs: {author_ids}'}), 400

#     # third validation - check if the author with the given id exists
#     cursor.execute('SELECT id FROM authors WHERE id = ?', (author_id,))
#     author = cursor.fetchone()
#     if not author:
#         conn.close()
#         return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
#     cursor.execute('INSERT INTO books (name, genre, author_id) VALUES (?, ?, ?)', (name, genre, author_id))
#     conn.commit()
#     conn.close()
#     return jsonify({'message': 'Book added successfully'}), 201

#update book
@app_books.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    new_name = data.get('name')
    new_genre = data.get('genre')
    new_author_id = data.get('author_id')

    if not new_name and not new_genre and not new_author_id:
        return jsonify({'error': 'Book name , genre and authors id are required'}), 400
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    if not book:
        return jsonify({'error': 'Book with the specified ID does not exist'}), 400
    
    # Second validation - if author_id is missing
    if new_author_id is None:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM authors')
        author_ids_data = [row[0] for row in cursor.fetchall()] # gets all author ids
        author_ids = json.dumps(author_ids_data) # makes the data readable
        conn.close()
        return jsonify({'error': f'Author ID is required. Possible author IDs: {author_ids}'}), 400

    # Third validation - check if the author with the given id exists
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM authors WHERE id = ?', (new_author_id,))
    author = cursor.fetchone()
    conn.close()
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE books SET name = ?, genre = ?, author_id = ? WHERE id = ?', (new_name, new_genre, new_author_id, book_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book updated successfully'}), 200

# delete book 
@app_books.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    if not book:
        return jsonify({'error': 'Book with the specified ID does not exist'}), 400
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book deleted successfully'}), 200