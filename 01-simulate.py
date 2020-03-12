import os
import sys
import random
from joblib import Parallel, delayed, parallel_backend
import ROOT


distances = [15, 35]
doubleplanes = [8, 12, 30]
energies = [600]
erels = [100, 500]
neutrons = [1, 2, 3, 4, 5]
filepattern = "output/%dm_%ddp_%dAMeV_%dkeV_%dn.%s.root"

ROOT.ROOT.EnableThreadSafety()
ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
ROOT.FairLogger.GetLogger().SetLogScreenLevel("WARNING")

vmcworkdir = os.environ["VMCWORKDIR"]
os.environ["GEOMPATH"] = vmcworkdir + "/geometry"
os.environ["CONFIG_DIR"] = vmcworkdir + "/gconfig"
os.environ["PHYSICSLIST"] = "QGSP_INCLXX_HP"


def simulate(distance, energy, doubleplane, neutron, erel, overwrite=False):
    simufile = filepattern % (distance, doubleplane, energy, erel, neutron, "simu")

    if not overwrite and os.path.isfile(simufile):
        print("Exists: " + simufile)
        return

    # Redirect stdout / stderr to log files
    sys.stdout = open(simufile.replace(".root", ".log"), "w")
    sys.stderr = open(simufile.replace(".root", ".err"), "w")

    # Initialize Simulation
    run = ROOT.FairRunSim()
    run.SetName("TGeant4")
    run.SetStoreTraj(False)
    run.SetMaterials("media_r3b.geo")

    # Output
    output = ROOT.FairRootFileSink(simufile)
    run.SetSink(output)

    # Primary Generator
    generator = ROOT.FairPrimaryGenerator()
    inputfile = "%s/input/%dSn_%dn_%dAMeV_%dkeV.dat" % (
        vmcworkdir,
        132 - neutron,
        neutron,
        energy,
        erel,
    )
    generator.AddGenerator(ROOT.R3BAsciiGenerator(inputfile))
    run.SetGenerator(generator)

    # Geometry
    cave = ROOT.R3BCave("Cave")
    cave.SetGeometryFileName("r3b_cave_vacuum.geo")
    run.AddModule(cave)

    neuland_position = ROOT.TGeoTranslation(0.0, 0.0, distance + doubleplane * 10.0 / 2.0)
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
    parafile = filepattern % (distance, doubleplane, energy, erel, neutron, "para")
    parout = ROOT.FairParRootFileIo(True)
    parout.open(parafile)
    rtdb.setOutput(parout)
    rtdb.saveOutput()

    run.Run(10000)
    return


# simulate(distance=15, energy=600, doubleplane=8, neutron=1, erel=100, overwrite=True)


with parallel_backend('multiprocessing'):
    results = Parallel(n_jobs=30, verbose=11)(
        delayed(simulate)(distance, energy, doubleplane, neutron, erel, overwrite=False)
        for distance in distances
        for energy in energies
        for doubleplane in doubleplanes
        for neutron in neutrons
        for erel in erels
    )
