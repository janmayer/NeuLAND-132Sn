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
vmcworkdir = os.environ["VMCWORKDIR"]
os.environ["GEOMPATH"] = vmcworkdir + "/geometry"
os.environ["CONFIG_DIR"] = vmcworkdir + "/gconfig"
os.environ["PHYSICSLIST"] = "QGSP_INCLXX_HP"


def simulate(distance, energy, doubleplane, neutron, erel, overwrite=False):
    outfile = filepattern % (distance, doubleplane, energy, erel, neutron, "simu")

    # Re-Process only if explicitly asked to
    if not overwrite and os.path.isfile(outfile):
        print("Exists: " + outfile)
        return None

    # Write all output to a log file
    logfile = outfile.replace(".root", ".log")
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
    return None


# Single simulation
# simulate(distance=15, energy=600, doubleplane=8, neutron=1, erel=100, overwrite=True)


# Parallel simulations
joblib.Parallel(n_jobs=-1, backend="multiprocessing", verbose=11)(
    joblib.delayed(simulate)(
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
