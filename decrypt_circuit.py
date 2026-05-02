from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import sys
import os
import glob

if len(sys.argv) != 4:
    print("Usage: python decrypt_circuit.py <private_key.pem> <encrypted_symkey.bin> <encrypted_circuit.bin>")
    sys.exit(1)

priv_key_name = sys.argv[1]
sym_key_name = sys.argv[2]
circuit_name = sys.argv[3]

with open(priv_key_name, "rb") as f: # load priv key
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
        )

with open(sym_key_name,"rb") as f : # load sym key
    encrypted_symkey = f.read()

#Decrypt the symmetric key using the private key
symmetric_key = private_key.decrypt(
    encrypted_symkey,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

with open(circuit_name, "rb") as f: #load encrypted circuit
    encrypted_data = f.read()

cipher = Fernet(symmetric_key)
decrypted_data = cipher.decrypt(encrypted_data)

with open("decrypted_circuit.json", "wb") as f:
    f.write(decrypted_data)

print("Decryption complete.")

for file in glob.glob("*.bin"): #supprimer les fichier encryptés ^_^
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")
