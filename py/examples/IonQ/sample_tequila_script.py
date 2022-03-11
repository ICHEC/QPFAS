"""
This code was provided by Jakob Kottmann (jakob.kottmann@gmail.com)
"""
import tequila as tq
import qiskit
from qiskit_ionq import IonQProvider

U = tq.gates.Ry("a", 0) + tq.gates.CNOT(0,1)
H = tq.paulis.X(0)+tq.paulis.Z(1)
E = tq.ExpectationValue(H=H, U=U)

# this would be the qiskit default (same as calling compile without device option)
# this will work
#provider= qiskit.qiskit.providers.basicaer.BasicAer
#name="qasm_simulator"

# this is the ionq provider
# run will fail for me as the provider can not log in (no account registered on my laptop)
provider = IonQProvider()
name = "ionq_simulator"

# define qiskit device
device = {"provider":provider, "name":name}
# compile tequila object to backend
f = tq.compile(E, backend="qiskit", device=device)
# run it
evaluated = f(variables={"a":1.0}, samples=1000)
print(evaluated)

# in the same way you can use it with minimize
result = tq.minimize(E, backend="qiskit", device=device, samples=1000)