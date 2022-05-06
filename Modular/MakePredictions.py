import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import json
import CreateRegressionModel as crm
import ProcessData as d

if __name__ == "__main__":
    lr = pkl.load(open(d.fileName + '_model.pkl', 'rb'))

    prediction = lr.predict([[1.00525105e+04, 1.00000000e+03, 1.00000000e-02, 1.00000000e+02, 1.40000000e-12,
                              2.00000000e-12, 7.00000000e-13, 1.10000000e-12, 2.00000000e-12, 1.59000000e-03,
                              4.48000000e-09, 4.00000000e-07, 1.08297508e+00, 1.94062779e-02, 1.20000000e-11,
                              1.50000000e-11, 1.80000000e-11, 5.50000000e-11, 1.59000000e-03, 8.96000000e-09,
                              8.00000000e-07, 4.96749105e-04, 1.90000000e-03, 2.00000000e-02, 5.02345546e-02,
                              9.66334524e-01, 1.59000000e-03, 3.36000000e-09, 3.00000000e-07, 4.00000000e+02,
                              1.00000000e-03, 1.01422583e-01, 5.08121995e-07, 5.20000000e-11, 4.80000000e-11,
                              2.00000000e-02, 2.05770280e-02, 9.49009121e-01]])
    print(prediction)
    freq = crm.frequencies[1:]
    total_data = pd.DataFrame(prediction.reshape(len(d.Y_variables), len(freq)).transpose(), columns=d.Y_variables)
    print(total_data)
    # plot the score for all frequency bands for every variables

    #for var in d.Y_variables:
    var = "D"
    plt.loglog(freq, total_data[var], label=var)

    plt.xlim([freq[0], freq[-1]])
    plt.legend()

    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.show()
