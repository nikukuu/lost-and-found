from werkzeug.security import generate_password_hash

hashed_password = generate_password_hash('ADMIN')
print(f"Hashed password for 'ADMIN': {hashed_password}")