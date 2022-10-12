#!/usr/bin/env python3

import os, sys, shelve
from datetime import datetime, timedelta

# system-specific
AC_STATUS = "/sys/class/power_supply/ACAD/online"
CHARGE_FULL = "/sys/class/power_supply/BAT1/charge_full"
CHARGE_NOW = "/sys/class/power_supply/BAT1/charge_now"
MEM_SLEEP = "/sys/power/mem_sleep"
VOLTAGE_DESIGN = "/sys/class/power_supply/BAT1/voltage_min_design"

TMP_FILE = "/tmp/powerdrainpy.shelve"


def read_charge(path):
    with open(path, "r") as f:
        data = f.readlines()[0]
    return int(data.strip())

def read_battery_capacity():
    with open(CHARGE_FULL, "r") as f:
        charge_full = int(f.readlines()[0].strip())
    with open(VOLTAGE_DESIGN, "r") as f:
            volt_design = int(f.readlines()[0].strip())

    return (charge_full /1e6) * (volt_design / 1e6)

def percentage_now():
    full = read_charge(CHARGE_FULL)
    now = read_charge(CHARGE_NOW)

    return now/full


def is_plugged_in(path):
    with open(path, "r") as f:
        data = f.readlines()[0]
    return int(data.strip()) == 1

def write_stats():
    with shelve.open(TMP_FILE) as sh:
        sh["suspend_start"] = datetime.now()
        sh["percentage_start"] = percentage_now()

def read_stats():
    with shelve.open(TMP_FILE, "r") as sh:
        suspend_start = sh["suspend_start"]
        percentage_start = sh["percentage_start"]
    return suspend_start, percentage_start

def os_info():
    release = os.uname().release

    with open(MEM_SLEEP, "r") as f:
        sleep_mode = f.read().strip()

    return f"kernel: {release} sleep mode: {sleep_mode}"


#  ['/usr/lib/systemd/system-sleep/testenv.py', 'pre', 'suspend'] <- suspending
#  ['/usr/lib/systemd/system-sleep/testenv.py', 'post', 'suspend'] <- resuming

if sys.argv[1] == "pre":
    if is_plugged_in(AC_STATUS):
        try:
            os.remove(TMP_FILE)
        except OSError:
            pass
        exit()
    
    write_stats()
elif sys.argv[1] == "post":
    if is_plugged_in(AC_STATUS):
      exit()

    try:
        suspend_start, percentage_start = read_stats()
    except Exception:
        exit()

    sleep_time = (datetime.now() - suspend_start).seconds  # in seconds
    percentage_diff = percentage_start - percentage_now()

    discharge_percent_hour = 60.0 * 60 * 100.0 * percentage_diff / sleep_time
    discharge_mW_hour = read_battery_capacity() * 1e3 *  (discharge_percent_hour / 100)

    sleep_hours = sleep_time // 3600
    sleep_minutes = (sleep_time % 3600) // 60
    sleep_seconds = (sleep_time % 3600) % 60

    print(f"Suspend duration: {sleep_hours}h {sleep_minutes:02d}m {sleep_seconds:02d}s")
    print(f"Discharge rate: {discharge_percent_hour:.3f} %/h ({discharge_mW_hour:.0f} mW/h)")
    print(os_info())

    try:
        os.remove(TMP_FILE)
    except OSError:
        pass