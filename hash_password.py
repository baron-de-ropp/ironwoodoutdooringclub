import hashlib

def hash_password(password, salt="Athena", pepper="Minerva", iterations=41623):
    combined = salt + password + pepper
    hashed = combined.encode('utf-8')
    
    for _ in range(iterations):
        hashed = hashlib.sha512(hashed).digest()
    
    return hashed.hex()

if __name__ == "__main__":
    import getpass
    password = getpass.getpass("Enter password: ")
    hashed_password = hash_password(password)
    print(f"Hashed password: {hashed_password}")
