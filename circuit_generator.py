import random
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from datetime import datetime
from qiskit.qasm3 import dumps

import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet

n_qubits = 10
tmps_creation= datetime.now().strftime("%d/%m/%Y_%H:%M:%S")
id_session =datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

shared_bits = [random.randint(0, 1) for _ in range(n_qubits)]
shared_bases = [random.randint(0, 1) for _ in range(n_qubits)]

qc = QuantumCircuit(n_qubits) #taille du circuit peut etre dynamique plus tard

# generation de la même serie de qubits et de bases
for i in range(n_qubits):
    if shared_bits[i] == 1:
        qc.x(i)                     # si le bit =1 alors appliquer flip gate au qubit |0>

    if shared_bases[i] == 1:         # si base = 1 appliquer hadamard gate au qubit
        qc.h(i)


# --- generation du fichier txt et le supprimer plus tard pour supprimer la trace
print(tmps_creation + "\n") # juste pour test
circuit_data = {
    "session_id": id_session,
    "timestamp": tmps_creation,
    "protocol": "BB84",
    "n_qubits": n_qubits,
    "shared_bits": shared_bits,
    "shared_bases": shared_bases,
    "circuit_qasm": dumps(qc)   #traduction de l'etat du circuit en langage qasm
}

fich_plain = f"circuit_data_{id_session}.json"
with open(fich_plain, "w") as f:
    json.dump(circuit_data, f, indent=2)

# --- Generatiion des 2 fichiers encryptés (ssl pour l'instant puis pqc plus tard)
#lire les 2 clés
with open("Alice_pubK.pem", "rb") as f:
    alice_public_key = serialization.load_pem_public_key(f.read())
with open("Bob_pubK.pem", "rb") as f:
    bob_public_key = serialization.load_pem_public_key(f.read())

with open(fich_plain, "rb") as f:
    plaintext_data = f.read()

#generer une clé aes et chiffrer le file avec (classique pour l'instant)
symmetric_key = Fernet.generate_key()
cipher = Fernet(symmetric_key)
encrypted_data = cipher.encrypt(plaintext_data)

encrypted_file = f"circuit_encrypted_{id_session}.bin"
with open(encrypted_file, "wb") as f:
    f.write(encrypted_data)

#chiffrage de la clé avec les clés pub de a et b
alice_encrypted_key = alice_public_key.encrypt(
    symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

with open(f"alice_symkey_{id_session}.bin", "wb") as f:
    f.write(alice_encrypted_key)
bob_encrypted_key = bob_public_key.encrypt(
    symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

with open(f"bob_symkey_{id_session}.bin", "wb") as f:
    f.write(bob_encrypted_key)

os.remove(fich_plain)
print("Plaintext supprimé.")
