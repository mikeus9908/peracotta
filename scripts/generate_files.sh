#!/bin/bash

# Dependencies on Debian:
# pciutils i2c-tools mesa-utils smartmontools dmidecode

# -e -> exit on first error
# -u -> exit if unused variable is found
# -x -> show every command that is run
set -ux

if [ $# -eq 0 ]; then
    echo "No path given: outputting files to working directory"
    OUTPATH="."
elif [ $# -eq 1 ]; then
    echo "Outputting files to $1"
    OUTPATH="$1"
else
    echo -n "Unexpected number of parameters.\nUsage: sudo ./generate_files.sh /optional/path/to/files"
fi

# Already done on our custom distro, but repetita iuvant
modprobe at24
modprobe eeprom
decode-dimms > "$OUTPATH/dimms.txt"

dmidecode -t baseboard > "$OUTPATH/baseboard.txt"
dmidecode -t connector > "$OUTPATH/connector.txt"
dmidecode -t chassis > "$OUTPATH/chassis.txt"
truncate -s 0 "$OUTPATH/net.txt"  # Create empty file or delete content
NET=($(find /sys/class/net -maxdepth 1 \( -name "en*" -o -name "wl*" \) -exec basename  '{}' ';'))
for NETDEV in "${NET[@]}"
do
	ADDRESS=$(cat "/sys/class/net/$NETDEV/address")
	if [[ $? -ne 0 ]]; then
		echo The \"invalid argument\" error above is normal, disregard it
	fi
	SPEED=$(cat "/sys/class/net/$NETDEV/speed")
	echo "$NETDEV $ADDRESS $SPEED" >> "$OUTPATH/net.txt"
done
lscpu > "$OUTPATH/lscpu.txt"
lspci -v > "$OUTPATH/lspci.txt"
glxinfo > "$OUTPATH/glxinfo.txt"
DISKZ=($(lsblk -d -I 8 -o NAME -n))
echo Found ${#DISKZ[@]} disks
for d in "${DISKZ[@]}"; do
	smartctl -x /dev/"$d" > "$OUTPATH/smartctl-dev-$d.txt"
done

# Add an empty file if no disk is detected
[[ ${#DISKZ[@]} -eq 0 ]] && touch "$OUTPATH/smartctl-dev-nodisk.txt"
