# emu2influx
# read InstantaneousDemand stanzas and throw 'em into influxdb

from __future__ import print_function
import time
from emu import emu
from influxdb import InfluxDBClient

INFLUX_HOST = "localhost"
INFLUX_PORT = 8888
INFLUX_USER = ''
INFLUX_PASS = ''
INFLUX_DB = 'home'

EMU_DEVICE = "ttyACM0"

PRICE_BLOCK_COUNTER = 0
PRICE_BLOCK_COUNTER_MAX=10
COST_COUNTER = 0
COST_COUNTER_MAX=15

try:
    EMU = emu(EMU_DEVICE)
    EMU.start_serial()
    # EMU.set_fast_poll('0x60', '0x00000001')
    EMU.get_fast_poll_status()
    EMU.get_current_price("1")
    ICLIENT = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)
    ICLIENT.create_database(INFLUX_DB)
    EMU.get_price_blocks()
    # time.sleep(5)
    while True:
        time.sleep(1)
        PRICE_BLOCK_COUNTER += 1
        if (PRICE_BLOCK_COUNTER == PRICE_BLOCK_COUNTER_MAX):
            PRICE_BLOCK_COUNTER = 0
            EMU.get_price_blocks()
        COST_COUNTER += 1
        if (COST_COUNTER == COST_COUNTER_MAX):
            COST_COUNTER = 0
            EMU.get_current_price("1")
            emu.get_current_summation_delivered()


        if EMU.history:
            while len(EMU.history) > 0:
                print("EMU.history length =" + str(len(EMU.history)))
            # for MSG in EMU.history:
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
                    if MSG['type'] == "PriceCluster":
                        TS_LOC = int(time.strftime('%s'))
                        TS_RSP = int(MOBJ.TimeStamp, base=16) + 946684800
                        TS_SPD = TS_LOC - TS_RSP
                        PRICE = int(MOBJ.Price, base=16)
                        #print("{0} (took {1}s): {2} kW".format(
                        #    TS_RSP, TS_SPD, PWR_USE))

                        INFLUX_POINT = [{
                            "measurement": "price_cluster",
                            "tags": {
                                "device_mac_id": MOBJ.DeviceMacId,
                                "meter_mac_id": MOBJ.MeterMacId,
                            },
                            "time": TS_RSP * 1000000000,
                            "fields": {
                                "price": PRICE,
                                "currency": int(MOBJ.Currency, base=16),
                                "tier": int(MOBJ.Tier, base=16),
                                # "rate_label": str(MOBJ.RateLabel),
                            }
                        }]
                        print(INFLUX_POINT)
                        ICLIENT.write_points(INFLUX_POINT)
                    if MSG['type'] == "BlockPriceDetail":
                        TS_LOC = int(time.strftime('%s'))
                        TS_RSP = int(MOBJ.TimeStamp, base=16) + 946684800
                        TS_SPD = TS_LOC - TS_RSP
                        # PRICE = int(MOBJ.Price, base=16)
                        #print("{0} (took {1}s): {2} kW".format(
                        #    TS_RSP, TS_SPD, PWR_USE))

                        INFLUX_POINT = [{
                            "measurement": "block_price_detail",
                            "tags": {
                                "device_mac_id": MOBJ.DeviceMacId,
                                "meter_mac_id": MOBJ.MeterMacId,
                            },
                            "time": TS_RSP * 1000000000,
                            "fields": {
                                "block_period_consumption": int(MOBJ.BlockPeriodConsumption, base=16),
                                "block_period_consumption_multiplier": int(MOBJ.BlockPeriodConsumptionMultiplier, base=16),
                                "block_period_consumption_divisor": int(MOBJ.BlockPeriodConsumptionDivisor, base=16),
                                "number_of_blocks": int(MOBJ.NumberOfBlocks, base=16),
                                "multiplier": int(MOBJ.Multiplier, base=16),
                                "divisor": int(MOBJ.Divisor, base=16),
                                "trailing_digits": int(MOBJ.TrailingDigits, base=16),
                                "price_1": int(MOBJ.Price1, base=16),
                                "price_2": int(MOBJ.Price2, base=16),
                                "threshold_1": int(MOBJ.Threshold1, base=16),
                            }
                        }]
                        print(INFLUX_POINT)
                        ICLIENT.write_points(INFLUX_POINT)

finally:
    EMU.stop_serial()
