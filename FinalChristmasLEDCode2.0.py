from umqttsimple import MQTTClient
import network
from machine import Pin
from time import sleep


class WiFi:
    # Connects to the wifi in order to publish payloads to the broker.
    def wifiConnect():
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        
        wlan.connect(ssid, wifipwd)
        print(f'Connecting to {ssid}...')
        sleep(3)
        attempts = 0
        while not wlan.isconnected():
            attempts += 1
            if attempts > 60:
                machine.reset()
            sleep(1)
            print(wlan.status())
        return print("Network Config", wlan.ifconfig())

    # If the ESP fails to connect to the broker because of an
    # OSError the reconnect function will preform a system reset.
    def reconnect():
        print('Failed to connect to the MQTT Broker. Reconnecting...')
        sleep(5)
        machine.reset()
            
 
 # Interrupt handling function to control PIR sensor.
def handle_interrupt(pin):
    global motion
    motion = True
    global interrupt_pin
    interrupt_pin = pin
    
# Establishes client and connects to the MQTT broker to publish
# payload later in the code.
def mqttMain():
    client = MQTTClient(clientID, broker, port, username, password,
                        \keepalive=60)
    client.connect()
    sleep(1)
    return client

def main():
    pir.irq(trigger = Pin.IRQ_RISING, handler = handle_interrupt)
    # The following code connects to WiFi and the MQTT broker
    # in order to publish a trigger to the lights based upon
    # if motion was detected from the Sensor.
    try:
        client = mqttMain()
        print('Connected to Broker')
        network = WiFi()
        network.wifiConnect()
        print('Connected to WiFi')
        
    except OSError as e:
        if not wlan.isconnected():
            print('Failed to connect to WiFi')
        network.reconnect()
        
    else:
        while True:
            if motion == True:
                client.connect()
                client.publish(pubTopic, "ON")
                print('Motion detected! Sending message.')
                sleep(300)
                client.disconnect()
                motion=False
            else:
                print('Motion not detected! Sending message.')
                client.connect()
                client.publish(pubTopic, "OFF")
                sleep(5)
                client.disconnect()

# This is the wifi information used by the WiFi class in order to connect to
# the TILTOperations network in order to allow the clients and broker to be
# connected over wifi.
ssid = 'TILTOperations'
wifipwd = 'TILTops11235'

# This is the broker information used to connect to the Mosquitto
# broker hosted on the Raspberry Pi in order to publish/scruibe the payload
# user to trigger the WLED lights on/off.
broker = '192.168.21.93'
port = 1883
username = 'WLED'
password = 'Toyota'

# ?????
clientID = 'Wled1234'
pubTopic = 'wled/a'

motion = False # Declares sensor value to use later in the code.

# Initalizes PIR sensor to be used later in code.
pir = Pin(14, Pin.IN)

main()