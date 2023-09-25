import json
import sqlite3
from flask import jsonify, request
from flask import Blueprint

authors = Blueprint('authors', __name__,url_prefix='/authors')


# get all authors
@authors.route('/authors', methods=['GET'])
def get_authors():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM authors')
    authors = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(authors), 200

# get specific author with id
@authors.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    conn.close()
    if author:
        return jsonify({'id': author[0], 'name': author[1]}), 200
    else:
        return jsonify({'error': 'Author not found'}), 404
    
#add author
@authors.route('/authors', methods=['POST'])
def add_author():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Author name is required'}), 400

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO authors (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Author added successfully'}), 201

#update author
@authors.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.json
    new_name = data.get('name')

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM authors WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    conn.close()
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
    if not new_name:
        return jsonify({'error': 'Author name is required'}), 400

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE authors SET name = ? WHERE id = ?', (new_name, author_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Author updated successfully'}), 200



#delete author
@authors.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM authors WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    conn.close()
    if not author:
        return jsonify({'error': 'Author with the specified ID does not exist'}), 400
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM authors WHERE id = ?', (author_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Author deleted successfully'}), 200