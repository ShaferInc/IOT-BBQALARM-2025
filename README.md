# Smart Grill Master: A Wi-Fi-Enabled Grill Thermometer

### By: Henry Shafer (hs223nr)

This project walks you through creating a Wi-Fi-connected thermometer for your grill. Using a Raspberry Pi Pico W and a K-Type thermocouple, this device will measure the internal temperature of your grill and send the data to a cloud-based dashboard. This allows you to monitor your grill's temperature remotely from your phone or computer, ensuring your food is cooked to perfection every time.

### Project overview: 
Building a device to measure grill temperature and notify users.
Time to complete: 2-3 hours
Cost: $30-50

## Objective

The main goal of this project is to create a reliable and accurate way to monitor the temperature of a grill remotely.

Why this project? Have you ever undercooked or overcooked your food on the grill? This project solves that problem by providing temperature readings sent directly to a device of your choice. It's a practical application of IoT technology that can improve your cooking skills.

Purpose: The device will read the high temperatures inside a grill, which standard food thermometers can't withstand for long periods. It will then transmit this data over Wi-Fi to a cloud platform.

Data Insights: By logging temperature data over time, you can analyze your grill's heating patterns, identify hot spots, and understand how different factors like charcoal arrangement or lid placement affect the cooking temperature. This will help you achieve more consistent and predictable cooking results. You can also set up alerts to notify you when the grill reaches a specific temperature, so you know exactly when to start cooking or when your food is ready.

## Materials
Here is a list of the components needed for this project:

Raspberry Pi Pico W with Pre-Soldered Headers: This is the microcontroller that will serve as the brain of our project. It has built-in Wi-Fi, which is perfect for our IoT application.
Where to buy: Amazon
Cost: $10 - $15.

HiLetgo MAX6675 Module + K-Type Thermocouple: The K-Type thermocouple is a sensor capable of measuring a wide range of temperatures (0°C to 500°C for this model), making it ideal for a grill. The MAX6675 module is an amplifier that converts the thermocouple's analog signal into a digital one that our Pico W can read. WARNING-Frequently Faulty
Where to buy: Amazon
Cost: $5 - $10.

Yunsailing Type K Thermocouple Probe: This is the specific probe that will be placed inside the grill to measure the heat.
Where to buy: Amazon
Cost: $8 - $12.

Solderless Breadboard and Jumper Wires: These will be used to connect all the electronic components without needing to solder.
Where to buy: Included in most electronics starter kits on Amazon.
Cost: $10 - $15 for a kit.

Micro USB Cable: To connect the Raspberry Pi Pico W to your computer for programming and power.

## Computer Setup

To program the Raspberry Pi Pico W, we'll use the Thonny IDE, which is a beginner-friendly Python editor.

Install Thonny IDE: Download and install Thonny from the official website (thonny.org). It's available for Windows, Mac, and Linux.

### Flash MicroPython Firmware:

Download the latest MicroPython firmware for the Raspberry Pi Pico W. Go to the MicroPython downloads page and download the .uf2 file.

Connect your Pico W to your computer via a micro USB cable while holding down the BOOTSEL button. The Pico will appear as a mass storage device named RPI-RP2.

Drag and drop the downloaded .uf2 file onto the RPI-RP2 drive. The Pico will automatically reboot and will now be running MicroPython.

### Configure Thonny:

Open Thonny. Go to Tools -> Options.

In the Interpreter tab, select MicroPython (Raspberry Pi Pico) as the interpreter.

The port should be detected automatically. If not, try reconnecting your Pico.

### Install the MAX6675 Library:

In Thonny, go to Tools -> Manage packages.

Search for micropython-max6675 and click Install. This library will make it easy to read data from our temperature sensor.

## Putting Everything Together

Now, let's wire up the components. The connections are straightforward since we are using a breadboard.

### Wiring Instructions:

Connect the MAX6675 module to the Raspberry Pi Pico W as follows:

    GND (MAX6675) -> GND (Pico)

    VCC (MAX6675) -> 3V3(OUT) (Pico - Pin 36)

    SCK (MAX6675) -> GP10 (Pico - Pin 14)

    CS (MAX6675) -> GP11 (Pico - Pin 15)

    SO (MAX6675) -> GP12 (Pico - Pin 16)

Finally, connect the two pins from the K-Type thermocouple to the screw terminal on the MAX6675 module. The polarity doesn't matter for the screw terminals.

## Circuit Diagram:

Here is a diagram to help you visualize the connections:

# TO DO !!!

This setup is intended for development and prototyping. For a production version, you would want to solder the components onto a permanent protoboard and place the Pico W and MAX6675 module in a protective case to shield them from the elements and the heat of the grill.

## Platform

For this project, we'll use Adafruit as our IoT platform. It's a great choice for beginners because it offers a user-friendly interface, clear documentation, and a free educational license that provides enough credits for this project.

