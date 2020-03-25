import joblib
import subprocess
from simulation import simulation


distances = [15, 35]
doubleplanes = [8, 12, 30]
energies = [200, 600, 1000]
erels = [100, 500]
neutrons = [1, 2, 3, 4, 5, 6]
physicss = ["bert", "bic", "inclxx"]
scenarios = ["air", "vacuum"]


# Parallel simulations
joblib.Parallel(n_jobs=-1, backend="loky", verbose=11)(
    joblib.delayed(simulation)(
        distance=distance,
        doubleplane=doubleplane,
        energy=energy,
        erel=erel,
        neutron=neutron,
        physics=physics,
        scenario=scenario)
    for distance in distances
    for energy in energies
    for doubleplane in doubleplanes
    for neutron in neutrons
    for erel in erels
    for physics in physicss
    for scenario in scenarios
)
