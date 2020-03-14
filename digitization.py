import os
import sys
from helpers import stdout_redirector
import ROOT


def digitization(distance, doubleplane, energy, erel, neutron, overwrite=False):
    namepattern = "%dm_%ddp_%dAMeV_%dkeV_%dn"
    name = namepattern % (distance, doubleplane, energy, erel, neutron)

    filepattern = "output/%s.%s.%s"
    inpfile = filepattern % (name, "simu", "root")
    parfile = filepattern % (name, "para", "root")
    outfile = filepattern % (name, "digi", "root")
    logfile = filepattern % (name, "digi", "log")

    if not os.path.isfile(inpfile):
        print(f"Input {inpfile} does not exist")
        return

    if not overwrite and os.path.isfile(outfile):
        print(f"Output {outfile} exists and overwriting is disabled")
        return

    ROOT.ROOT.EnableThreadSafety()
    ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
    ROOT.FairLogger.GetLogger().SetLogScreenLevel("WARNING")

    # Write all output to a log file
    with stdout_redirector(logfile):
        run = ROOT.FairRunAna()
        run.SetSource(ROOT.FairFileSource(inpfile))
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


if __name__ == "__main__":
    distance = int(sys.argv[1])
    doubleplane = int(sys.argv[2])
    energy = int(sys.argv[3])
    erel = int(sys.argv[4])
    neutron = int(sys.argv[5])
    digitization(distance, doubleplane, energy, erel, neutron, overwrite=True)
