#!/usr/bin/env python3

import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', **{'family': 'serif', 'serif': ['Palatino']})
rc('text', usetex=True)
rc('legend', **{'fontsize': 13})
from quantum_unfolding import input_data


known_methods = [
    'IB4',
    'sim',
    'qpu_lonoise_reg0',
    'qpu_lonoise_reg01',
    'qpu_lonoise_reg025',
    #'qpu_lonoise_reg05',
    'qpu_lonoise_reg1',
    #'qpu_hinoise_reg0',
    #'qpu_hinoise_reg1',
]
n_methods = len(known_methods)

labels = {
    'truth': "True value",
    'IB4': "D\'Agostini ItrBayes ($N_{itr}$=4)",
    'sim': "QUBO (CPU, Neal)",
    'qpu_lonoise_reg0': "QUBO (QPU, $\lambda=0$)",
    'qpu_lonoise_reg1': "QUBO (QPU, $\lambda=1$)",
    'qpu_lonoise_reg01': "QUBO (QPU, $\lambda=0.1$)",
    'qpu_lonoise_reg025': "QUBO (QPU, $\lambda=0.25$)",
    # 'qpu_lonoise_reg05' : "QUBO (QPU, $\lambda=0.5$)",
    'qpu_hinoise_reg0': "QUBO (QPU, $\lambda=0$)",
    'qpu_hinoise_reg1': "QUBO (QPU, $\lambda=1$)",
    'hyb_reg0': "QUBO (Hybrid, $\lambda$=0)",
    'hyb_reg1': "QUBO (Hybrid, $\lambda$=1)",
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def FromFile(csv_file):
    data = np.genfromtxt(csv_file, delimiter=',')

    return {'mean': np.mean(data, axis=0), 'rms': np.std(data, axis=0)}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

parser = argparse.ArgumentParser("Quantum unfolding plotter")
parser.add_argument('-o', '--observable', default='peak')
parser.add_argument('-e', '--encoding', default=4)
args = parser.parse_args()

nbits = int(args.encoding)
obs = args.observable

z = input_data[obs]['truth']
nbins = z.shape[0]

unfolded_data = {
    'truth': {
        'mean': z,
        'rms': np.zeros(nbins),
    },
    'IB4':
    input_data[obs]['IB4'],
    'sim':
    FromFile(f"data/results.obs_{obs}.sim.reg_0.{nbits}bits.csv"),
    'qpu_lonoise_reg0':
    FromFile(f"data/results.obs_{obs}.qpu_lonoise.reg_0.{nbits}bits.csv"),
    'qpu_lonoise_reg1':
    FromFile(f"data/results.obs_{obs}.qpu_lonoise.reg_1.{nbits}bits.csv"),
    'qpu_hinoise_reg0':
    FromFile(f"data/results.obs_{obs}.qpu_hinoise.reg_0.{nbits}bits.csv"),
    'qpu_hinoise_reg1':
    FromFile(f"data/results.obs_{obs}.qpu_hinoise.reg_1.{nbits}bits.csv"),
    'qpu_lonoise_reg01':
    FromFile(f"data/results.obs_{obs}.qpu_lonoise.reg_0.1.{nbits}bits.csv"),
    'qpu_lonoise_reg025':
    FromFile(f"data/results.obs_{obs}.qpu_lonoise.reg_0.25.{nbits}bits.csv"),
    'qpu_lonoise_reg05':
    FromFile(f"data/results.obs_{obs}.qpu_lonoise.reg_0.5.{nbits}bits.csv"),
    #'hyb_reg0'         : FromFile(f"csv/results.obs_{obs}.hyb.reg_0.csv"),
    #'hyb_reg1'         : FromFile(f"csv/results.obs_{obs}.hyb.reg_1.csv"),
}

colors = [
    'black', 'red', 'gold', 'seagreen', 'blue', 'violet', 'cyan', 'navyblue'
]
#          'gold', 'cyan', 'violet', 'navyblue']
# colors = ['black', 'salmon', 'royalblue', 'lightgreen', 'gold']
markers = ['o', 'v', '^', 'D', 'o', 'D', 'o', 'D']
bar_width = 0.1

fig, ax = plt.subplots(tight_layout=True, figsize=(10, 6))

ibin = np.arange(1, nbins + 1)  # position along the x-axis

print("Truth")
print(unfolded_data['truth']['mean'])

# First, plot truth-level distribution
plt.step([0] + list(ibin), [unfolded_data['truth']['mean'][0]] +
         list(unfolded_data['truth']['mean']),
         label=labels['truth'],
         color='black',
         linestyle='dashed')

#plt.step(ibin, unfolded_data['pdata']['mean'], where='mid',
#         label=labels['pdata'], color='black', linestyle='dashed')

for i in range(1, n_methods + 1):
    method = known_methods[i - 1]

    print(method)
    print(unfolded_data[method]['mean'])
    print(unfolded_data[method]['rms'])

    plt.errorbar(x=ibin + 0.1 * i - 0.8,
                 y=unfolded_data[method]['mean'],
                 yerr=unfolded_data[method]['rms'],
                 color=colors[i],
                 fmt=markers[i],
                 ms=10,
                 label=labels[method])

plt.xlim(-0.2, 5.2)
plt.legend()
plt.ylabel("Unfolded")
plt.xlabel("Bin")
ax.xaxis.label.set_fontsize(14)
ax.yaxis.label.set_fontsize(14)
plt.xticks(np.arange(5) + 0.5, [1, 2, 3, 4, 5], fontsize=14)
plt.yticks(fontsize=14)
plt.show()
fig.savefig(f"unfolded_{obs}.pdf")
