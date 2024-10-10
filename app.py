import pytds
from flask import Flask, jsonify, request
from google.cloud import storage
import os

app = Flask(__name__)


# CREATE DATABASE assignemnt_1;
# CREATE LOGIN assignemnt_1 WITH PASSWORD = 'somPass@123';
# USE assignemnt_1;
# CREATE USER assignemnt_1 FOR LOGIN assignemnt_1;
# EXEC sp_addrolemember 'db_owner', 'assignemnt_1';


# SQL Server connection details
server = "172.27.176.3"
database = "assignemnt_1"
username = "assignemnt_1"
password = "***"


def create_connection():
    try:
        conn = pytds.connect(
            server=server,
            database=database,
            user=username,
            password=password,
            timeout=10.0,
        )
        return conn
    except Exception as e:
        return None


@app.route("/create_table", methods=["POST"])
def create_table():
    conn = create_connection()
    if not conn:
        return jsonify({"error": "Unable to connect to database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT PRIMARY KEY IDENTITY(1,1),
                name NVARCHAR(100),
                age INT
            );
        """)
        conn.commit()
        return jsonify({"message": "Table created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()


@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    age = data.get("age")

    if not name or not age:
        return jsonify({"error": "Invalid data"}), 400

    conn = create_connection()
    if not conn:
        return jsonify({"error": "Unable to connect to database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", (name, age))
        conn.commit()
        return jsonify({"message": f"User {name} added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()


@app.route("/get_users", methods=["GET"])
def get_users():
    conn = create_connection()
    if not conn:
        return jsonify({"error": "Unable to connect to database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        users = [{"id": row[0], "name": row[1], "age": row[2]} for row in rows]
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()


# GCP Bucket Operations
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage-key.json"
bucket_name = "upload-bucket-cbd"


def get_gcp_client():
    return storage.Client()


@app.route("/upload_file", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    client = get_gcp_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file.filename)

    try:
        blob.upload_from_file(file)
        return jsonify({"message": f"File {file.filename} uploaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/list_files", methods=["GET"])
def list_files():
    try:
        client = get_gcp_client()
        bucket = client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        files = [blob.name for blob in blobs]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
