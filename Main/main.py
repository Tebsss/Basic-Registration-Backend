#!/usr/bin/python
from logging import exception
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT NOT NULL,
                contact TEXT NOT NULL
            );
        ''')

        conn.commit()
        print("User table created successfully")
    except:
        print("User table creation failed - Maybe table")
    finally:
        conn.close()

create_db_table()


#functions
def insert_user(user):
    inserted_user = {}


    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, firstname, lastname, address, email, contact) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (user['username'], user['password'], user['firstname'], user['lastname'], user['address'], user['email'], user['contact']) 
        )
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_user

def get_by_username(username):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["user_id"] = row["user_id"]
        user["username"] = row["username"]
    except:
        user = {}

    finally: conn.close()

    return user


def save_step1(user):
    inserted_user = {}
    existing_user = get_by_username(user['username'])

    if bool(existing_user):
   
        # raise Exception("wrong login")
        return { "data": {"error": "existing username"}, "status": 409 }
    else:
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password, firstname, lastname, address, email, contact) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (user['username'], user['password'], '', '', '', '', '') 
            )
            conn.commit()
            inserted_user = get_user_by_id(cur.lastrowid)

        except:
            conn.rollback()

        finally:
            conn.close()

    return { "data": inserted_user, "status": 200 }


def save_step2(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET firstname = ?, lastname = ?, address = ? WHERE user_id = ?", 
            (user["firstname"], user["lastname"], user["address"], user["user_id"])
        )
        conn.commit()
        inserted_user = get_user_by_id(user["user_id"])
    except:
        conn().rollback()

    finally:
        conn.close()

    return { "data": inserted_user, "status": 200 }

def save_step3(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET email = ?, contact = ? WHERE user_id = ?", 
            (user["email"], user["contact"], user["user_id"])
        )
        conn.commit()
        inserted_user = get_user_by_id(user["user_id"])
    except:
        conn().rollback()

    finally:
        conn.close()

    return { "data": inserted_user, "status": 200 }

def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["username"] = i["username"]
            user["password"] = i["password"]
            user["firstname"] = i["firstname"]
            user["lastname"] = i["lastname"]
            user["address"] = i["address"]
            user["email"] = i["email"]
            user["contact"] = i["contact"]
            users.append(user)

    except:
        users = []

    return users


def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        user["user_id"] = row["user_id"]
        user["username"] = row["username"]
        user["password"] = row["password"]
        user["firstname"] = row["firstname"]
        user["lastname"] = row["lastname"]
        user["address"] = row["address"]
        user["email"] = row["email"]
        user["contact"] = row["contact"]

    except:
        user = {}

    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET firstname = ?, lastname = ?, address = ?", (user["firstname"], user["lastname"], user["address"],))
        conn.commit()
        #return the user
        updated_user = get_user_by_id(user["user_id"])

    except:
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()

    return updated_user




def get_login(payload):
    users = []

    username = payload.get('username')
    password = payload.get('password')

    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        rows = cur.fetchall()

        if len(rows) < 1:
            raise Exception("wrong login")
        else:

            for i in rows:
                user = {}
                user["user_id"] = i["user_id"]
                user["username"] = i["username"]
                user["password"] = i["password"]
                user["firstname"] = i["firstname"]
                user["lastname"] = i["lastname"]
                user["address"] = i["address"]
                user["email"] = i["email"]
                user["contact"] = i["contact"]
                
                
                users.append(user)

            

    except:
        raise Exception("wrong login")

    return users





app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/login', methods=['GET'])
def api_get_login():
    payload = request.args
    return jsonify(get_login(payload))

@app.route('/api/users/step1/save',  methods = ['POST'])
def api_step1():
    user = request.get_json(force=True)
    res = save_step1(user)
    
    return jsonify(res["data"]), res["status"]

@app.route('/api/users/step2/save',  methods = ['POST'])
def api_step2():
    user = request.get_json(force=True)

    # return user
    res = save_step2(user)
    
    return jsonify(res["data"]), res["status"]

@app.route('/api/users/step3/save',  methods = ['POST'])
def api_step3():
    user = request.get_json(force=True)

    # return user
    res = save_step3(user)
    
    return jsonify(res["data"]), res["status"]

if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=True)
    app.run()