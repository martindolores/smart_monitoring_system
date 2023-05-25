import time
import pyi2c
import Adafruit_DHT
import RPi.GPIO as GPIO
from pyi2c import SMBus
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import string
sensor = Adafruit_DHT.DHT22
DHT22_PIN = 18
bus_number = 1
device_address = 0x23
SOIL_MOISTURE_SENSOR = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_MOISTURE_SENSOR, GPIO.OUT)

#Email Setup
sender_email = '{SENDER_EMAIL}'
receiver_email = '{RECEIVER_EMAIL}'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = sender_email
smtp_password = '{SENDER_EMAIL_PASS}'

#Sensors
plant_one_sensor = {
    "DHT22_PIN": DHT22_PIN,
    "SOIL_MOISTURE_SENSOR": SOIL_MOISTURE_SENSOR,
    "LIGHT_SENSOR_ADDRESS": device_address
}
#plant_two_sensor = {...}
#plant_three_sensor = {...}


#Plants
plant_one = {
    "name": "Plant One",
    "temp": 0,
    "light": 0,
    "soil": 0
}
#plant_two
#plant_three


def generate_plant(): 
    chars = string.ascii_letters + string.digits
    name = ''.join(random.choice(chars) for _ in range(4))
    plant = {
        "temp": random.randint(0,99),
        "light": random.randint(0,99),
        "soil": random.randint(0,99),
        "name": name
    }
    return plant


def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print('Email Sent:' + subject)
    except Exception as e:
        print('Error sending email:', str(e))

def post_thinkspeak(plant, api_key):
    url = "https://api.thingspeak.com/update"
    payload = {
        "api_key": api_key,
        "field1": plant["temp"],
        "field2": plant["light"],
        "field3": plant["soil"]
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Data sent successfully")
    else:
        print("Failed to send data")
        save_data_to_file(plant)

def save_data_to_file(plant):
    current_datetime = datetime.now()
    with open("{}.txt".format(plant["name"]), "a") as file:
        file.write("[{}]: Temp - {}, Soil - {}, Lux - {}".format(current_datetime.strftime("%Y-%m-%d %H:%M:%S"), plant["temp"], plant["soil"], plant["lux"]))

# Read the analog value from the sensor
def read_moisture(plant_sensor):
    # Set the duty cycle to 50%
    pwm.ChangeDutyCycle(50)

    # Wait for 10 milliseconds
    time.sleep(0.01)

    # Read the analog value from the sensor
    moisture_value = GPIO.input(plant_sensor["SOIL_MOISTURE_SENSOR"])

    # Return the moisture value
    return moisture_value

# Set the PWM frequency to 50 Hz
pwm = GPIO.PWM(SOIL_MOISTURE_SENSOR, 50)

# Start the PWM with a duty cycle of 0%
pwm.start(0)

def read_lux(plant_sensor, plant):
    # Read data from sensor
    data = bus.read_i2c_block_data(plant_sensor["LIGHT_SENSOR_ADDRESS"], 0x20, 2)
    # Convert data to lux
    raw_value = (data[1] + (256 * data[0]))
    lux = raw_value / 1.2

    # Determine light level
    if lux > 100000:
        message = "Too bright"
    elif lux > 1000:
        message = "Bright"
    elif lux > 100:
        message = "Medium"
    elif lux > 10:
        message = "Dark"
    else:
        message = "Too dark"
    
    sendLuxEmail = lux < 1000 or lux > 3000
    # Print the data and message and send to particle
    print("Light level: {} lux - {}".format(lux, message))
    plant["light"] = round(lux,2)
    
    if sendLuxEmail:
        send_email('LUX LEVEL', 'Warning: The current lux level is {} for {}'.format(lux, plant["name"]))
    
        
def read_temp_hum(plant_sensor, plant):
    # Read the temperature and humidity values and send temp to particle
    humidity, temperature = Adafruit_DHT.read_retry(sensor, plant_sensor["DHT22_PIN"])

    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.2f}°C")
        print(f"Humidity: {humidity:.2f}%")
        sendTempEmail = temperature < 15.5 or temperature > 24
        plant["temp"] = round(temperature, 2)
        if sendTempEmail:
            send_email('TEMPERATURE', 'Warning: The current temperature is {} for {}'.format(temperature, plant["name"]))
    else:
        print("Failed to retrieve data from DHT22 sensor")

def read_moisture_level(plant_sensor, plant):
    # Read the moisture value 10 times and print the average and send to particle
    moisture_sum = 0
    for i in range(10):
        moisture_sum += read_moisture(plant_sensor)

    moisture_avg = moisture_sum / 10
    print(f"Soil moisture value: {moisture_avg}")
    sendSoilEmail = moisture_avg < 0.6 or moisture_avg > 0.8
    plant["soil"] = moisture_avg
    if sendSoilEmail:
        send_email('MOISTURE LEVEL', 'Warning: The current moisture level is {} for {}'.format(moisture_avg, plant["name"]))

with SMBus(bus_number) as bus:
    while True:
        #plant one
        read_lux(plant_one_sensor, plant_one)		  
        read_temp_hum(plant_one_sensor, plant_one)           
        read_moisture_level(plant_one_sensor, plant_one)
        post_thinkspeak(plant_one, "{CHANNEL_ONE_API}")
        
        #mock plants and sensors for UI
        ##plant 2
        ###read_lux(plant_two_sensor, plant_two)		  
        ###read_temp_hum(plant_two_sensor, plant_two)           
        ###read_moisture_level(plant_two_sensor, plant_two)
        post_thinkspeak(generate_plant(), "{CHANNEL_TWO_API}")
        ##plant 3
        ###read_lux(plant_three_sensor, plant_three)		  
        ###read_temp_hum(plant_three_sensor, plant_three)           
        ###read_moisture_level(plant_three_sensor, plant_three)
        post_thinkspeak(generate_plant(), "{CHANNEL_THREE_API}")
        # Wait before taking another measurement
        time.sleep(10)
