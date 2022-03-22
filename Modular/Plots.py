from ParseRaw import *
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # Jämför simuleringsresultat mellan en krets utan common-mode-choke och en med
    # compareFourier(["tmp_cmc_all2.raw", "tmp_cmc_all.raw"], labels=["all2", "all"])

    # Jämför common mode strömmen mellan två kretsar (från försimulerad data)
    # compareCMCCurrent("tmp_bin.raw", "tmp_cmc.raw", "No CMC", "Lcmc = 51 mH")
    
    # Jämför FFT mellan icke-subsamplad fasström och subsamplad fasström, också lite andra plots
    # compareUniformResample("tmp_bin.raw")

    # Visualiserar hur interpoleringen av datan fungerar
    # visInterpolation()

    # Plotta ett antal variabler i samma graf med olika färger
    # plt.figure(0)
    # plotVars("tmp_cmc.raw", ["i(@c.xbatgnd.c1[i])", "i(@c.xinvgnd.c1[i])", "i(@c.xloadgnd.c1[i])"], ["Battery", "Inverter", "Load"], title="Current through parasitic capacitances")
    # plt.figure(1)
    # plotVars("tmp_cmc.raw", ["v(pha)", "v(phb)", "v(phc)"], ["A", "B", "C"], title="Phase Voltages")
    # plt.figure(2)
    # plotVars("tmp_cmc.raw", ["i(l.xload.l1)", "i(l.xload.l2)", "i(l.xload.l3)"], ["A", "B", "C"], title="Phase Currents")

    # plt.figure(3)
    # compareFourier(["tmp_cmc.raw"], labels=[""], variableName="i(l.xload.l1)", title="Phase current")

    # plt.figure(4)
    # compareFourier(["tmp_none_phcurr_gear.raw", "tmp_none_phcurr_trap.raw"], labels=["gear", "trap"], variableName="i(l.xload.l1)", title="Phase current")

    # plt.figure(3)
    # plotVars("igbt.raw", ["i(l.xload.l1)"], ["A"], title="Phase Current")
    # plt.figure(4)
    # compareFourier(["igbt.raw"], labels=["A"], variableName="i(l.xload.l1)", title="Phase current")

    # plt.figure(4)
    # plotFourier("tmp_cmc.raw", ["i(@c.xbatgnd.c1[i])", "i(@c.xinvgnd.c1[i])", "i(@c.xloadgnd.c1[i])"], ["Battery", "Inverter", "Load"], title="Current through parasitic capacitances")

    # plt.figure(0)
    # compareFourier(["tmp_cmc.raw", "tmp_xcap.raw"], labels=["CMC", "CMC + XCap"], variableName="i(@c.xbatgnd.c1[i])", title="Parasitic capacitance current on battery")


    plt.figure(3)
    plotVars("igbt.raw", ["v(batpos)", "v(batneg)"], [""], title="Battery voltage")

    plt.show()
    