from flask_app.config.mysqlconnection import connectToMySQL
# Flash messages import
from flask import flash
# REGEX import
import re
# Create a regular expression object that we'll use later
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Database name
db = "game_vault_schema"

# User class
class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    # Classmethod for saving a new user.
    @classmethod
    def save_user(cls, data):
        # print('Save the user method...')
        query = """INSERT INTO users (first_name, last_name, email, password)
                VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"""
        # print('Saving the user method was successful...')
        return connectToMySQL(db).query_db(query, data)

    # Classmethod for getting a user by their email address.
    @classmethod
    def get_user_by_email(cls, data):
        # print('Getting the user by email method...')
        query = """SELECT * FROM users WHERE email = %(email)s;"""
        results = connectToMySQL(db).query_db(query, data)
        if len(results) < 1:
            return False
        # print('Getting the user by email method was successful...')
        return cls(results[0])

    # Classmethod for updating a user's details.
    @classmethod
    def update_user(cls, data):
        query = """UPDATE users SET email=%(email)s, password=%(password)s,
                updated_at=NOW() WHERE id = %(id)s;"""
        return connectToMySQL(db).query_db(query, data)

    # Classmethod for getting a user by their ID.
    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])

    # Staticmethod for validating a user.
    @staticmethod
    def validate_user(data):
        # print('Validating the user staticmethod...')
        # Set is_valid to True.
        is_valid = True
        # Test if the first name is at least 2 characters.
        if len(data['first_name']) < 2:
            flash("First name is required", "register")
            is_valid = False
        # Test if the last name is at at least 2 characters.
        if len(data['last_name']) < 2:
            flash("Last name is required.", "register")
            is_valid = False
        # Test whether email matches the  EMAIL_REGEX pattern.
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address." , "register")
            is_valid = False
        query = """SELECT * FROM users
                WHERE email = %(email)s;"""
        results = connectToMySQL(db).query_db(query, data)
        # Test if the email is already being used.
        if len(results) != 0:
            flash("This email is already being used.", "register")
            is_valid = False
        # Test if the password is a certain amount of characters.
        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.", "register")
            is_valid = False
        # Test if passwords match.
        if data['password'] != data['confirm_password']:
            flash("Password does not match.", "register")
            is_valid = False
        # print("Validating the user staticmethod was successful...")
        return is_valid

    # Staticmethod for editing a user's email/password.
    @staticmethod
    def validate_edit_user(data):
        is_valid = True
        if len(data['email']) < 10:
            is_valid = False
            flash("Email must be at least 10 characters", "edit_user")
        if len(data['password']) < 8:
            is_valid = False
            flash("Password must be at least 8 characters", "edit_user")
        if  data['password'] != data['confirm_password']:
            is_valid = False
            flash("Passwords must match", "edit_user")
        return is_valid