import joblib
import subprocess
# from simulation import simulation


distances = [15, 35]
doubleplanes = [8, 12, 30]
energies = [200, 600, 1000]
erels = [100, 500]
neutrons = [1, 2, 3, 4, 5, 6]
physicss = ["bert", "bic", "inclxx"]
scenarios = ["air", "vacuum"]


# Really ugly hack, as FairRun (FairRunSim, FairRunAna) has some undeleteable, not-quite-singleton behavior
# Here, create a fully standalone process that is fully destroyed afterwards
# Once/If this is fixed, remove this and import the function
def simulation(*args, **kwargs):
    d = [
        "python",
        "simulation.py",
        str(kwargs['distance']),
        str(kwargs['doubleplane']),
        str(kwargs['energy']),
        str(kwargs['erel']),
        str(kwargs['neutron']),
        str(kwargs['physics']),
        str(kwargs['scenario']),
    ]
    subprocess.call(d)


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
