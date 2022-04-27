import numpy as np
import matplotlib.pyplot as plt
from biot_savart import computeBMagMtx

def getBfaltAmplitude(I):
    I_pos = [B[0] for B in I]
    I_neg = [B[1] for B in I]
    #print("I_pos: ", I_pos)
    #print("I_neg: ", I_neg)
    # Field points
    rFldMtx = np.array([[-0.08, -0.08, -0.08],
                        [0.0, 0.0, 0.0],
                        [0.0, -0.25, -0.5]])

    # Centers of line currents
    rSrcMtx = np.array([[-0.01, 0.01],
                        [0.0, 0.0],
                        [0.0, 0.0]])

    # Lengths of line currents
    lSrcVtr = np.array([1.0, 1.0])

    # Amplitudes of line currents at 5 different frequencies
    iSrcMtx = np.array([I_pos,
                        I_neg])

    # Compute magnitude of B-field at field points
    bMagMtx = computeBMagMtx(rFldMtx, rSrcMtx, lSrcVtr, iSrcMtx)
    #print(bMagMtx)
    return 1e6*np.transpose(bMagMtx)
