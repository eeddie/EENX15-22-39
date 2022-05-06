import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import json

fileName = "results_v4"

total_y_vars = ["bandStart", "bandEnd", "numOfPoints", "i(VDC_P)", "i(VDC_N)", "i(VAC_A)", "i(VAC_B)", "i(VAC_C)",
                "i(l.xinvgnd.l1)", "i(l.xbatgnd.l1)", "i(l.xloadgnd.l1)", "v(batCase)", "v(invCase)", "v(loadCase)",
                "v(CMCpos)-v(CMCneg)", "i(VAC_A)+i(VAC_B)+i(VAC_C)", "A", "B", "C", "D", "E"]
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
               "v(CMCpos)-v(CMCneg)", "i(VAC_A)+i(VAC_B)+i(VAC_C)", "A", "B", "C", "D", "E"]
# get the y-variables
cols = [total_y_vars.index(var) for var in Y_variables]
if __name__ == "__main__":
    # load the results.npy file
    results = np.load(fileName+".npy", allow_pickle=True)

    data = pd.json_normalize(results, max_level=0)
    # remove all entries where the simulation failed
#    data.drop(data[data['results'].apply(lambda x: "log" in x)].index, inplace=True)

    # get the x-variables
    d_X = pd.json_normalize(data['modules'])[X_variables]

    # make the y-data easier to work with
    df = pd.DataFrame(data['results'].tolist())

    # divide every value by the number of points
    d_Y = df.applymap(lambda x: [x[n] / x[2] for n in cols])

    # drop all values where any of the x-variables is nan
    d_XY = pd.concat([d_X, d_Y], axis=1).dropna()

    # save the dataFrame
    d_XY.to_pickle(fileName + '.pkl')
