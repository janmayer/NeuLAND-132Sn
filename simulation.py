import os
import sys
import subprocess
import pathlib
import random


def simulation_impl(distance, doubleplane, energy, erel, neutron, physics, scenario, overwrite):
    from helpers import stdout_redirector
    import ROOT

    # Workaround, as the GLAD Magnet is filled with air and the VacuumChamber does not exist
    # The Sn will react a lot in air, so either run in vacuum or remove the Sn (later will screw with E_rel)
    scenarios = {
        "air": {
            "inp": "input/%dSn_%dn_%dAMeV_%dkeV_noSn.dat.bz2",
            "geo": "r3b_cave.geo"
        },
        "vacuum": {
            "inp": "input/%dSn_%dn_%dAMeV_%dkeV.dat.bz2",
            "geo": "r3b_cave_vacuum.geo"
        },
    }

    inpfile = scenarios[scenario]["inp"] % (132 - neutron, neutron, energy, erel)

    basepath = "output/%s-%s/" % (physics.lower(), scenario)
    pathlib.Path(basepath).mkdir(parents=True, exist_ok=True)

    basename = "%dm_%ddp_%dAMeV_%dkeV_%dn" % (distance, doubleplane, energy, erel, neutron)
    parfile = basepath + basename + ".para.root"
    outfile = basepath + basename + ".simu.root"
    logfile = basepath + basename + ".simu.log"

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
    os.environ["PHYSICSLIST"] = f"QGSP_{physics.upper()}_HP"

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
        cave.SetGeometryFileName(scenarios[scenario]["geo"])
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


# Ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior.
# As a result, the same process can't be reused after the first run.
# Here, create a fully standalone process that is fully destroyed afterwards.
# TODO: Once/If this is fixed, remove this and rename the impl function
def simulation(distance, doubleplane, energy, erel, neutron, physics, scenario):
    d = [
        "python",
        "simulation.py",
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
    simulation_impl(distance, doubleplane, energy, erel, neutron, physics, scenario, overwrite=False)
