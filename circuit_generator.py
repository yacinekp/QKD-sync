from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps
from qiskit_aer import AerSimulator
from qiskit import transpile
import socket
from datetime import datetime
import json

#la fonction de generation du circuit de ref
def build_quantum_circuit():
    qc = QuantumCircuit(4,4, name="reference circuit") # 4 qubits pour les 4 etats 0 1 + -
    # q0 = |0>
    qc.x(1) #q1 = |1>
    qc.h(2) #qc2 = |+>
    qc.x(3)
    qc.h(3) # qc3 = |->
    return qc

#alice genere ce circuit :
ref_qc = build_quantum_circuit()
qasm_circuit = dumps(ref_qc)

#envoi de données
data_to_send = {
    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "n_qubits": 4,
    "qasm": qasm_circuit,
    "timestamp": datetime.now().isoformat()
    }
file_send ="ref_circuit_param.json"
with open(file_send, "w") as f:
    json.dump(data_to_send, f, indent=2)

#alice crée une copie de la preparation (et non des etats quantiques) puis mesure de son coté
ref_copy = ref_qc.copy()
ref_copy.measure(range(4), range(4))
sim = AerSimulator()
compiled = transpile(ref_copy, sim)
result = sim.run(compiled, shots=1024).result()
counts = result.get_counts()
print(counts)

# envoi a travers sockets
HOST = '127.0.0.1'
PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Alice en écoute sur {HOST}:{PORT} ... En attente de Bob")

    conn, addr = s.accept()
    print(f"Bob connecté depuis {addr}")

    import pickle
    conn.sendall(json.dumps(data_to_send).encode())
    print("  Reference circuit envoyé avec succès à Bob")

    conn.close()

