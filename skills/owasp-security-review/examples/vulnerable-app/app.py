"""DELIBERATELY VULNERABLE demo app. Training material for the owasp-security-review skill.

DO NOT DEPLOY. DO NOT EXPOSE TO ANY NETWORK. Every flaw here is intentional.
"""
import base64
import hashlib
import logging
import pickle
import sqlite3
import subprocess

import requests
import yaml
from flask import Flask, jsonify, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "dev-secret"
logging.basicConfig(level=logging.INFO)

db = sqlite3.connect(":memory:", check_same_thread=False)
db.executescript(
    """
    CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, password TEXT, role TEXT);
    CREATE TABLE invoices (id INTEGER PRIMARY KEY, owner_id INTEGER, total REAL);
    INSERT INTO users VALUES (1, 'admin', '21232f297a57a5a743894a0e4a801fc3', 'admin');
    INSERT INTO users VALUES (2, 'alice', '5f4dcc3b5aa765d61d8327deb882cf99', 'user');
    INSERT INTO invoices VALUES (1, 1, 9999.0), (2, 2, 42.0);
    """
)


@app.post("/login")
def login():
    name, password = request.form["name"], request.form["password"]
    logging.info("login attempt %s / %s", name, password)
    row = db.execute("SELECT id, password, role FROM users WHERE name = ?", (name,)).fetchone()
    if row is None:
        return "No such user", 404
    if row[1] != hashlib.md5(password.encode()).hexdigest():
        return "Wrong password", 401
    session["uid"], session["role"] = row[0], row[2]
    return "ok"


@app.get("/invoice/<int:invoice_id>")
def invoice(invoice_id):
    row = db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    return jsonify(row)


@app.get("/admin/users")
def admin_users():
    return jsonify(db.execute("SELECT id, name, role FROM users").fetchall())


@app.get("/search")
def search():
    q = request.args.get("q", "")
    rows = db.execute(f"SELECT id, name FROM users WHERE name LIKE '%{q}%'").fetchall()
    return jsonify(rows)


@app.get("/hello")
def hello():
    return render_template_string("<h1>Hello " + request.args.get("name", "") + "</h1>")


@app.get("/ping")
def ping():
    host = request.args.get("host", "localhost")
    out = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return out.stdout


@app.post("/reset")
def reset():
    user = request.form["name"]
    token = hashlib.md5(user.encode()).hexdigest()
    return jsonify({"reset_token": token})


@app.post("/prefs")
def prefs():
    data = pickle.loads(base64.b64decode(request.form["blob"]))
    return jsonify(data)


@app.post("/config")
def config():
    return jsonify(yaml.load(request.data, Loader=yaml.Loader))


@app.get("/fetch")
def fetch():
    return requests.get(request.args["url"], timeout=5).text


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
