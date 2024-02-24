from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Define models
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    # One-to-many relationship with Book model
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

with app.app_context():
    db.create_all()

# Routes
@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    authors_data = [{'id': author.id, 'name': author.name} for author in authors]
    return jsonify({'status': 'success', 'data': authors_data}), 200

@app.route('/authors', methods=['POST'])
def create_author():
    name = request.form.get('name')
    if not name:
        return jsonify({'status': 'validation_error', 'data': {'name': ['This field is required']}}), 400
    new_author = Author(name=name)
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'status': 'success','data': 'Author created successfully'}), 201

@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    try:
        author = Author.query.get_or_404(author_id)
        author_data = {'id': author.id, 'name': author.name}
        return jsonify({'status': 'success', 'data': author_data}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400

@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    try:
        author = Author.query.get_or_404(author_id)
        name = request.form.get('name')
        author.name = name
        db.session.commit()
        return jsonify({'status': 'success', 'data': 'Author updated successfully'}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400

@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    try:
        author = Author.query.get_or_404(author_id)
        db.session.delete(author)
        db.session.commit()
        return jsonify({'status': 'success', 'data': 'Author deleted successfully'}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400


# Routes for books CRUD operations
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    books_data = [{'id': book.id, 'title': book.title, 'author': book.author.name} for book in books]
    return jsonify({'status': 'success', 'data': books_data}), 200

@app.route('/books', methods=['POST'])
def create_book():
    author_id = request.form.get('author_id')
    title = request.form.get('title')
    error = {}
    if not author_id:
        error['author_id'] = ['This field is required']
    if not title:
        error['title'] = ['This field is required']
    if error != {}:
        return jsonify({'status': 'validation_error', 'data': error}), 400
    
    author = Author.query.get(author_id)
    if author:
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'status': 'success', 'data': 'Book created successfully'}), 200
    else:
        return jsonify({'status': 'error', 'data': 'Author not found'}), 404

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        book_data = {'id': book.id, 'title': book.title, 'author': book.author.name}
        return jsonify({'status': 'success', 'data': book_data}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        title = request.form.get('title')
        if not title:
            return jsonify({'data': 'validation_error', 'data': {'title': ['This field is required']}})
        book.title = title
        db.session.commit()
        return jsonify({'status': 'success', 'data': 'Book updated successfully'}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return jsonify({'status': 'success', 'data': 'Book deleted successfully'}), 200
    except:
        return jsonify({'status': 'validation_error', 'data':{'url': ['Invalid Url']}}), 400

@app.route('/authors-books', methods=['GET'])
def get_authors_with_books():
    authors = Author.query.options(joinedload(Author.books)).all()
    
    authors_data = []
    for author in authors:
        author_data = {
            'id': author.id,
            'name': author.name,
            'books': [{'id': book.id, 'title': book.title} for book in author.books]
        }
        authors_data.append(author_data)
    
    return jsonify({'status': 'success', 'data': authors_data}), 200


if __name__ == '__main__':
    app.run(debug=True)
