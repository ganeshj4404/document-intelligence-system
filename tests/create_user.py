from getpass import getpass

from app.database import create_user
from app.services.auth_service import hash_password


username = input("Enter username: ").strip()
password = getpass("Enter password: ")

if not username:
    raise ValueError("Username cannot be empty.")

if not password:
    raise ValueError("Password cannot be empty.")

password_hash = hash_password(password)

user_id = create_user(username, password_hash)

print("User created successfully")
print("User ID:", user_id)
print("Username:", username)