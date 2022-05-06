import ProcessData as d
import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

limits = [0, 10000, 150000, 30000000, 400000000]
bandwidths = [100 * 10 ** p for p in range(5)]
frequencies = []
for i in range(len(limits) - 1):
    for j in range(limits[i], limits[i + 1], bandwidths[i]):
        frequencies.append(j)
frequencies.append(limits[-1])

if __name__ == "__main__":

    # choose the x-variables.
    X_variables = d.X_variables
    # choose the y-variables.
    Y_variables = d.Y_variables
    cols = d.cols

    # load the data.
    d_XY = pd.read_pickle(d.fileName + '.pkl')

    # get the x-variables (that are not nan and battery voltage is 400V)
    X = d_XY[X_variables]

    # get the y-variables that correspond to the new x-variables
    Y = d_XY.drop(columns=X_variables)
    # rename the columns such that ex. getting "12.2" means getting the 12th frequency band for the variable
    # Y_variables[2].
    Y = pd.concat([Y.applymap(lambda x: x[varnr])
                  .rename(columns={bandnr: str(bandnr) + '.' + str(varnr) for bandnr in Y.columns})
                   for varnr in range(len(cols))], axis=1)

    # split the data into training and test data
    x_train, x_test, y_train, y_test = train_test_split(X.values, Y, test_size=0.2, random_state=2)

    # print the number of samples in the training and test data
    print(len(x_train), len(x_test), len(y_train), len(y_test))

    # create the model and train it
    lr = LinearRegression()
    lr.fit(x_train, y_train)

    # save the model
    pkl.dump(lr, open(d.fileName + '_model.pkl', 'wb'))

    lr = pkl.load(open(d.fileName + '_model.pkl', 'rb'))

    # enlarge plt font size
    plt.rcParams.update({'font.size': 12})

    # predict the test data and get the score
    y_pred = lr.predict(x_test)
    score = r2_score(y_test, y_pred, multioutput='raw_values')

    freq = frequencies[1:]
    total_data = pd.DataFrame(score.reshape(len(Y_variables), len(freq)).transpose(), columns=Y_variables)
    # plot the score for all frequency bands for every variables
    for var in Y_variables:
        plt.plot(freq, total_data[var], label=var)

    # change the x-axis to logarithmic and set x-limits,
    # value for frequency band [0,100] will be shown at x=100 and so on
    plt.xscale('log')
    plt.axis([freq[0], freq[-1], -1, 1])
    plt.legend()

    plt.xlabel('Frequency [Hz]')
    plt.ylabel('R2-score')

    plt.show()
