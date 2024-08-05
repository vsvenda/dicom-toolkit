from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()

# Print the generated key
print("Generated Key:", key.decode())