Functionality: Adafruit allows you to easily create dashboards with widgets like gauges, charts, and indicators to visualize your data in real-time. You can also set up events and alerts. For example, you can get an email or SMS notification when your grill reaches a certain temperature.

Why Adafruit? The platform has excellent support for MicroPython and the Raspberry Pi Pico W. Their documentation provides clear examples, which simplifies the process of sending data from our device to the cloud. The ability to quickly build a dashboard without any front-end coding makes it ideal for this project.

## The Code

The code for this project is written in MicroPython. The core functionalities are connecting to your Wi-Fi network, reading the temperature from the sensor, and sending it to Adafruit.

You can find the complete code in this repository.

Here is a snippet of the core logic:

```Python
# main.py
import machine
import time
import urequests
from max6675 import MAX6675
import network

# --- Your Wi-Fi and Adafruit Credentials ---
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
TOKEN = "YOUR_Adafruit_TOKEN" 
DEVICE_LABEL = "grill-thermometer"

# --- Pin Definitions ---
sck = machine.Pin(10, machine.Pin.OUT)
cs = machine.Pin(11, machine.Pin.OUT)
so = machine.Pin(12, machine.Pin.IN)

# --- Sensor Initialization ---
thermo = MAX6675(sck, cs, so)

# --- Function to connect to Wi-Fi ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

# --- Main Loop ---
connect_wifi(WIFI_SSID, WIFI_PASS)

while True:
    try:
        temp_c = thermo.read()
        temp_f = temp_c * 9/5 + 32
        print(f"Temperature: {temp_c}°C, {temp_f}°F")

        # --- Build the JSON payload ---
        payload = {VARIABLE_LABEL: {"value": temp_f}}

        # --- Send data to Adafruit ---
        url = f"https://industrial.api.Adafruit.com/api/v1.6/devices/{DEVICE_LABEL}"
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        
        response = urequests.post(url=url, headers=headers, json=payload)
        response.close()
        
        print("Data sent to Adafruit")
        
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(30) # Send data every 30 seconds
```
## Code Walk Through

This code first sets up the Wi-Fi connection and initializes the temperature sensor. Then, in an infinite loop, it reads the temperature, converts it to Fahrenheit, and sends it to Adafruit in a JSON format.

Transmitting the Data / Connectivity

Data Frequency: The data is sent to Adafruit every 30 seconds. This provides a good balance between real-time monitoring and not overwhelming the free tier of the Adafruit service.

Wireless Protocol: We are using Wi-Fi (802.11n), which is built into the Raspberry Pi Pico W. This is suitable for home use where the grill is within range of your Wi-Fi router.

Transport Protocol: The data is sent using an HTTP POST request (a webhook) to the Adafruit API. This is a simple and reliable way to send data to a web service. For a more advanced setup, MQTT would be a more efficient choice, as it is a lightweight messaging protocol designed for IoT devices and can reduce battery consumption. However, for this project, the simplicity of HTTP is sufficient.

## Presenting the Data

The data sent to Adafruit can be visualized on a custom dashboard.

Dashboard Creation: In Adafruit, you can create a new dashboard and add widgets. For this project, a gauge widget is perfect for showing the current temperature, and a line chart can display the temperature trend over time.

Data Retention: On the Adafruit free tier, data is typically stored for one month. For longer-term data storage, you would need to upgrade to a paid plan.

Automation/Triggers: Adafruit allows you to create triggers. For example, you can set up a rule to send you an email or a push notification when the temperature variable exceeds a certain value (e.g., 350°F), letting you know the grill is preheated and ready for cooking.

## Example Dashboard:

Here is what your dashboard could look like in Adafruit:

# TO DO !!!

## Finalizing the Design

This project successfully creates a functional smart grill thermometer. The final step is to assemble it in a way that is practical to use.

## Final Product:

For a more polished final product, you could design and 3D print a custom enclosure for the Raspberry Pi Pico W and the MAX6675 module. This would protect the electronics from heat and weather. The thermocouple probe would then be the only component placed inside the grill.

## Final Thoughts and Improvements:

What Went Well: The project was relatively simple to assemble thanks to the solderless breadboard and the user-friendly MicroPython libraries. The Raspberry Pi Pico W's built-in Wi-Fi made the IoT aspect straightforward.

### Potential Improvements:

Battery Power: To make the device truly wireless, it could be powered by a LiPo battery pack. This would require adding a battery charging circuit.

Multiple Probes: For more advanced grilling, you could add a second thermocouple to monitor the internal temperature of the food and the ambient temperature of the grill simultaneously.

Local Display: An OLED or LCD screen could be added to display the temperature directly on the device, so you don't always have to check your phone.

Overall, this project is an excellent introduction to building a practical IoT device and provides a solid foundation for more complex projects in the future.






PYCAD!!!!