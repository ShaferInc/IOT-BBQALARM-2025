import network
import time
from machine import Pin
from umqtt.simple import MQTTClient
from max6675 import MAX6675

# --- ❗️ UPDATE THESE VALUES ❗️ ---
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "YOUR_ADAFRUIT_USERNAME"
AIO_KEY = "YOUR_ADAFRUIT_IO_KEY"
AIO_CLIENT_ID = "pico-grill-monitor"

# This is the "Feed" you create on Adafruit IO
AIO_TEMP_FEED = "YOUR_ADAFRUIT_USERNAME/feeds/temperature" 
# ------------------------------------

# --- Hardware Setup ---
sck = Pin(10, Pin.OUT)
cs = Pin(13, Pin.OUT)
so = Pin(12, Pin.IN)
thermo = MAX6675(sck, cs, so)

def connect_wifi():
    """Connects the device to Wi-Fi."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print('Network connected:', wlan.ifconfig())
    return wlan

def main():
    """Main function to run the thermometer."""
    connect_wifi()
    client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, port=AIO_PORT, user=AIO_USER, password=AIO_KEY)
    
    try:
        client.connect()
        print("Successfully connected to Adafruit IO!")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return

    while True:
        try:
            temp_c = thermo.read()
            temp_f = (temp_c * 9/5) + 32
            
            print(f"Temperature: {temp_c:.2f}°C, {temp_f:.2f}°F")
            
            # Publish the Celsius value to the Adafruit IO feed
            client.publish(topic=AIO_TEMP_FEED, msg=str(temp_c))
            print("Published to Adafruit IO.")
            
            # Send data every 30 seconds
            time.sleep(30)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Reconnecting in 15 seconds...")
            time.sleep(15)
            main() # Attempt to restart the main function on error

if __name__ == "__main__":
    main()