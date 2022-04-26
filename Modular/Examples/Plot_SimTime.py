#
# Plot_SimTime.py
#
# Plottar simuleringstider för olika switchmodeller både i enkel krets och i drivlina
#


import matplotlib.pyplot as plt

if __name__ == "__main__":

    plt.figure(1)
    labels = ["Strömbrytare", "Varistor", "Inb. MOSFET", "Sub. MOSFET", "IGBT"]
    times = [31, 41, 37, 66, 620]
    
    # Make a bar plot
    plt.bar(labels, times)
    plt.ylabel('Tid (s)')
    plt.title('Tid för att simulera i enkel krets')
    

    # Add the values centered on top of the bars formated as seconds
    for i, v in enumerate(times):
        plt.text(i, v, str(v) + " s", color='black', ha='center', va='bottom')


    plt.figure(2)
    labels = ["Strömbrytare", "Inb. MOSFET", "Sub. MOSFET"]
    times = [2265/60, 2304/60, 9488/60]

    # Make a bar plot
    plt.bar(labels, times)
    plt.ylabel('Tid (min)')
    plt.title('Tid för att simulera i drivlina')

    # Add the values centered on top of the bars formated as minutes
    for i, v in enumerate(times):
        plt.text(i, v, str(round(v)) + " min", color='black', ha='center', va='bottom')



    plt.show()
