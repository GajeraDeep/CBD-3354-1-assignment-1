import os
import streamlit as st
import requests

# Base URL for backend API
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:5000")


# Page 1: Database Operations
def database_page():
    st.title("Database Operations")

    if st.button("Create Table"):
        response = requests.post(f"{BASE_URL}/create_table")
        st.write(response.json())

    st.subheader("Add a New User")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1)

    if st.button("Add User"):
        data = {"name": name, "age": age}
        response = requests.post(f"{BASE_URL}/add_user", json=data)
        st.write(response.json())

    if st.button("Show Users"):
        response = requests.get(f"{BASE_URL}/get_users")
        users = response.json()
        if users:
            for user in users:
                st.write(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
        else:
            st.write("No users found.")


# Page 2: GCP Bucket Operations
def bucket_page():
    st.title("GCP Bucket Operations")

    st.subheader("Upload a File")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file:
        if st.button("Upload"):
            files = {"file": uploaded_file}
            response = requests.post(f"{BASE_URL}/upload_file", files=files)
            if not response.ok:
                st.write("Error: ")
                st.write(response.text)
            else:
                st.write(response.json())

    if st.button("List Files in Bucket"):
        response = requests.get(f"{BASE_URL}/list_files")
        files = response.json()
        if not response.ok:
            st.write("Error: ")
            st.write(response.text)
        else:
            if files:
                st.write("Files in bucket:")
                for file in files:
                    st.write(file)
            else:
                st.write("No files found.")


# App Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Database Operations", "GCP Bucket Operations"])

if page == "Database Operations":
    database_page()
else:
    bucket_page()
