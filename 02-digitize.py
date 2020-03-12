import os
import random
import joblib
from stdout_redirector import stdout_redirector
import ROOT


distances = [15, 35]
doubleplanes = [8, 12, 30]
energies = [600]
erels = [100, 500]
neutrons = [1, 2, 3, 4, 5]


ROOT.ROOT.EnableThreadSafety()
ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
ROOT.FairLogger.GetLogger().SetLogScreenLevel("WARNING")

filepattern = "output/%dm_%ddp_%dAMeV_%dkeV_%dn.%s.root"


def digitize(distance, energy, doubleplane, neutron, erel, overwrite=False):
    simfile = filepattern % (distance, doubleplane, energy, erel, neutron, "simu")
    parfile = filepattern % (distance, doubleplane, energy, erel, neutron, "para")
    outfile = filepattern % (distance, doubleplane, energy, erel, neutron, "digi")

    if not overwrite and os.path.isfile(outfile):
        print("Exists: " + outfile)
        return None

    # Write all output to a log file
    logfile = outfile.replace(".root", ".log")
    with stdout_redirector(logfile):
        run = ROOT.FairRunAna()
        run.SetSource(ROOT.FairFileSource(simfile))
        run.SetSink(ROOT.FairRootFileSink(outfile))

        # Connect Runtime Database
        rtdb = run.GetRuntimeDb()
        pario = ROOT.FairParRootFileIo(False)
        pario.open(parfile)
        rtdb.setFirstInput(pario)
        rtdb.setOutput(pario)
        rtdb.saveOutput()

        # Digitize data to hit level and create respective histograms
        run.AddTask(ROOT.R3BNeulandDigitizer())

        # Build clusters and create respective histograms
        run.AddTask(ROOT.R3BNeulandClusterFinder())

        # Find the actual primary interaction points and their clusters
        run.AddTask(ROOT.R3BNeulandPrimaryInteractionFinder())
        run.AddTask(ROOT.R3BNeulandPrimaryClusterFinder())

        # Create spectra
        run.AddTask(ROOT.R3BNeulandMCMon())
        run.AddTask(ROOT.R3BNeulandHitMon())
        run.AddTask(ROOT.R3BNeulandClusterMon())

        run.Init()
        run.Run(0, 0)

    return None


# Single digitization
# digitize(distance=15, energy=600, doubleplane=8, neutron=1, erel=100, overwrite=True)


# Parallel simulations
joblib.Parallel(n_jobs=-1, backend="multiprocessing", verbose=11)(
    joblib.delayed(digitize)(
        distance=distance,
        energy=energy,
        doubleplane=doubleplane,
        neutron=neutron,
        erel=erel,
        overwrite=False)
    for distance in distances
    for energy in energies
    for doubleplane in doubleplanes
    for neutron in neutrons
    for erel in erels
)
