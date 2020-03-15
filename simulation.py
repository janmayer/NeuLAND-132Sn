import os
import sys
from helpers import stdout_redirector
import ROOT
import random


def simulation(distance, doubleplane, energy, erel, neutron, overwrite=False):
    namepattern = "%dm_%ddp_%dAMeV_%dkeV_%dn"
    name = namepattern % (distance, doubleplane, energy, erel, neutron)

    filepattern = "output/%s.%s.%s"
    inpfile = "input/%dSn_%dn_%dAMeV_%dkeV.dat" % (132 - neutron, neutron, energy, erel)
    parfile = filepattern % (name, "para", "root")
    outfile = filepattern % (name, "simu", "root")
    logfile = filepattern % (name, "simu", "log")

    if not os.path.isfile(inpfile):
        print(f"Input {inpfile} does not exist")
        return

    if not overwrite and os.path.isfile(outfile):
        print(f"Output {outfile} exists and overwriting is disabled")
        return

    ROOT.ROOT.EnableThreadSafety()
    ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
    ROOT.FairLogger.GetLogger().SetLogScreenLevel("WARNING")

    vmcworkdir = os.environ["VMCWORKDIR"]
    os.environ["GEOMPATH"] = vmcworkdir + "/geometry"
    os.environ["CONFIG_DIR"] = vmcworkdir + "/gconfig"
    os.environ["PHYSICSLIST"] = "QGSP_INCLXX_HP"

    # Write all output to a log file
    with stdout_redirector(logfile):
        # Initialize Simulation
        run = ROOT.FairRunSim()
        run.SetName("TGeant4")
        run.SetStoreTraj(False)
        run.SetMaterials("media_r3b.geo")

        # Output
        output = ROOT.FairRootFileSink(outfile)
        run.SetSink(output)

        # Primary Generator
        generator = ROOT.FairPrimaryGenerator()
        generator.AddGenerator(ROOT.R3BAsciiGenerator(inpfile))
        run.SetGenerator(generator)

        # Geometry
        cave = ROOT.R3BCave("Cave")
        cave.SetGeometryFileName("r3b_cave_vacuum.geo")
        #cave.SetGeometryFileName("r3b_cave.geo")
        run.AddModule(cave)

        neuland_position = ROOT.TGeoTranslation(0.0, 0.0, distance * 100 + doubleplane * 10.0 / 2.0)
        neuland = ROOT.R3BNeuland(doubleplane, neuland_position)
        run.AddModule(neuland)

        magnetic_field = ROOT.R3BGladFieldMap("R3BGladMap")
        magnetic_field.SetScale(-0.6)
        run.SetField(magnetic_field)

        # Prepare to run
        run.Init()
        ROOT.TVirtualMC.GetMC().SetRandom(ROOT.TRandom3(random.randint(0, 10000)))
        ROOT.TVirtualMC.GetMC().SetMaxNStep(100000)

        # Runtime Database
        rtdb = run.GetRuntimeDb()
        parout = ROOT.FairParRootFileIo(True)
        parout.open(parfile)
        rtdb.setOutput(parout)
        rtdb.saveOutput()

        run.Run(10000)


if __name__ == "__main__":
    distance = int(sys.argv[1])
    doubleplane = int(sys.argv[2])
    energy = int(sys.argv[3])
    erel = int(sys.argv[4])
    neutron = int(sys.argv[5])
    simulation(distance, doubleplane, energy, erel, neutron, overwrite=False)
