#!/usr/bin/env python3

import os
import sys
import argparse
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from decimal2binary import *
import dimod
from dwave.system import EmbeddingComposite, DWaveSampler
import neal

sampler_qpu = EmbeddingComposite(DWaveSampler())
sampler_sim = neal.SimulatedAnnealingSampler()

np.set_printoptions(precision=1, linewidth=200, suppress=True)

parser = argparse.ArgumentParser("Quantum unfolding")
parser.add_argument('-l', '--lmbd', default=0.00)
parser.add_argument('-n', '--nreads', default=10000)
parser.add_argument('-b', '--backend', default='cpu')  # [cpu, qpu, sim]
args = parser.parse_args()

num_reads = int(args.nreads)

# truth-level:
x = [5, 8, 12, 6, 2]

# response matrix:
R = [[1, 2, 0, 0, 0],
     [1, 2, 1, 1, 0],
     [0, 1, 3, 3, 0],
     [0, 2, 2, 3, 2],
     [0, 0, 0, 1, 2]
     ]

# pseudo-data:
d = [12, 32, 40, 15, 10]

# convert to numpy arrays
x = np.array(x, dtype='uint8')
R = np.array(R, dtype='uint8')
b = np.array(d, dtype='uint8')

# closure test
b = np.dot(R, x)

n = 8
N = x.shape[0]

print("INFO: N bins:", N)
print("INFO: n-bits encoding:", n)

lmbd = np.uint8(args.lmbd)  # regularization strength
D = laplacian(N)

# convert to bits
x_b = discretize_vector(x, n)
b_b = discretize_vector(b, n)
R_b = discretize_matrix(R, n)
D_b = discretize_matrix(D, n)

print("INFO: Truth-level x:")
print(x, x_b)
print("INFO: pseudo-data b:")
print(b, b_b)
print("INFO: Response matrix:")
print(R)
print(R_b)
print("INFO: Laplacian operator:")
print(D)
print(D_b)
print("INFO: regularization strength:", lmbd)

# Create QUBO operator

# linear constraints
h = {}
for j in range(n*N):
    idx = (j)
    h[idx] = 0
    for i in range(N):
        h[idx] += (R_b[i][j]*R_b[i][j] -
                   2*R_b[i][j] * b[i] +
                   lmbd*D_b[i][j]*D_b[i][j])
    #print("h", idx, ":", h[idx])

# quadratic constraints
J = {}
for j in range(n*N):
    for k in range(j+1, n*N):
        idx = (j, k)
        J[idx] = 0
        for i in range(N):
            J[idx] += 2*(R_b[i][j]*R_b[i][k] + lmbd*D_b[i][j]*D_b[i][k])
        #print("J", idx, ":", J[idx])

# QUBO
bqm = dimod.BinaryQuadraticModel(linear=h,
                                 quadratic=J,
                                 offset=0.0,
                                 vartype=dimod.BINARY)
print("INFO: solving the QUBO model...")

result = None
if args.backend == 'cpu':
    print("INFO: running on CPU...")
    result = dimod.ExactSolver().sample(bqm)
elif args.backend == 'qpu':
    print("INFO: running on QPU...")
    result = sampler_qpu.sample(bqm, num_reads=num_reads).aggregate()
elif args.backend == 'sim':
    print("INFO: running on simulated annealer...")
    result = sampler_sim.sample(bqm, num_reads=num_reads).aggregate()
print("INFO: ...done.")

result = result.first
energy = result.energy
q = np.array(list(result.sample.values()))
y = compact_vector(q, n)
print("INFO: best-fit:   ", q, "::", y, ":: E =", energy)
print("INFO: truth value:", x_b, "::", x)
