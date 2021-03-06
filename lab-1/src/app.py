from flask import request, Flask, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedSerializer
from flask_migrate import Migrate
from flasgger import Swagger

from db import db
from models import User
from config import SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/auth.db'
db.init_app(app)
migrate = Migrate(app, db)

app.config['SWAGGER'] = {
    'title': 'Users Management Service',
    'Description': 'A Sample User Management Service',
    'uiversion': 2
}
swagger = Swagger(app)


@app.route('/')
def welcome():
    return 'Welcome'

@app.route('/users/signup/', methods=['POST'])
def user_signup():
    """ New User Signup
    ---
    parameters:
      - in: "body"
        name: "body"
        description: "Signup a new User"
        required: true
        schema:
          $ref: "#/definitions/UserSignupRequest"
    responses:
      400:
        description: "Invalid input"
    definitions:
      UserSignupRequest:
        type: "object"
        properties:
          username:
            type: "string"
          first_name:
            type: "string"
          last_name:
            type: "string"
          email:
            type: "string"
          password:
            type: "string"
          description:
            type: "string"
          affiliation:
            type: "string"
    """
    user_data = request.json

    if user_data.get('username') is None or user_data.get('password') is None or user_data.get('email') is None or user_data.get('first_name') is None  or user_data.get('last_name') is None :
        return "Missing mandatory input",  400
    else :
        user = User(
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            username=user_data.get('username'),
            email=user_data.get('email'),
            password_hash=generate_password_hash(user_data.get('password')),
            description=user_data.get('description'),
            affiliation=user_data.get('affiliation'),
        )
        db.session.add(user)
        db.session.commit()

        # TODO: DB error handling

        return jsonify({'user_id': user.id})


@app.route('/users/login/', methods=['POST'])
def user_login():
    """ User login
    ---
    parameters:
      - in: "body"
        name: "body"
        description: "Login to get a auth token"
        required: true
        schema:
          $ref: "#/definitions/UserLoginRequest"
    responses:
      401:
        description: "Invalid Credentials"
    definitions:
      UserLoginRequest:
        type: "object"
        properties:
          username:
            type: "string"
          password:
            type: "string"
    """
    user_details = request.json
    username = user_details.get('username')
    password = user_details.get('password')
    user = User.query.filter_by(username=username).first()
    validLogin = False
    if user != None :
        password_hash = user.password_hash
        if check_password_hash(password_hash, password):
            # generate a token
            s = TimedSerializer(SECRET_KEY)
            token = s.dumps({'user_id': user.id})
            validLogin = True

    if validLogin :
        return "Welcome %s, Your token is %s " % (user.first_name, token)
    else:
        return 'Invalid Credentials', 401


@app.route('/users/check/', methods=['POST'])
def check_token():
    """ Check if a user's auth token is valid
    ---
    parameters:
      - in: "body"
        name: "body"
        description: "Check if an auth token is valid"
        required: true
        schema:
          $ref: "#/definitions/UserTokenCheckRequest"
    responses:
        401:
          description: "Invalid Credentials"
    definitions:
      UserTokenCheckRequest:
        type: "object"
        properties:
          token:
            type: "string"
    """
    token = request.json.get('token')
    user = User.verify_auth_token(token)
    if user:
        return jsonify({'user_id': user.id})
    else:
        return 'Invalid Credentials', 401


@app.route('/users/<int:user_id>/')
def user_details(user_id):
    """ Return user details
    ---
    /users/{user_id}/:
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: Numeric ID of the user to get.
    responses:
      200:
        description: A User object
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: The first name of the user
            last_name:
              type: string
              description: The last name of the user
            username:
              type: string
              description: The user name.
            description:
              type: string
              description: A short description about the user.
            affiliation:
              type: string
              description: A group/organisation the user is affiliated with.
      401:
        description: "Invalid Credentials"
    """
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'description': user.description,
            'affiliation': user.affiliation,
        })
    else:
        return 'User not found', 404



@app.route('/users/all/')
def list_all_users():
    """ List all users
    ---
    /users/all/:


    responses:
      200:
        description: A User object
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: The first name of the user
            last_name:
              type: string
              description: The last name of the user
            username:
              type: string
              description: The user name.
            description:
              type: string
              description: A short description about the user.
            affiliation:
              type: string
              description: A group/organisation the user is affiliated with.
      401:
        descriptiosn: "Invalid Credentials"
    """
    users = User.query.all()
    if users:
        userList = []
        for user in users :
            userList.append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'description': user.description,
            'affiliation': user.affiliation,
            })
        return jsonify({"users" : userList})
    else:
        return 'No Users signed up yet', 404


@app.route('/users/affiliation/<string:affiliation>/')
def user__affiliation(affiliation):
    """ Search users affiliated with a group/organisation
    ---
    /users/{user_id}/:
    parameters:
      - in: path
        name: affiliation
        type: string
        required: true
        description: Affiliation of the user.
    responses:
      200:
        description: A User object
        schema:
          type: object
          properties:
            first_name:
              type: string
              description: The first name of the user
            last_name:
              type: string
              description: The last name of the user
            username:
              type: string
              description: The user name.
            description:
              type: string
              description: A short description about the user.
            affiliation:
              type: string
              description: A group/organisation the user is affiliated with.
      401:
        description: "Invalid Credentials"
    """
    users = User.query.filter_by(affiliation=affiliation).all()
    if users:
        userList = []
        for user in users :
            userList.append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'description': user.description,
            'affiliation': user.affiliation,
            })
        return jsonify({"users" : userList})
    else:
        return 'No Users present for this affiliation', 404

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=404, text=str(e)), 404


if __name__ == '__main__':
    app.run(port=5000)
