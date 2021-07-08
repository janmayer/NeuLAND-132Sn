import pathlib


def filename_for(distance, doubleplane, energy, erel, neutron, physics, what):
    basepath = "output/%s/" % physics.lower()
    pathlib.Path(basepath).mkdir(parents=True, exist_ok=True)
    basename = "%dm_%ddp_%dAMeV_%dkeV_%dn" % (
        distance,
        doubleplane,
        energy,
        erel,
        neutron,
    )
    return basepath + basename + what
