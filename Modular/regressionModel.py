import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import json


def saveToDataFrame(model, X_variables, Y_variables, fileName):
    saveDataFrame = pd.DataFrame()
    saveDataFrame[str(X_variables)] = np.zeros(6925)
    nrOfBands = 6925
    s = []
    for k in range(len(Y_variables)):
        print(k)
        coef = lr.coef_[k * nrOfBands:(k + 1) * nrOfBands]
        intercept = lr.intercept_[k * nrOfBands:(k + 1) * nrOfBands]
        s = np.append(coef, [[i] for i in intercept], axis=1)
        print(s)
        saveDataFrame[Y_variables[k]] = s.tolist()

    saveDataFrame.to_pickle(fileName + '.pkl')

    pkl.dump(model, open(fileName + '.sav', 'wb'))


if __name__ == "__main__":
    # Load data
    with open("all_sim_results_fixed.json", "r") as f:
        data = pd.DataFrame(json.load(f))

    # remove all entries where the simulation failed
    data.drop(data[data['results'].apply(lambda x: "log" in x)].index, inplace=True)

    limits = [0, 10000, 150000, 30000000, 400000000]
    bandwidths = [100 * 10 ** p for p in range(5)]
    frequencies = []
    for i in range(len(limits) - 1):
        for j in range(limits[i], limits[i + 1], bandwidths[i]):
            frequencies.append(j)
    frequencies.append(limits[-1])

    total_y_vars = ["bandStart", "bandEnd", "numOfPoints", "i(VDC_P)", "i(VDC_N)", "i(VAC_A)", "i(VAC_B)", "i(VAC_C)",
                    "i(l.xinvgnd.l1)", "i(l.xbatgnd.l1)", "i(l.xloadgnd.l1)", "v(batCase)", "v(invCase)", "v(loadCase)",
                    "v(CMCpos)-v(CMCneg)", "i(VAC_A)+i(VAC_B)+i(VAC_C)", "BS1", "BS2", "BS3", "BS4", "BS5"]
    total_x_vars = ['InverterControlModule.Fs', 'InverterControlModule.Gain',
                    'InverterControlModule.OverlapProtection', 'TransistorModule.v_t',
                    'TransistorModule.r_on', 'TransistorModule.r_off', 'InverterModule.Mod',
                    'InverterModule.Freq', 'InverterModule.InvConModName',
                    'InverterModule.TranModName', 'InverterModule.ParCapA',
                    'InverterModule.ParCapB', 'InverterModule.ParCapC',
                    'InverterModule.ParCapP', 'InverterModule.ParCapN',
                    'InverterGroundModule.R', 'InverterGroundModule.C',
                    'InverterGroundModule.L', 'LoadModule.R_load', 'LoadModule.L_load',
                    'LoadModule.ParCapA', 'LoadModule.ParCapB', 'LoadModule.ParCapC',
                    'LoadModule.ParCapN', 'LoadGroundModule.R', 'LoadGroundModule.C',
                    'LoadGroundModule.L', 'XCapModule.C_self', 'XCapModule.R_self',
                    'ACCommonModeChokeModule.R_ser', 'ACCommonModeChokeModule.L_choke',
                    'ACCommonModeChokeModule.Coupling', 'BatteryGroundModule.R',
                    'BatteryGroundModule.C', 'BatteryGroundModule.L',
                    'BatteryModule.Voltage', 'BatteryModule.RampTime',
                    'BatteryModule.R_self', 'BatteryModule.L_self', 'BatteryModule.ParCapP',
                    'BatteryModule.ParCapN', 'DCCommonModeChokeModule.R_ser',
                    'DCCommonModeChokeModule.L_choke', 'DCCommonModeChokeModule.Coupling']

    # choose the x-variables.
    X_variables = ['InverterControlModule.Fs', 'InverterControlModule.Gain',
                   'InverterControlModule.OverlapProtection', 'InverterModule.Freq', 'InverterModule.ParCapA',
                   'InverterModule.ParCapB', 'InverterModule.ParCapC',
                   'InverterModule.ParCapP', 'InverterModule.ParCapN',
                   'InverterGroundModule.R', 'InverterGroundModule.C',
                   'InverterGroundModule.L', 'LoadModule.R_load', 'LoadModule.L_load',
                   'LoadModule.ParCapA', 'LoadModule.ParCapB', 'LoadModule.ParCapC',
                   'LoadModule.ParCapN', 'LoadGroundModule.R', 'LoadGroundModule.C',
                   'LoadGroundModule.L', 'XCapModule.C_self', 'XCapModule.R_self',
                   'ACCommonModeChokeModule.R_ser', 'ACCommonModeChokeModule.L_choke',
                   'ACCommonModeChokeModule.Coupling', 'BatteryGroundModule.R',
                   'BatteryGroundModule.C', 'BatteryGroundModule.L',
                   'BatteryModule.Voltage', 'BatteryModule.RampTime',
                   'BatteryModule.R_self', 'BatteryModule.L_self', 'BatteryModule.ParCapP',
                   'BatteryModule.ParCapN', 'DCCommonModeChokeModule.R_ser',
                   'DCCommonModeChokeModule.L_choke', 'DCCommonModeChokeModule.Coupling']
    # choose the y-variables.
    Y_variables = ["i(VDC_P)", "i(VDC_N)", "i(VAC_A)", "i(VAC_B)", "i(VAC_C)",
                   "i(l.xinvgnd.l1)", "i(l.xbatgnd.l1)", "i(l.xloadgnd.l1)", "v(batCase)", "v(invCase)", "v(loadCase)",
                   "v(CMCpos)-v(CMCneg)", "i(VAC_A)+i(VAC_B)+i(VAC_C)", "BS1", "BS2", "BS3", "BS4", "BS5"]

    # get the x-variables
    d_X = pd.json_normalize(data['modules'])[X_variables]

    # make the y-data easier to work with
    df = pd.DataFrame(pd.json_normalize(data['results'])['energies'].tolist())

    # get the y-variables
    cols = [total_y_vars.index(var) for var in Y_variables]
    # divide every value by the number of points
    d_Y = df.applymap(lambda x: [x[n] / x[2] for n in cols])

    # drop all values where any of the x-variables is nan
    d_XY = pd.concat([d_X, d_Y], axis=1).dropna()
    # drop all values where battery voltage is not 400V
    d_XY.drop(d_XY[(d_XY['BatteryModule.Voltage'] != 400)].index, inplace=True)

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
    # print(Y['56.4'])

    # print the number of samples in the training and test data
    print(len(x_train), len(x_test), len(y_train), len(y_test))

    # create the model and train it
    lr = LinearRegression()
    lr.fit(x_train, y_train)

    # This shows all the n-dimensional planes that are created by the regression
    # for i, j in zip(lr.coef_, lr.intercept_):
    #   print(i, j)
    
    # save lr_coef and lr_intercept in a dataFrame to a .pkl file and save the model to a .sav file
    # saveToDataFrame(lr, X_variables,Y_variables, "linearRegressionModel")

    # enlarge plt font size
    plt.rcParams.update({'font.size': 16})

    # predict the test data and get the score
    y_pred = lr.predict(x_test)
    score = r2_score(y_test, y_pred, multioutput='raw_values')
    
    # plot the score for all frequency bands for every variables
    size = len(frequencies[1:])
    for m in range(int(len(score) / size)):
        plt.plot(frequencies[1:], score[m * size:(m + 1) * size], label=Y_variables[m])

    # change the x-axis to logarithmic and set x-limits,
    # value for frequency band [0,100] will be shown at x=100 and so on
    plt.xscale('log')
    plt.axis([100, frequencies[-1], -1, 1])
    plt.legend()

    plt.xlabel('Frequency [Hz]')
    plt.ylabel('R2-score')

    plt.show()
