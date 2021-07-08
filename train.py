import os
import sys
import subprocess
import ROOT
from helpers import filename_for


def train_impl(distance, doubleplane, energy, nmax, physics, overwrite):
    outfile = f"output/{physics}/{distance}m_{doubleplane}dp_{energy}AMeV_{nmax}n.train.root"
    parfile = f"output/{physics}/{distance}m_{doubleplane}dp_{energy}AMeV_{nmax}n.ncut.root"

    if os.path.isfile(outfile):
        if overwrite:
            os.remove(outfile)
        else:
            print(f"Output {outfile} exists and overwriting is disabled")
            return

    if os.path.isfile(parfile):
        if overwrite:
            os.remove(parfile)
        else:
            print(f"Output {parfile} exists and overwriting is disabled")
            return

    # TODO: Might be better to train on one erel with 10x statistics
    erels = [100, 500, 1000]

    files = [
        filename_for(distance, doubleplane, energy, erel, neutron, physics, ".digi.root")
        for erel in erels
        for neutron in range(1, nmax + 1)
    ]
    files = [file for file in files if os.path.isfile(file)]

    ROOT.ROOT.EnableThreadSafety()
    ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
    ROOT.FairLogger.GetLogger().SetLogScreenLevel("INFO")

    run = ROOT.FairRunAna()
    ffs = ROOT.FairFileSource(files[0])
    for file in files[1:]:
        ffs.AddFile(file)
    run.SetSource(ffs)
    run.SetSink(ROOT.FairRootFileSink(outfile))

    # Connect Runtime Database
    rtdb = run.GetRuntimeDb()
    paro = ROOT.FairParRootFileIo(True)
    paro.open(os.fspath(parfile))
    rtdb.setOutput(paro)

    # Train tasks
    trn = ROOT.R3BNeulandMultiplicityCalorimetricTrain("NeulandClusters", "NeulandPrimaryTracks")
    trn.SetEdepOpt(energy, 25, energy * 0.25, energy * 1.75)
    # trn.SetWeight(0.5)
    run.AddTask(trn)

    run.AddTask(ROOT.R3BNeulandMultiplicityBayesTrain("NeulandClusters", "NeulandPrimaryTracks"))

    run.Init()
    run.Run(0, 0)
    rtdb.writeContainers()
    rtdb.writeVersions()
    rtdb.saveOutput()
    rtdb.print()
    rtdb.closeOutput()


# Ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior.
# As a result, the same process can't be reused after the first run.
# Here, create a fully standalone process that is fully destroyed afterwards.
# TODO: Once/If this is fixed, remove this and rename the impl function
def train(distance, doubleplane, energy, nmax, physics):
    logfile = f"output/{physics}/{distance}m_{doubleplane}dp_{energy}AMeV_{nmax}n.train.log"
    d = [
        "python",
        "train.py",
        str(distance),
        str(doubleplane),
        str(energy),
        str(nmax),
        str(physics),
    ]
    with open(logfile, "w") as log:
        subprocess.run(d, stdout=log, stderr=log)


if __name__ == "__main__":
    distance = int(sys.argv[1])
    doubleplane = int(sys.argv[2])
    energy = int(sys.argv[3])
    nmax = int(sys.argv[4])
    physics = sys.argv[5]
    train_impl(distance, doubleplane, energy, nmax, physics, overwrite=True)
