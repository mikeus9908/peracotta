#!/usr/bin/python3

"""
Read "decode-dimms" output
"""

import sys
from InputFileNotFoundError import InputFileNotFoundError
from enum import Enum
from dataclasses import dataclass


class ECC(Enum):
	available = "yes"
	not_available = "no"


@dataclass
class Dimm:
	type = "ram"
	brand = ""
	model = ""
	serial_number = ""
	frequency = -1
	capacity = -1
	ram_type = ""  # DDR, DDR2, DDR3 etc.
	ecc = ECC.not_available
	cas_latencies = ""
	manufacturer_data_type = ""


# initial_chars_to_ignore is the length of the feature whose name the line begins with
# e.g. "Fundamental Memory Type" begins with 23 characters that are not all spaces, then n spaces to ignore,
# and finally there's the value needed, e.g. "DDR3 SDRAM"
def ignore_spaces(line: str, initial_chars_to_ignore: int):
	relevant_part = line[initial_chars_to_ignore:]
	return relevant_part.strip()


def read_decode_dimms(path: str, interactive: bool = False):
	try:
		with open(path, 'r') as f:
			output = f.read()
	except FileNotFoundError:
		raise InputFileNotFoundError(path)

	if interactive:
		print("Reading decode-dimms...")

	# this optimization can crash the script if output is empty
	# last_line = output.splitlines()[-1]

	# check based on output of decode-dimms v6250
	if "Number of SDRAM DIMMs detected and decoded: 0" in output\
		or "Number of SDRAM DIMMs detected and decoded: " not in output:
		if interactive:
			print("decode-dimms was not able to find any RAM details")
		return []

	# split strings in 1 str array for each DIMM
	dimm_sections = output.split("Decoding EEPROM")
	# remove useless first part
	del dimm_sections[0]

	# create list of as many dimms as there are dimm_sections
	dimms = [Dimm() for _ in range(len(dimm_sections))]

	for i, dimm in enumerate(dimm_sections):
		for line in dimm.splitlines():
			if line.startswith("Fundamental Memory type"):
				dimms[i].ram_type = line.split(" ")[-2].lower()
				if dimms[i].ram_type == 'unknown':
					dimms[i].ram_type = ''

			if line.startswith("Maximum module speed"):
				freq = line.split(" ")[-3:-1]
				dimms[i].frequency = int(freq[0])
				if "KHz" in freq[1] or "kHz" in freq[1]:
					dimms[i].frequency *= 1000
				elif "MHz" in freq[1]:
					dimms[i].frequency *= 1000 * 1000
				elif "GHz" in freq[1]:
					dimms[i].frequency *= 1000 * 1000 * 1000
				# The official thing is 667 MHz even if they run at 666 MHz
				if dimms[i].frequency == 666000000:
					dimms[i].frequency = 667000000

			if line.startswith("Size"):
				cap = line.split(" ")[-2:]
				dimms[i].capacity = int(cap[0])
				if "KB" in cap[1] or "kB" in cap[1]:
					dimms[i].capacity *= 1024
				elif "MB" in cap[1]:
					dimms[i].capacity *= 1024 * 1024
				elif "GB" in cap[1]:
					dimms[i].capacity *= 1024 * 1024 * 1024

			# alternatives to "Manufacturer" are "DRAM Manufacturer" and "Module Manufacturer"
			if "---=== Manufacturer Data ===---" in line:
				dimms[i].manufacturer_data_type = "DRAM Manufacturer"

			if "---=== Manufacturing Information ===---" in line:
				dimms[i].manufacturer_data_type = "Manufacturer"

			if line.startswith(dimms[i].manufacturer_data_type):
				if dimms[i].manufacturer_data_type == "DRAM Manufacturer":
					dimms[i].brand = ignore_spaces(line, len("DRAM Manufacturer"))
				elif dimms[i].manufacturer_data_type == "Manufacturer":
					dimms[i].brand = ignore_spaces(line, len("Manufacturer"))

			# This seems to always be the model (or at least never be the serial number)
			if line.startswith("Part Number"):
				dimms[i].model = ignore_spaces(line, len("Part Number"))

			# part number can be overwritten by serial number if present
			if line.startswith("Assembly Serial Number"):
				dimms[i].serial_number = ignore_spaces(line, len("Assembly Serial Number"))
				if dimms[i].serial_number.startswith('0x'):
					try:
						dimms[i].serial_number = str(int(dimms[i].serial_number[2:], base=16))
					except ValueError:
						# Ooops, this isn't an hex number after all...
						pass

			if line.startswith("Module Configuration Type") and (
					"Data Parity" in line or "Data ECC" in line or "Address/Command Parity" in line):
				dimms[i].ecc = ECC.available

			# Two (or more) spaces after because there are lines like "tCL-tRCD-tRP-tRAS as ..."
			if line.startswith("tCL-tRCD-tRP-tRAS  "):
				dimms[i].cas_latencies = ignore_spaces(line, len("tCL-tRCD-tRP-tRAS"))

	dimms_dicts = []
	for dimm in dimms:
		dimms_dicts.append({
			"type": "ram",
			"brand": dimm.brand,
			"model": dimm.model,
			"sn": dimm.serial_number,
			"frequency-hertz": dimm.frequency,
			"capacity-byte": dimm.capacity,
			"ram-type": dimm.ram_type,
			"ram-ecc": str(dimm.ecc.value),
			"ram-timings": dimm.cas_latencies,
			"working": 'yes',  # Indeed it is working
		})

	return dimms_dicts


if __name__ == '__main__':
	import json
	try:
		result = read_decode_dimms(sys.argv[1], True)
		print(json.dumps(result, indent=2))
	except InputFileNotFoundError as e:
		print(str(e))
		exit(1)
