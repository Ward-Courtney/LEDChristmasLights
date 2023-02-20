from umqttsimple import MQTTClient
import network
from machine import Pin
from time import sleep


 # This class uses the wifiConnect function to activate the station 
 # interface to connect to the wifi using the network ssid
 # and password. If an error is encountered, the system will use the
 # reconnect function to reconnectup to 60 times. The device will reset
 # if attempts go over 60. If connection is successful the system will
 # display the network configuration.
class WiFi:
    
    def wifiConnect():
        
        # Station Interface.
        wlan = network.WLAN(network.STA_IF)                  
        wlan.active(True)                                    
        
        # Sets Access Point to False to hide the access point
        # SSID in order to prevent un-authorized connections.
        ap = network.WLAN(network.AP_IF)                     
        ap.active(False)                                     
                                                             
        wlan.connect(ssid, wifipwd)
        print(f'Connecting to {ssid}...')
        sleep(3)
        
        # See comment block above.
        attempts = 0
        while not wlan.isconnected():
            attempts += 1
            if attempts > 60:
                machine.reset()
            sleep(1)
            
            print(wlan.status())
        return print("Network Config", wlan.ifconfig())
    
    # See comment block above.
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

def mqttMain():
    client = MQTTClient(broker, port, username, password,keepalive=60)
    client.connect()
    sleep(1)
    return client

# This function calls the WiFi class to connect to wifi in order to connect
# to broker. It resets the device if connection fails.
# It also calls the mqttMain function to pull the broker's
# information to connect to it and publishes ON/OFF messages to the broker 
# depending on the motion sensor data readings, in order to trigger the 
# LED lights that are subscribed to the broker.  
def main():
    pir.irq(trigger = Pin.IRQ_RISING, handler = handle_interrupt)
    
    try:
        # Calling mqttMain function to connect to broker
        # and assign it to client variable.
        client = mqttMain()
        print('Connected to Broker')                          
        # Calling the WiFi class and assigning it to network variable
        # and connecting to it.
        network = WiFi()
        network.wifiConnect()
        print('Connected to WiFi')
        
    # explained in comment block above.    
    except OSError as e:
        if not wlan.isconnected():
            print('Failed to connect to WiFi')
        network.reconnect()
    
    else:
        while True:
        # This is a Forever loop used to detect motion repeatedly. If motion 
        # is/ins't detected the MQTTMain function (called client) will
        # publish/subscribe to the broker using the pubTopic. If motion
        # detected the MQTTMain function will publish an ON message to turn 
        # the lights on for 5 minutes. If motion is no longer detected the
        # MQTTMain function will publish an OFF message to turn the lights off.
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
                sleep(1)
                client.disconnect()

#
ssid = 'TILTOperations'
wifipwd = 'TILTops11235' 

# This is our broker information used to
# connect to the Mosquitto broker hosted
# on the Raspberry Pi. 
# The broker's IP address will fluctuate
# depending on what network the RaspBerry
# Pi is connected to.
broker = '192.168.21.93'  # Update if connected to different wifi than specified above.       
port = 1883                        
username = 'WLED'                 
password = 'Toyota'

# 
pubTopic = 'wled/a'

# Declares and initalizes sensor value to no-motion in order to be used to
# detect motion
motion = False   

# Motion sensor is in pin 14
pir = Pin(14, Pin.IN)


main()