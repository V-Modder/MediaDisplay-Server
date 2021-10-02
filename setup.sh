#!/bin/bash

function main {
    ensure_root
    install_pyusb
    add_group_plugdev_to_user
    add_udev_rule
}

function ensure_root {
    if [ "$EUID" -ne 0 ]; then
        echo "Please run as root"
        exit 1
    fi
}

function install_pyusb {
    pip install pyusb
}

function add_group_plugdev_to_user {
    for d in "/home/"*; do
        username=$(basename $d)
        if groups $username | grep -q '\bplugdev\b'; then
            echo "User already in group plugdev"
        else 
            useradd -G plugdev "${username}" 
        fi
    done
}

function add_udev_rule {
    echo "Updating udev rule"
    echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"0403\", ATTR{idProduct}==\"6001\", GROUP=\"plugdev\", MODE=\"660\", ENV{MODALIAS}=\"ignore\"" > /lib/udev/rules.d/60-relay_ft245r.rules
}

main
