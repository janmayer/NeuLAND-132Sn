import os
import random
import joblib
from helpers import stdout_redirector
import ROOT


distances = [15, 35]
doubleplanes = [8, 12, 30]
energies = [200, 600, 1000]
erels = [100, 500]
neutrons = [1, 2, 3, 4, 5, 6]


ROOT.ROOT.EnableThreadSafety()
ROOT.FairLogger.GetLogger().SetLogVerbosityLevel("LOW")
ROOT.FairLogger.GetLogger().SetLogScreenLevel("WARNING")
ROOT.gROOT.SetBatch(True)



def calibr(distance, doubleplane, energy, erel, nmax):
    filepattern = "output/%dm_%ddp_%dAMeV_%dkeV_%dn.%s.root"
    outfile = filepattern % (distance, doubleplane, energy, erel, nmax, "ncut")

    # Write all output to a log file
    logfile = outfile.replace(".root", ".log")
    with stdout_redirector(logfile):
        cal = ROOT.Neuland.Neutron2DCalibr(nmax)
        for neutron in range(1, nmax + 1):
            digifile = filepattern % (distance, doubleplane, energy, erel, neutron, "digi")
            cal.AddClusterFile(digifile)

        # Starting parameters (double val, double step, double lower, double upper)
        vslope = ROOT.std.vector('double')()
        vslope += [0.04, 0.001, 0.001, 10]
        vdistance = ROOT.std.vector('double')()
        vdistance += [energy / 20., energy / 100., energy / 100., energy]
        vdist_off = ROOT.std.vector('double')()
        vdist_off += [3, 0.5, 3, 6]

        # Create Cuts
        cal.Optimize(vslope, vdistance, vdist_off);

        # Write the output files (root, dat, pdf)
        cal.WriteParameterFile(outfile)
        o = ROOT.std.ofstream(outfile.replace(".root", ".dat"))
        cal.Print(o)
        cal.Draw(outfile.replace(".root", ".pdf"))


# Parallel simulations
joblib.Parallel(n_jobs=-1, backend="multiprocessing", verbose=11)(
    joblib.delayed(calibr)(
        distance=distance,
        doubleplane=doubleplane,
        energy=energy,
        erel=erel,
        nmax=neutron)
    for distance in distances
    for energy in energies
    for doubleplane in doubleplanes
    for neutron in neutrons
    for erel in erels
)
