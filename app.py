from flask import Flask, render_template, request, jsonify
import os
import sqlite3
import uuid
import numpy as np

app = Flask(__name__)

UPLOAD_MISSING_FOLDER = "static/uploads_missing"
UPLOAD_FOUND_FOLDER = "static/uploads_found"

os.makedirs(UPLOAD_MISSING_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOUND_FOLDER, exist_ok=True)

app.config['UPLOAD_MISSING_FOLDER'] = UPLOAD_MISSING_FOLDER
app.config['UPLOAD_FOUND_FOLDER'] = UPLOAD_FOUND_FOLDER

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missing_children (
            id TEXT PRIMARY KEY, name TEXT, age INTEGER, id_mark TEXT,
            home_location TEXT, missing_location TEXT, parent_contact TEXT, email TEXT, image_path TEXT)
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS found_children (
            id TEXT PRIMARY KEY, image_path TEXT,
            found_location TEXT, finders_contact_number TEXT, identification_mark TEXT)
    """)
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload_missing', methods=['POST'])
def upload_missing():
    image = request.files['image']
    unique_id1 = str(uuid.uuid4())
    image_path = f"uploads_missing/{unique_id1}.jpg"
    image.save(os.path.join("static", image_path))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO missing_children (id, name, age, id_mark, home_location, missing_location, parent_contact, email, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (unique_id1, request.form['name'], request.form['age'], request.form['id_mark'], 
          request.form['home_location'], request.form['missing_location'], 
          request.form['parent_contact'], request.form['email'], image_path))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Missing child report submitted successfully!", "id": unique_id1})

@app.route('/upload_found', methods=['POST'])
def upload_found():
    file = request.files['child_image']
    unique_id2 = str(uuid.uuid4())
    filename = f"{unique_id2}.jpg"
    file_path = f"uploads_found/{filename}"
    file.save(os.path.join("static", file_path))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO found_children (id, image_path, found_location, finders_contact_number, identification_mark)
        VALUES (?, ?, ?, ?, ?)
    """, (unique_id2, file_path, request.form['found_location'], request.form['finders_contact_number'], request.form['identification_mark']))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Found child report submitted successfully!", "id": unique_id2})

@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM missing_children")
    missing_children = cursor.fetchall()
    
    cursor.execute("SELECT * FROM found_children")
    found_children = cursor.fetchall()
    
    conn.close()
    
    return render_template("admin.html", missing_children=missing_children, found_children=found_children)

@app.route("/matches")
def view_matches():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, finders_contact, found_loc, parent_contact, mail, image_path FROM match_children")
    matches = cursor.fetchall()
    conn.close()
    return render_template("matches.html", matches=matches)

if __name__ == "__main__":
    app.run(debug=True)
