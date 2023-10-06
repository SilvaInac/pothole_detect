import esp32
import time
import network
from umqttsimple import MQTTClient
from machine import UART


BROKER_PORT = 1883
BROKER_MQTT = "test.mosquitto.org"
ID_MQTT = "C115CarlosFrancisco"
TOPIC_SUBSCRIBE = "GETDETECTINFO"
TOPIC_PUBLISH = "POTHOLE"

WIFINAME ="WLL-Inatel"
WIFIKEY = "inatelsemfio"

last_message = 0
message_interval = 3
counter = 0

#callback
def sub_cb(topic,msg):
    print((topic,msg))
    if topic == b'notification' and msg == b'received':
        print("ESP received hello message")
        
def connect_and_subscribe(client_id,mqtt_server,topic_sub):
    client =MQTTClient(client_id,mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print("Connect to %s MQTT broker, subscribed to %s topic" %(mqtt_server,topic_sub))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()


def connect_Wifi(ssid,key):
    wlan = network.WLAN(network.STA_IF) # create station interface
    wlan.active(True)       # activate the interface
    wlan.scan()
    if(not wlan.isconnected()):
        print("Connecting...")
        try:
            wlan.connect(ssid,key) # connect to an AP 
            while wlan.isconnected() == False:
              pass
            print('Connection successful!!')
            print(wlan.ifconfig())
        except Exception as error:
            print("erro:",error)


#connect to WIFI
connect_Wifi(WIFINAME,WIFIKEY)
print("Initializing")

#connect to UART OPENMV
uart = UART(2, 115200)  # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1)  # init with given parameters
uart.write("Iniciar\n")  # write the 3 characters

#connect to mqtt
try:
    client = connect_and_subscribe(ID_MQTT,BROKER_MQTT,TOPIC_SUBSCRIBE)
except OSError as e:
    restart_and_reconnect()

while True:        
    result = uart.readline()  # read all available characters
    if result != None:
        resultString = result.decode("utf-8")
        if str("detect") in resultString:
            try:
                client.check_msg()
                if(time.time() - last_message) > message_interval:
                    msg = b'pothole detect #%d' % counter #counter potholes detect
                    print("pothole detect #%d" %counter)
                    client.publish(TOPIC_PUBLISH,msg)
                    last_message = time.time()
                    counter += 1
            except OSError as e:
                print("restarting")
                restart_and_reconnect()
        time.sleep(0.1)

