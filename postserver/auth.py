import functools

from flask import (Blueprint, flash, request)
from flask.json import jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from postserver.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is reuqired.'

    if error is None:
        try:
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password)),
                       )
            db.commit()
        except db.IntegrityError:
            error = f"User {username} is already registered."
        else:
            res = {
                'status': 'OK',
                'message': f'User {username} has registered sucessfully.'
            }
            return res


@bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    sql = 'SELECT * FROM user WHERE username=?'
    user = db.execute(sql, (username,)).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        return jsonify(user['id'])

    flash(error)
