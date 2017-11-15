from emu import *
instance = emu('ttyACM0')
instance.start_serial()
# instance.get_current_price("20")
instance.get_current_summation_delivered()
# print(hex(int(time.strftime('%s')) - 946684800 + 500))
# instance.set_fast_poll('0x01', hex(int(time.strftime('%s')) - 946684800))
# time.sleep(5)


while True:
    # instance.get_fast_poll_status()
    time.sleep(5)
    instance.get_current_summation_delivered()


    # instance.get_price_blocks()

    while len(instance.history) > 0:
        history_obj = instance.history.pop(0)
    #
    # for history_obj in instance.history:
        histType = history_obj['type']
        if (histType == 'CurrentSummationDelivered'):# or (histType == 'PriceCluster'):
        # print(history_obj['origin'])
        # print()
            print(history_obj['raw'])
    # if type(history_obj['obj'] == 'NetworkInfo'):
    #     print(history_obj['obj'].Status)

# instance.get_current_summation()
# instance.get_current_summation_delivered()
# time.sleep(5)
# instance.stop_serial()
# print(instance.CurrentSummationDelivered)
# print(instance.CurrentSummationDelivered.SummationDelivered)
# for hist in instance.history:
#     print(hist)

# instance.get_network_info()
#
# time.sleep(5)
# print(instance.NetworkInfo)
# instance.stop_serial()
