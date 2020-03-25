#!/usr/bin/env bash
set -e

# Downloads the input files for NeuLAND Simulations (Sn-132 Case)
mkdir -p tmpinp
for energy in 200 600 1000; do
	for erel in 100 500; do
		curl -s "https://www.r3broot.gsi.de/data/event_${energy}AMeV_${erel}keV.tar.gz" | tar --strip 1 -C tmpinp -xvz
	done
done

# Fix problems with input files and provide compressed versions
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
			# Remove superfluous event parameters
			# Remove some leading whitespace
			cat $tmp | \
				head -n -$(expr $n + 2) | \
				cut -c -118 | \
				sed "s/      ${nx}      0.0      0.0/      ${nx}/g" | \
				sed "s/^      //g" | \
				tee $in | gzip --best > "${in}.gz"
			bzip2 --keep --best ${in}
			# Remove Sn from input files for simulating with air
			# Correct the number of tracks accordingly
			cat $in | grep -v " -1     50 " | sed "s/      ${nx}\$/      ${n}/g" | tee $out | gzip --best > "${out}.gz"
			bzip2 --keep --best ${out}
		done
	done
done

rm -r tmpinp
