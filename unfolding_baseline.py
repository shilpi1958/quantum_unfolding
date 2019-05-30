#!/usr/bin/env python

import os
import sys
import argparse

from ROOT import *
import numpy as np

from decimal2binary import *
from input_data import *

np.set_printoptions(precision=1, linewidth=200, suppress=True)

###########################


def array_to_th1(a, hname="h", htitle=";X;Entries"):
    n_bins = a.shape[0]

    h = TH1F(hname, htitle, n_bins, 0.5, n_bins+0.5)

    for i in range(n_bins):
        h.SetBinContent(i+1, a[i])

    return h

#~~~~~~~~~~~~~~~~~~~~~~~~~~


def th1_to_array(h):
    n = h.GetNbinsX()
    a = [h.GetBinContent(i+1) for i in range(n)]
    a = np.array(a, dtype='uint8')
    return a

#~~~~~~~~~~~~~~~~~~~~~~~~~~


def array_to_th2(a, hname="res", htitle=";reco;truth"):
    n_bins_x = a.shape[0]
    n_bins_y = a.shape[1]

    h = TH2F(hname, htitle, n_bins_x,
             0.5, n_bins_x+0.5, n_bins_y, 0.5, n_bins_y+0.5)

    for i in range(n_bins_x):
        for j in range(n_bins_y):
            h.SetBinContent(i+1, j+1, a[i][j])

    return h

###########################


parser = argparse.ArgumentParser("Quantum unfolding")
parser.add_argument('-l', '--lmbd', default=0.00)
parser.add_argument('-n', '--nreads', default=1000)
args = parser.parse_args()

num_reads = int(args.nreads)

#d = np.array(d, dtype='uint8')

print("INFO: Signal truth-level x:")
print(x)
print("INFO: Pseudo-data truth-level z:")
print(z)
print("INFO: Response matrix:")
print(R)
print("INFO: Signal y:")
print(y)
print("INFO: Pseudo-data d:")
print(d)

h_x = array_to_th1(x, "truth")
h_R = array_to_th2(R, "response")
h_y = array_to_th1(y, "signal")
h_d = array_to_th1(d, "data")
# h_R.Draw("text")
loaded_RooUnfold = gSystem.Load("libRooUnfold.so")
if not loaded_RooUnfold == 0:
    print "INFO: RooUnfold not found."
else:
    print "INFO: RooUnfold found. Output file will contain unfolded distributions with (unregularized) Matrix Inversion and (regularized) Iterative Bayesian with Nitr=4"

# see: http://hepunx.rl.ac.uk/~adye/software/unfold/RooUnfold.html

m_response = RooUnfoldResponse(h_y, h_x, h_R)
m_response.UseOverflow(False)

unfolder_mi = RooUnfoldInvert("MI", "Matrix Inversion")
unfolder_mi.SetVerbose(0)
unfolder_mi.SetResponse(m_response)
unfolder_mi.SetMeasured(h_d)
h_unf_mi = unfolder_mi.Hreco()
h_unf_mi.SetName("unf_mi")
u_mi = th1_to_array(h_unf_mi)
print("INFO: unfolded (MI):")
print(u_mi)


unfolder_ib = RooUnfoldBayes("IB", "Iterative Baysian")
unfolder_ib.SetIterations(4)
unfolder_ib.SetVerbose(1)
unfolder_ib.SetSmoothing(0)
unfolder_ib.SetResponse(m_response)
unfolder_ib.SetMeasured(h_d)
h_unf_ib = unfolder_ib.Hreco()
h_unf_ib.SetName("unf_ib")

u_ib = th1_to_array(h_unf_ib)
print("INFO: unfolded (IB):")
print(u_ib)

unfolder_svd = RooUnfoldSvd("SVD", "SVD Tikhonov")
unfolder_svd.SetKterm(3)  # usually nbins//2
unfolder_svd.SetVerbose(1)
unfolder_svd.SetResponse(m_response)
unfolder_svd.SetMeasured(h_d)
h_unf_svd = unfolder_svd.Hreco()
h_unf_svd.SetName("unf_svd")

u_svd = th1_to_array(h_unf_svd)
print("INFO: unfolded (SVD):")
print(u_svd)

print("INFO: Truth-level z:")
print(z)