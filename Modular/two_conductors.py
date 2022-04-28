
import numpy as np
import matplotlib.pyplot as plt
from biot_savart import computeBMagMtx

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
iSrcMtx = np.array([[ 1.0,  0.9,  0.8,  0.7,  0.6,  0.5],
                    [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5]])

# Compute magnitude of B-field at field points
bMagMtx = computeBMagMtx(rFldMtx, rSrcMtx, lSrcVtr, iSrcMtx)
currScale=2
for freqIdx in range(iSrcMtx.shape[1]):
    # Initialize figure
    fig, ax = plt.subplots(figsize=(6,6))

    # Draw line sources and currents
    for i in range(rSrcMtx.shape[1]):
        ax.plot([rSrcMtx[0, i]]*2, rSrcMtx[2, i] + np.array([-lSrcVtr[i]/2, lSrcVtr[i]/2]), color='black', zorder=1)

    # Draw currents
    ax.quiver(rSrcMtx[0, :], rSrcMtx[2, :], np.array([0.0, 0.0]), iSrcMtx[:, freqIdx], color='red', scale_units='xy', scale=currScale, label='Current', zorder=2)

    # Draw B-field magnitudes at field points
    c = ax.scatter(rFldMtx[0, :], rFldMtx[2, :], c=1e6*bMagMtx[:, freqIdx])
    plt.colorbar(c, label=r'$|\mathbf{B}|$ [µT]')

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')

    ax.set_xlim([-0.2, 0.2])
    ax.set_ylim([-1, 1])

    ax.set_title('Frequency {}'.format(freqIdx + 1))

    ax.legend()
    plt.tight_layout()
    plt.show()
