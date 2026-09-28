from app.database import create_user
from app.services.auth_service import hash_password


username = "admin"
password = "Admin@123"

password_hash = hash_password(password)

user_id = create_user(username, password_hash)

print("User created successfully")
print("User ID:", user_id)
print("Username:", username)