from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps
from qiskit_aer import AerSimulator
from qiskit import transpile
import socket
from datetime import datetime
import json
import time
import random

#la fonction de generation du circuit de ref
def build_quantum_circuit():
    qc = QuantumCircuit(4,4, name="reference circuit") # 4 qubits pour les 4 etats 0 1 + -
    # q0 = |0>
    qc.x(1) #q1 = |1>
    qc.h(2) #qc2 = |+>
    qc.x(3)
    qc.h(3) # qc3 = |->
    return qc

#alice genere ce circuit et mesurre le temps de generation:
gen_debut = time.time()
ref_qc = build_quantum_circuit()
gen_fin = time.time()
tps_gen = gen_fin - gen_debut

#serialisation en QASM
qasm_circuit = dumps(ref_qc)

#parametres de synchronisation simulés
decalage_phase = random.uniform(-0.05, 0.05)
decalage_horloge = random.uniform(-0.001, 0.001)
bruit_canal = random.uniform(0.0, 0.03)
shots = 1024

#envoi de données
data_to_send = {
    "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "n_qubits": 4,
    "shots" : shots,
    "qasm": qasm_circuit,
    "temps_generation_circuit" : tps_gen,
    "decalage_horloge" : decalage_horloge,
    "decalage_phase" : decalage_phase,
    "nb_essais" : shots,
    "bruit_canal" : bruit_canal,
    "timestamp": datetime.now().isoformat()
    }
file_send ="ref_circuit_param.json"
with open(file_send, "w") as f:
    json.dump(data_to_send, f, indent=2)

#alice crée une copie de la preparation (et non des etats quantiques) puis mesure de son coté
ref_copy = ref_qc.copy()
ref_copy.measure(range(4), range(4))
sim = AerSimulator()

#tps compilation
compil_deb = time.time()
compiled = transpile(ref_copy, sim)
compil_fin =time.time()

#tps execution
exec_deb = time.time()
result = sim.run(compiled, shots=1024).result()
exec_fin = time.time()

counts = result.get_counts()

#affichage des parametres chez alice
print("\n \033[1;33m Counts :", counts,' \033[0m\n')
print(f"Temps génération circuit : {tps_gen:.6f} sec")
print(f"Temps compilation : {compil_fin - compil_deb:.6f} sec")
print(f"Temps exécution : {exec_fin - exec_deb:.6f} sec")
print(f"décalage de phase simulé : {decalage_phase:.6f}")
print(f"Décalage d'horloge simulé : {decalage_horloge:.6f} sec")
print(f"Bruit estimé simulé: {bruit_canal:.6f} \n")
# envoi a travers sockets
HOST = '127.0.0.1'
PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Alice en écoute sur {HOST}:{PORT} ... En attente de Bob")

    conn, addr = s.accept()
    print(f"Bob connecté depuis {addr}")

    import pickle
    conn.sendall(json.dumps(data_to_send).encode())
    print("  Reference circuit envoyé avec succès à Bob")

    conn.close()

