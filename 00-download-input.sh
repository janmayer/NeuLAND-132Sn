#!/usr/bin/env bash
set -e

# Downloads the input files for NeuLAND Simulations (Sn-132 Case)
mkdir -p tmpinp
for energy in 200 600 1000; do
	for erel in 100 500; do
		curl -s "https://www.r3broot.gsi.de/data/event_${energy}AMeV_${erel}keV.tar.gz" | tar --strip 1 -C tmpinp -xvz
	done
done

# Fix problems with input files
mkdir -p input
for energy in 200 600 1000; do
	for erel in 100 500; do
		for n in 1 2 3 4 5 6; do
			sn=$(expr 132 - $n)
			nx=$(expr $n + 1)
			tmp="tmpinp/${sn}Sn_${n}n_${energy}AMeV_${erel}keV.dat"
			in="input/${sn}Sn_${n}n_${energy}AMeV_${erel}keV.dat"
			out="input/${sn}Sn_${n}n_${energy}AMeV_${erel}keV_noSn.dat"
			echo $in
			# Last entry (9999) is duplicated and damaged
			# Cutoff line to remove masses
			cat $tmp | head -n -$(expr $n + 2) | cut -c -118 > $in
			# Remove Sn from input files for simulating with air
			cat $in | grep -v " -1     50 " | sed "s/      ${nx}      0.0      0.0/      ${n}      0.0      0.0/g" > $out
		done
	done
done

rm -r tmpinp
