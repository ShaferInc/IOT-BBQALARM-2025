# IoT Grill Thermometer: A Step-by-Step Tutorial

**By:** Henry Shafer hs223nr

-----

## Short Project Overview

This tutorial walks you through building a smart Wi-Fi-enabled thermometer for your grill. Using a Raspberry Pi Pico W and a K-type thermocouple, this device will measure the internal temperature of your grill and send the data to a cloud platform. You can then monitor the temperature remotely from your phone or computer and receive notifications when your grill reaches the perfect temperature for cooking.

**Estimated Time to Complete:** 2-3 hours

-----

## Objective

### Why this project?

The main reason for this project is to take the guesswork out of grilling. Achieving a consistent and precise temperature is key to perfectly cooked food, whether you're slow-smoking ribs or searing a steak. This device allows for remote monitoring, so you don't have to constantly be near the grill to check the temperature.

### What is the purpose?

The primary purpose is to create a reliable and accurate way to measure and track the temperature of a grill. The data will be sent to an online dashboard, making it accessible from anywhere with an internet connection. The system will be designed to send alerts when a user-defined temperature is reached.

### What insights will it give?

By collecting and visualizing temperature data over time, you can gain several insights:

  * **Heating Patterns:** Understand how long your specific grill takes to heat up to certain temperatures.
  * **Temperature Stability:** Analyze how well your grill maintains a consistent temperature.
  * **Cooking Profiles:** Create and refine temperature profiles for different types of food to ensure repeatable, perfect results every time.

-----

## Materials

Here is a list of the components needed for this project. Note that while the MAX6675 module may come with a basic thermocouple, this tutorial assumes you are using the more robust, separately purchased probe.

| Component | Description & Specifications |
| :--- | :--- |
| **Raspberry Pi Pico W** | A microcontroller with a dual-core Arm Cortex M0+ processor and a 2.4 GHz Wi-Fi chip. The pre-soldered headers are recommended for easy breadboarding. |
| **MAX6675 Module** | A K-type thermocouple to digital converter. It translates the analog signal from the probe into a digital format for the Pico W to read via the SPI protocol. |
| **Robust K-Type Thermocouple** | The high-temperature sensor probe you purchased separately. It should have `+` and `-` markings for correct polarity. |
| **Solderless Breadboard & Jumper Wires** | Used to build and prototype the circuit without any soldering. |
| **Micro USB Cable** | Connects the Raspberry Pi Pico W to your computer for power and programming. |

-----

## Computer Setup 💻

This project uses **Visual Studio Code (VS Code)** with an extension to program the Raspberry Pi Pico W in MicroPython.

1.  **Install VS Code:** If you don't already have it, download and install VS Code from the [official website](https://code.visualstudio.com/).

