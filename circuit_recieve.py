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

# 3. measurement
qc.measure(range(qc.num_qubits), range(qc.num_clbits))

# 4. simulate
sim = AerSimulator()
compiled = transpile(qc, sim)

result = sim.run(compiled, shots=1024).result()

bob_counts = result.get_counts(compiled)

print("Bob counts:", bob_counts)
