# -*- coding: utf-8 -*-

from app import app
from models import User
from flask import Flask
from flask import request, url_for, jsonify, g
from flask.ext.httpauth import HTTPBasicAuth
from itsdangerous import URLSafeTimedSerializer
import re

auth = HTTPBasicAuth()

def filterUserModel(user):
    return {
        'uid': user.uid,
        'email': user.email,
        'name': user.name,
        'age': user.age,
        #'validate': user.validate,
        'occupation': user.occupation,
        'education': user.education,
        'location': user.location
    }

def generate_validate_email(email):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return s.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def validate_token(token, expiration=3600): # email validate expiration 1 hours
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'message': '404 not found'}), 404

@app.route('/validate/<token>')
def validate_email(token):
    try:
        email = validate_token(token)
    except:
        return 'The confirmation link is invalid or has expired.', 200

    user = User.objects(email=email).first()
    if user is not None:
        if user.validate:
            return 'Account already confirmed. Please login.', 200
        else:
            user.update(set__validate=True)
            return 'You have confirmed your account. Thanks!', 200
    return 'The confirmation link is invalid or has expired.', 200


@app.route('/api/v1/user/create', methods=['POST'])
def reg_user():
    email = request.json.get('email') or ''
    pwd   = request.json.get('password') or ''

    if re.match(r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$', email) \
        or len(pwd) < 7 \
        or User.objects(email=email).first() is not None:
        return jsonify({'Success': 0, 'message': 'Invalid!'}), 400

    user = User(email=email, password=pwd)
    # password to hash
    user.saveNewsUser()
    return jsonify({'email': user.email}), 201, {'Location': url_for('get_user', uid = user.uid, _external = True)}




@app.route('/api/v1/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'Success': 1, 'token': token.decode('ascii'), 'duration': 600})


@auth.verify_password
def verify_password(email_or_token, psw):
    # verify email or token
    user = User.verify_auth_token(email_or_token)
    if not user:
        user = User.objects(email=email_or_token).first()
        if not user or not user.verify_password(psw):
            return False
    g.user = user
    return True


# API

# GET All users /api/v1/users
@app.route('/api/v1/users')
def get_users():
    # print jsonify({'a': 1, 'b': '{"c":1}'})
    # get qyert: request.args.get('s')
    _ref = map(filterUserModel, User.objects.all() or [])
    return jsonify({'Success': 1, 'data': _ref})

# GET /api/v1/users/{uid}
@app.route('/api/v1/users/<int:uid>')
def get_user(uid):
    user = User.objects(uid=uid).first()
    if not user:
        return jsonify({'Success': 0, 'message': 'not user!'}), 400
    return jsonify({'Success': 1, 'data': filterUserModel(user)})

# POST or PUT /api/v1/users/update/{uid} send body data
@app.route('/api/v1/users/update/<int:uid>', methods=['POST', 'PUT'])
@auth.login_required
def user_update(uid):
    if uid != g.user.uid:
        return jsonify({'Success': 0, 'message': 'wu quan xian!'}), 200

    user = User.objects(uid=uid).first()
    if not user:
        return jsonify({'Success': 0, 'message': 'not user!'}), 200
    # filter safe fields
    _ref = {}
    for key in ['name','age','occupation','education','location']:
        if request.json.get(key) is not None:
            _ref[key] = request.json.get(key)

    _ref = dict(("set__%s" % k, v) for k,v in _ref.iteritems())
    user.update(**_ref)
    return jsonify({'Success': 1}), 200

# POST or DELETE /api/v1/users/delete/{uid}
@app.route('/api/v1/users/delete/<int:uid>', methods=['POST', 'DELETE'])
@auth.login_required
def user_delete(uid):
    if uid == g.user.uid or g.user.uid > 1:
        return jsonify({'Success': 0, 'message': 'wu quan xian!'}), 200

    return jsonify({'Success': User.objects(uid=uid).delete()}), 200

'''
@app.route('/api/v1/problems/create', methods=['POST'])
def p_create():
    question = request.json.get('q') or ''
    print type(question)
    return jsonify({'Success': 1}), 200
'''