2.  **Flash MicroPython:**

      * Download the latest MicroPython firmware `.uf2` file from the [Raspberry Pi website](https://micropython.org/download/RPI_PICO_W/).
      * Hold down the **BOOTSEL** button on your Pico W and plug it into your computer. It will appear as a USB drive named `RPI-RP2`.
      * Drag and drop the downloaded `.uf2` file onto that drive. The Pico W will restart and now run MicroPython.

3.  **Install the Pico-W-Go Extension:**

      * Open VS Code.
      * Go to the **Extensions** view (click the icon with four squares on the sidebar).
      * Search for **`Pico-W-Go`** and click **Install**. This extension allows you to connect to your Pico, upload files, and run code directly from the editor.

4.  **Configure the Project:**

      * Connect your Pico W to your computer (if you disconnected it).
      * Open your project folder in VS Code.
      * Click the `Pico-W-Go >` button in the blue status bar at the bottom of the VS Code window to connect to the device.

-----

## Putting Everything Together 🍞

Here’s how to wire the components on your breadboard.

1.  **Place the Components:**

      * Press the **Raspberry Pi Pico W** into the breadboard so it straddles the central channel.
      * Place the **MAX6675 module** nearby, also straddling the central channel.

2.  **Connect Power and Ground:**

      * Connect pin **36 (3V3 OUT)** on the Pico to the **positive (+)** power rail of the breadboard with a jumper wire.
      * Connect pin **38 (GND)** on the Pico to the **negative (-)** ground rail with another jumper wire.
      * Now, connect the **VCC** pin on the MAX6675 to the **positive (+)** rail and the **GND** pin on the MAX6675 to the **negative (-)** rail.

3.  **Connect the Data (SPI) Pins:**

      * Connect **SCK** on the MAX6675 to **GP10** (physical pin 14) on the Pico W.
      * Connect **SO** (Serial Out) on the MAX6675 to **GP12** (physical pin 16) on the Pico W.
      * Connect **CS** (Chip Select) on the MAX6675 to **GP13** (physical pin 17) on the Pico W.

4.  **Connect Your Thermocouple Probe:**

      * Loosen the screws on the green terminal block of the MAX6675 module.
      * Insert the wire or prong from your robust thermocouple marked with a **`+`** into the terminal on the module also marked with a **`+`**.
      * Insert the wire marked with a **`-`** into the terminal marked with a **`-`**.
      * Tighten both screws to ensure a good connection. **Matching the polarity is critical for an accurate reading.**

-----

## Platform

We'll use **Adafruit IO** as our IoT platform. It's a free, cloud-based service that's easy to set up for viewing data and creating alerts. Its user-friendly dashboards and reliable MQTT integration make it perfect for this project.

-----

## The Code

You will need two files on your Pico W. Use VS Code to create these files and the **Pico-W-Go** extension to upload them to your device.

### 1\. Sensor Driver (`max6675.py`)

This file is a library that handles the low-level communication with the MAX6675 sensor.

```python
# MAX6675 MicroPython Driver
from machine import Pin
import time

class MAX6675:
    def __init__(self, sck, cs, so):
        self.sck = sck
        self.cs = cs
        self.so = so
        self.cs.value(1)

    def read(self):
        self.cs.value(0)
        time.sleep_us(10)
        
        value = 0
        for i in range(16):
            self.sck.value(1)
            time.sleep_us(1)
            if self.so.value():
                value = (value << 1) | 1
            else:
                value = value << 1
            self.sck.value(0)
            time.sleep_us(1)
            
        self.cs.value(1)

        if (value & 0x4):
            raise Exception("Thermocouple is not connected.")

        temp_data = (value >> 3) & 0xFFF
        celsius = temp_data * 0.25
        
        return celsius
```

### 2\. Main Application (`main.py`)

This is the main script that runs your thermometer. **Remember to fill in your personal credentials.**

```python
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
```

-----

## Transmitting the Data / Connectivity

  * **How often is the data sent?** Data is sent every **30 seconds**.
  * **Which wireless protocol did you use?** The project uses **Wi-Fi**, leveraging the built-in wireless chip on the Pico W.
  * **Which transport protocol was used?** **MQTT** is used to efficiently send small packets of data to the Adafruit IO server. This combination is ideal for a stationary home IoT device where power consumption is not the primary concern.

-----

## Presenting the Data 📊

Your user interface is the **Adafruit IO dashboard**, viewable on any desktop or mobile browser.

1.  **Create a Feed:** In Adafruit IO, go to `Feeds > New Feed` and create a feed named **`temperature`**. This must match your code.
2.  **Create a Dashboard:** Go to `Dashboards > New Dashboard`.
3.  **Add Blocks (Widgets):**
      * **Gauge:** Add a gauge block linked to your `temperature` feed to see the current grill temp.
      * **Line Chart:** Add a line chart block, also linked to the `temperature` feed, to visualize temperature over time.
      * **Trigger an Action:** Use the `Actions` menu to set up email or other notifications when your `temperature` feed goes above a certain value.

-----

## Finalizing the Design

The final result is a functional smart thermometer that sends live grill temperatures to a clean web dashboard.

### Final Thoughts & Improvements:

  * **Enclosure:** The most important next step is to create a 3D-printed or project box enclosure to protect the Pico W and other electronics from heat and the elements.
  * **Power Source:** A portable USB power bank can be used to make the device more mobile and easier to place near the grill.
  * **Local Display:** Adding a small OLED screen would be a great upgrade to show the temperature and connection status directly on the device.