# powerdrain.py

Tracks the power consumption of the system while suspended.

Tested with the Framework Laptop on Manjaro. Some paths might need to be adjusted for other machines.

## Installation


Requirements: `python >= 3.6`

1. If necessary, adjust the locations of `AC_STATUS`, `CHARGE_FULL`, `CHARGE_NOW`, `MEM_SLEEP`, and `VOLTAGE_DESIGN`.
2. Copy `powerdrain.py` to `/usr/lib/systemd/system-sleep/` and make sure it is executable.

	```
	sudo cp powerdrain.py /usr/lib/systemd/system-sleep/
	chmod +x /usr/lib/systemd/system-sleep/powerdrain.py
	```


## Usage

Power consumption during suspend state is automatically logged and accessible via:

```
journalctl -u systemd-suspend.service
```

Example output:
```
...
Okt 12 20:34:04 manjaro1 systemd-sleep[28104]: System returned from sleep state.
Okt 12 20:34:04 manjaro1 systemd-sleep[28182]: Suspend duration: 3h 25m 09s
Okt 12 20:34:04 manjaro1 systemd-sleep[28182]: Discharge rate: 1.352 %/h (734 mW/h)
Okt 12 20:34:04 manjaro1 systemd-sleep[28182]: kernel: 5.19.14-1-MANJARO sleep mode: [s2idle] deep

```

Events are ignored if AC is connected.

## Misc
powerdrain.py is inspired by [batdistrack](https://github.com/oliver-machacik/batdistrack). However, powerdrain.py also works on systems where `/sys/class/power_supply/BAT0/energy_now` is not available.