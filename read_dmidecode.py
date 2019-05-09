#!/usr/bin/env python3

import subprocess as sp
import sys

class Baseboard:
    def __init__(self):
        self.type = "motherboard"
        self.brand = ""
        self.model = ""
        self.serial_number = ""
        # self.form_factor = "" # not detected by dmidecode

class Chassis:
    def __init__(self):
        self.type = "case" # TODO: ?
        self.brand = ""
        self.model = ""
        self.serial_number = ""

# TODO: implement read of connector.txt
class Port:
    def __init__(self):
        self.type = ""

# tmp/baseboard.txt
def get_baseboard(path: str):
    mobo = Baseboard()

    # p = sp.Popen(['sudo dmidecode -t baseboard'], shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    # out = p.communicate()
    # strings = str.split(str(out[0]), sep="\\n")

    try:
        with open(path, 'r') as f:
            output = f.read()
    except FileNotFoundError:
        print("Cannot open file.")
        print("Make sure to execute 'sudo ./generate_files.sh' first!")
        exit(-1)

    for line in output.splitlines():
        if "Manufacturer" in line:
            mobo.brand = line.split("Manufacturer:")[1].strip()

        if "Product Name" in line:
            mobo.model = line.split("Product Name:")[1].strip()

        if "Serial Number" in line:
            mobo.serial_number = line.split("Serial Number:")[1].strip()

    result = {
        "type": mobo.type,
        "brand": mobo.brand,
        "model": mobo.model,
        "serial_number": mobo.serial_number
    }

    for key, value in result.items():
        if value == "Unknown":
            del result[key]
            result[key] = None

    return result

def get_chassis(path: str):
    chassis = Chassis()

    # p = sp.Popen(['sudo dmidecode -t chassis'], shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    # out = p.communicate()
    # strings = str.split(str(out[0]), sep="\\n")

    try:
        with open(path, 'r') as f:
            output = f.read()
    except FileNotFoundError:
        print("Cannot open file.")
        print("Make sure to execute 'sudo ./generate_files.sh' first!")
        exit(-1)

    for line in output.splitlines():
        if "Manufacturer" in line:
            chassis.brand = line.split("Manufacturer:")[1].strip()

        if "Type" in line:
            chassis.model = line.split("Type:")[1].strip()

        if "Serial Number" in line:
            chassis.serial_number = line.split("Serial Number:")[1].strip()

    result = {
        "type": chassis.type,
        "brand": chassis.brand,
        "model": chassis.model,
        "serial_number": chassis.serial_number
    }

    for key, value in result.items():
        if value == "Unknown":
            del result[key]
            result[key] = None

    return result

if __name__ == '__main__':
    get_baseboard(sys.argv[1])