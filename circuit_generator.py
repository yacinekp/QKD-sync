import random
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from datetime import datetime
from qiskit.qasm3 import dumps


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

