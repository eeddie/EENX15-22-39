# from biot_savart import getI2bMtx
import numpy as np


def getI2bMtx(rFldMtx, rSrcMtx, lSrcVtr):
    """
    Parameters:
        rFldMtx: field points
        rSrcMtx: midpoints of straight line current sources
        lSrcVtr: lengths of straight line current sources
    Returns:
        i2bMtx: magnetic flux density contribution at field points
                for each straight line current source
    """
    m0 = 4e-7 * np.pi

    i2bMtx = np.zeros((3 * rFldMtx.shape[1], rSrcMtx.shape[1]))
    for idxFld in range(rFldMtx.shape[1]):

        rFldTmp = rFldMtx[:, idxFld]
        for idxSrc in range(rSrcMtx.shape[1]):
            rSrcTmp = rSrcMtx[:, idxSrc]
            lSrcTmp = lSrcVtr[idxSrc]
            iSrcTmp = 1  # Unit excitation

            drTmp = rFldTmp - rSrcTmp
            zt = drTmp[2]
            rt = np.sqrt(drTmp[0] ** 2 + drTmp[1] ** 2)
            cospt = drTmp[0] / rt
            sinpt = drTmp[1] / rt
            pht = np.array([-sinpt, cospt, 0])

            i2bTmp = pht * ((m0 * iSrcTmp) / (4 * np.pi * rt)) * (
                    (zt + lSrcTmp / 2) / np.sqrt(rt ** 2 + (zt + lSrcTmp / 2) ** 2) \
                    - (zt - lSrcTmp / 2) / np.sqrt(rt ** 2 + (zt - lSrcTmp / 2) ** 2)
            )

            i2bMtx[3 * idxFld + np.arange(3), idxSrc] = \
                i2bMtx[3 * idxFld + np.arange(3), idxSrc] + i2bTmp

    return i2bMtx


def computeBMagMtx(rFldMtx, rSrcMtx, lSrcVtr, iSrcMtx):
    """
    Parameters:
        rFldMtx: field points
                (matrix, each column a coordinate [x, y, z])
        rSrcMtx: midpoints of straight line current sources
                (matrix, each column a coordinate [x, y, z])
        lSrcVtr: lengths of straight line current sources (vector)
        iSrcMtx: amplitudes of straight line current sources
                (matrix, each row an array of amplitudes for different frequencies)
    Returns:
        bMagMtx: magnitude of magnetic flux density at field points
                (matrix, each row an array of amplitudes for different frequencies)
    """
    # Compute magnetic flux density at all field points by superposition
    i2bMtx = getI2bMtx(rFldMtx, rSrcMtx, lSrcVtr)
    bFldMtx = i2bMtx @ iSrcMtx

    bMagMtx = np.zeros((rFldMtx.shape[1], iSrcMtx.shape[1]))
    for idxFld in range(rFldMtx.shape[1]):
        bMagMtx[idxFld] = np.sqrt(np.sum(np.square(np.abs(bFldMtx[3 * idxFld + np.arange(3), :])), axis=0))

    return bMagMtx


if __name__ == '__main__':
    mdict = np.load('testcase.npz')
    bMagMtx = computeBMagMtx(mdict['rFldMtx'], mdict['rSrcMtx'], mdict['lSrcVtr'], mdict['iSrcMtx'])
    assert np.all(np.isclose(bMagMtx, mdict['bMagMtx']))
    print('Test OK')
