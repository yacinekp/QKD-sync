from qiskit import transpile
from qiskit.qasm3 import loads
from qiskit_aer import AerSimulator
import socket
import json

HOST = "127.0.0.1"
PORT = 5555

# 1. receive
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1000000)

payload = json.loads(data.decode())

# 2. rebuild circuit
qc = loads(payload["qasm"])

# 3. measure
qc.measure(range(qc.num_qubits), range(qc.num_clbits))

# 4. simulation
sim = AerSimulator()
compiled = transpile(qc, sim)

result = sim.run(compiled, shots=1024).result()

bob_counts = result.get_counts(compiled)

print("\n \033[1;33m Bob counts:", bob_counts, "\033[0m \n")
print("PARAMÈTRES REÇUS \n")
print(f"Session ID : {payload['session_id']}")
print(f"Timestamp : {payload['timestamp']}")
print(f"Nombre de qubits : {payload['n_qubits']}")
print(f"Nombre de shots : {payload['shots']}")
print(f"Temps génération circuit : "f"{payload['temps_generation_circuit']:.6f} sec")
print(f"Phase drift : "f"{payload['decalage_phase']:.6f}")
print(f"Décalage horloge : "f"{payload['decalage_horloge']:.6f} sec")
print(f"Bruit estimé : "f"{payload['bruit_canal']:.6f}")

