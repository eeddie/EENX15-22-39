from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import json

if __name__ == "__main__":
    # Load data
    with open("all_sim_results_fixed.json", "r") as f:
        data = pd.DataFrame(json.load(f))

    # remove all entries where the simulation failed
    data.drop(data[data['results'].apply(lambda x: "log" in x)].index, inplace=True)

    # choose the x-variables.
    X_variables = ['ACCommonModeChokeModule.Coupling', 'ACCommonModeChokeModule.L_choke',
                   'ACCommonModeChokeModule.R_ser']
    # choose the y-variables.
    Y_variable = ["i(VAC_A)+i(VAC_B)+i(VAC_C)"]

    variables = ["bandStart", "bandEnd", "numOfPoints", "i(VDC_P)", "i(VDC_N)", "i(VAC_A)", "i(VAC_B)", "i(VAC_C)",
                 "i(l.xinvgnd.l1)", "i(l.xbatgnd.l1)", "i(l.xloadgnd.l1)", "v(batCase)", "v(invCase)", "v(loadCase)",
                 "v(CMCpos)-v(CMCneg)", "i(VAC_A)+i(VAC_B)+i(VAC_C)"
                 ]

    # get the x-variables
    d_X = pd.json_normalize(data['modules'])[X_variables]

    # make the y-data easier to work with
    df = pd.DataFrame(pd.json_normalize(data['results'])['energies'].tolist())

    # get the y-variables
    cols = [variables.index(var) for var in Y_variable]
    d_Y = df.applymap(lambda x: [x[i] for i in cols])

    # drop all values where any of the x-variables is nan
    d_XY = pd.concat([d_X, d_Y], axis=1).dropna()

    # get the x-variables that are not nan
    X = d_XY[X_variables]

    # get the y-variables that correspond to the x-variables not being nan
    Y = d_XY.drop(columns=X_variables)
    Y = pd.concat([Y.applymap(lambda x: x[i]).rename(columns={j: str(j) + '.' + str(i) for j in Y.columns})
                   for i in range(len(cols))], axis=1)

    # split the data into training and test data
    x_train, x_test, y_train, y_test = train_test_split(X.values, Y, test_size=0.2, random_state=2)
    # print(Y['56.4'])

    print(len(x_train), len(x_test), len(y_train), len(y_test))

    # create the model and train it
    lr = LinearRegression()
    lr.fit(x_train, y_train)

    # This shows all the n-dimensional planes that are created by the regression
    for i, j in zip(lr.coef_, lr.intercept_):
        print(i, j)

    y_pred = lr.predict(x_test)
    print("Score on the testing data: " + r2_score(y_test, y_pred))
    print("Score on the training data: " + r2_score(y_train, lr.predict(x_train)))
