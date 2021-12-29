from flask import (Blueprint, flash, request, jsonify, abort)
from postserver.db import get_db

bp = Blueprint('post', __name__)


@bp.route('/post', methods=['GET'])
def index():
    db = get_db()

    sql = 'SELECT p.id, title, body, created, author_id, u.username FROM post p JOIN user u ON p.author_id=u.id ORDER BY created DESC'
    posts = db.execute(sql).fetchall()
    result = []
    for post in posts:
        row = {}
        row['id'] = post['id']
        row['title'] = post['title']
        row['body'] = post['body']
        row['created'] = post['created']
        row['author_id'] = post['author_id']
        row['username'] = post['username']
        result.append(row)
    return jsonify({'posts': result})


@bp.route('/add', methods=['POST'])
def add_post():
    user_id = request.form['user_id']
    title = request.form['title']
    body = request.form['body']

    if not user_id:
        abort(403, 'Login is required.')
    elif not title:
        abort(403, 'Title is required.')
    else:
        db = get_db()
        sql = 'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)'
        db.execute(sql, (title, body, user_id))
        db.commit()
        return jsonify({'Post': f'{title} successfully added.'}), 201


def get_post(i):
    db = get_db()
    sql = 'SELECT p.id, title, body, created, author_id, u.username FROM post p JOIN user u ON p.author_id=u.id WHERE p.id=?'

    post = db.execute(sql, (i,)).fetchone()

    if post is None:
        abort(404, f"Post id {i} does not exist.")
    else:
        return post['author_id']


@bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    user_id = request.form['user_id']
    title = request.form['title']
    body = request.form['body']

    author_id = get_post(id)

    if not user_id or user_id != str(author_id):
        abort(403, "Unauthorized access.")
    elif not title:
        abort(403, 'Title is required.')
    else:
        db = get_db()
        sql = 'UPDATE post SET title=?, body=? WHERE id=?'
        db.execute(sql, (title, body, id))
        db.commit()
        return jsonify({'Post': f'{title} successfully updated.'}), 200


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    user_id = request.form['user_id']

    author_id = get_post(id)

    if not user_id or user_id != str(author_id):
        abort(403, "Unauthorized access.")
    else:
        db = get_db()
        sql = 'DELETE FROM post WHERE id=?'
        db.execute(sql, (id,))
        db.commit()
        return jsonify({'Post': f'id {id} deleted.'})
