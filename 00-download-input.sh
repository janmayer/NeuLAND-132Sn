#!/usr/bin/env bash

# Downloads the input files for NeuLAND Simulations (Sn-132 Case)

set -e
mkdir -p input
for energy in 200 600 1000; do
	for erel in 100 500; do
		curl -s "https://www.r3broot.gsi.de/data/event_${energy}AMeV_${erel}keV.tar.gz" | tar --strip 1 -C input -xvz
	done
done
