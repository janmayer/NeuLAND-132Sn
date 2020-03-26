import os
import sys
import wurlitzer
import subprocess
import ROOT


def digitization_impl(distance, doubleplane, energy, erel, neutron, physics, scenario, overwrite):
    basepath = "output/%s-%s/" % (physics.lower(), scenario)
    basename = "%dm_%ddp_%dAMeV_%dkeV_%dn" % (distance, doubleplane, energy, erel, neutron)
    inpfile = basepath + basename + ".simu.root"
    parfile = basepath + basename + ".para.root"
    outfile = basepath + basename + ".digi.root"
    logfile = basepath + basename + ".digi.log"

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
    with open(logfile, "w") as log, wurlitzer.pipes(stdout=log, stderr=wurlitzer.STDOUT):
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


# Ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior.
# As a result, the same process can't be reused after the first run.
# Here, create a fully standalone process that is fully destroyed afterwards.
# TODO: Once/If this is fixed, remove this and rename the impl function
def digitization(distance, doubleplane, energy, erel, neutron, physics, scenario):
    d = [
        "python",
        "digitization.py",
        str(distance),
        str(doubleplane),
        str(energy),
        str(erel),
        str(neutron),
        str(physics),
        str(scenario),
    ]
    subprocess.call(d)


if __name__ == "__main__":
    distance = int(sys.argv[1])  # 15
    doubleplane = int(sys.argv[2])  # 30
    energy = int(sys.argv[3])  # 600
    erel = int(sys.argv[4])  # 100
    neutron = int(sys.argv[5])  # 4
    physics = sys.argv[6] if len(sys.argv) >= 7 else "inclxx"
    scenario = sys.argv[7] if len(sys.argv) >= 8 else "vacuum"
    digitization_impl(distance, doubleplane, energy, erel, neutron, physics, scenario, overwrite=True)
