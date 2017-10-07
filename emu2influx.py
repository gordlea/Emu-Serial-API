# emu2influx
# read InstantaneousDemand stanzas and throw 'em into influxdb

from __future__ import print_function
import time
from emu import emu
from influxdb import InfluxDBClient

INFLUX_HOST = "influx"
INFLUX_PORT = 8086
INFLUX_USER = ''
INFLUX_PASS = ''
INFLUX_DB = 'home'

EMU_DEVICE = "emu2"

try:
    EMU = emu(EMU_DEVICE)
    EMU.start_serial()
    ICLIENT = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)
    ICLIENT.create_database(INFLUX_DB)
    while True:
        if EMU.history:
            MSG = EMU.history.pop(0)
            if MSG['origin'] == "EMU":
                MOBJ = MSG['obj']
                if MSG['type'] == "InstantaneousDemand":
                    TS_LOC = int(time.strftime('%s'))
                    TS_RSP = int(MOBJ.TimeStamp, base=16) + 946684800
                    TS_SPD = TS_LOC - TS_RSP
                    PWR_USE = int(MOBJ.Demand, base=16)

                    #print("{0} (took {1}s): {2} kW".format(
                    #    TS_RSP, TS_SPD, PWR_USE))

                    INFLUX_POINT = [{
                        "measurement": "instantaneous_demand",
                        "tags": {
                            "device_mac_id": MOBJ.DeviceMacId,
                            "meter_mac_id": MOBJ.MeterMacId,
                        },
                        "time": TS_RSP * 1000000000,
                        "fields": {
                            "demand": PWR_USE,
                            "multiplier": int(MOBJ.Multiplier, base=16),
                            "divisor": int(MOBJ.Divisor, base=16),
                            "digits_left": int(MOBJ.DigitsLeft, base=16),
                            "digits_right": int(MOBJ.DigitsRight, base=16),
                        }
                    }]
                    print(INFLUX_POINT)
                    ICLIENT.write_points(INFLUX_POINT)
        time.sleep(1)
finally:
    EMU.stop_serial()
