import sys
from linkkit import linkkit
import threading
import traceback
import inspect
import time
import logging

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)


class CustomerThing(object):
    def __init__(self):
        self.__linkkit = linkkit.LinkKit(
            host_name="cn-shanghai",
            product_key="xxxxxxxxxxx",
            device_name="device-name",
            device_secret="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
        self.__linkkit.enable_logger(logging.DEBUG)
        self.__linkkit.on_device_dynamic_register = self.on_device_dynamic_register
        self.__linkkit.on_connect = self.on_connect
        self.__linkkit.on_disconnect = self.on_disconnect
        self.__linkkit.on_topic_message = self.on_topic_message
        self.__linkkit.on_subscribe_topic = self.on_subscribe_topic
        self.__linkkit.on_unsubscribe_topic = self.on_unsubscribe_topic
        self.__linkkit.on_publish_topic = self.on_publish_topic
        self.__linkkit.on_thing_enable = self.on_thing_enable
        self.__linkkit.on_thing_disable = self.on_thing_disable
        self.__linkkit.on_thing_raw_data_post = self.on_thing_raw_data_post
        self.__linkkit.on_thing_raw_data_arrived = self.on_thing_raw_data_arrived
        self.__linkkit.thing_setup()
        self.__linkkit.config_device_info("Eth|03ACDEFF0032|Eth|03ACDEFF0031")

    def on_device_dynamic_register(self, rc, value, userdata):
        if rc == 0:
            print("dynamic register device success, value:" + value)
        else:
            print("dynamic register device fail, message:" + value)

    def on_connect(self, session_flag, rc, userdata):
        print("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))

    def on_disconnect(self, rc, userdata):
        print("on_disconnect:rc:%d,userdata:" % rc)

    def on_topic_message(self, topic, payload, qos, userdata):
        print("on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))
        pass

    def on_subscribe_topic(self, mid, granted_qos, userdata):
        print("on_subscribe_topic mid:%d, granted_qos:%s" %
              (mid, str(','.join('%s' % it for it in granted_qos))))
        pass

    def on_unsubscribe_topic(self, mid, userdata):
        print("on_unsubscribe_topic mid:%d" % mid)
        pass

    def on_publish_topic(self, mid, userdata):
        print("on_publish_topic mid:%d" % mid)

    def on_thing_enable(self, userdata):
        print("on_thing_enable")

    def on_thing_disable(self, userdata):
        print("on_thing_disable")

    def on_thing_raw_data_arrived(self, payload, userdata):
        print("on_thing_raw_data_arrived:%r" % payload)
        print("prop data:%r" % self.rawDataToProtocol(payload))

    def on_thing_raw_data_post(self, payload, userdata):
        print("on_thing_raw_data_post: %s" % str(payload))

    def rawDataToProtocol(self, byte_data):
        alink_data = {}
        head = byte_data[0]
        if head == 0x01:
            alink_data["method"] = "thing.service.property.set"
            alink_data["version"] = "1.0"
            alink_data["id"] = int.from_bytes(byte_data[1:5], "big")
            params = {}
            params["prop_int16"] = int.from_bytes(byte_data[5:7], "big")
            alink_data["params"] = params
            return alink_data

    def protocolToRawData(self, params):
        # command set
        payload_bytes = b'\x00'
        # id
        payload_bytes += b'\x00'
        payload_bytes += b'\x00'
        payload_bytes += b'\x00'
        payload_bytes += b'\x01'
        # prop_int16 big en
        prop_int16 = params["prop_int16"]
        payload_bytes += bytes([prop_int16 // 256])
        payload_bytes += bytes([prop_int16 % 256])
        return payload_bytes

    def user_loop(self):
        self.__linkkit.connect_async()
        tips = "1: disconnect\n" +\
               "2 connect&loop\n" +\
               "3 subscribe topic\n" + \
               "4 unsubscribe topic\n" + \
               "5 public topic\n" +\
               ""
        while True:
            try:
                msg = input()
            except KeyboardInterrupt:
                sys.exit()
            else:
                if msg == "1":
                    params = {
                        "prop_int16": 11
                    }
                    payload = self.protocolToRawData(params)
                    print("payload:%r" % payload.hex())
                    self.__linkkit.thing_raw_post_data(payload)
                    pass
                else:
                    sys.exit()


if __name__ == "__main__":
    custom_thing = CustomerThing()
    custom_thing.user_loop()
