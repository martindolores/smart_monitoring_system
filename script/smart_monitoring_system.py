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

sensor = Adafruit_DHT.DHT22
DHT22_PIN = 18
bus_number = 1
device_address = 0x23
SOIL_MOISTURE_SENSOR = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOIL_MOISTURE_SENSOR, GPIO.OUT)

#Email Setup
sender_email = 'martindolores65@gmail.com'
receiver_email = 'martindolores65@gmail.com'
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = sender_email
smtp_password = 'gueaqloxiudpgcyg'

#Particle Argon
access_token = "0796096240632ac381c0ff9462594a1951a0d25c"
device_id = "e00fce689d45860e19261d67"
headers = {
    "Authorization": f"Bearer {access_token}", 
    "Content-Type": "application/x-www-form-urlencoded"    
}

#Particle Function
temp_function = "changeTemp"
light_function = "ChangeLux"
soil_function = "changeSoil"

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

def post_particle(value, variable):
    url = f"https://api.particle.io/v1/devices/{device_id}/{variable}"
    data = {"arg": str(value)}
    response = requests.post(url, headers=headers, data=data, timeout=180)
    print(f"Request URL: {url}")
    print(f"Request Headers: {headers}")
    print(f"Request Data: {data}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content.decode('utf-8')}")
    if response.status_code == 200:
        print("Data sent successfully")
    else:
        print("Failed to send data")

# Read the analog value from the sensor
def read_moisture():
    # Set the duty cycle to 50%
    pwm.ChangeDutyCycle(50)

    # Wait for 10 milliseconds
    time.sleep(0.01)

    # Read the analog value from the sensor
    moisture_value = GPIO.input(SOIL_MOISTURE_SENSOR)

    # Return the moisture value
    return moisture_value

# Set the PWM frequency to 50 Hz
pwm = GPIO.PWM(SOIL_MOISTURE_SENSOR, 50)

# Start the PWM with a duty cycle of 0%
pwm.start(0)

def read_lux():
    # Read data from sensor
    data = bus.read_i2c_block_data(device_address, 0x20, 2)
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
    post_particle(round(lux, 2), light_function);
    
    if sendLuxEmail:
        send_email('LUX LEVEL', 'Warning: The current lux level is {}'.format(lux))
    
        
def read_temp_hum():
    # Read the temperature and humidity values and send temp to particle
    humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT22_PIN)

    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.2f}°C")
        print(f"Humidity: {humidity:.2f}%")
        sendTempEmail = temperature < 15.5 or temperature > 24
        post_particle(round(temperature, 2), temp_function);
        if sendTempEmail:
            send_email('TEMPERATURE', 'Warning: The current temperature is {}'.format(temperature))
    else:
        print("Failed to retrieve data from DHT22 sensor")

def read_moisture_level():
    # Read the moisture value 10 times and print the average and send to particle
    moisture_sum = 0
    for i in range(10):
        moisture_sum += read_moisture()

    moisture_avg = moisture_sum / 10
    print(f"Soil moisture value: {moisture_avg}")
    sendSoilEmail = moisture_avg < 0.6 or moisture_avg > 0.8
    post_particle(round(moisture_avg, 2), soil_function);
    if sendSoilEmail:
        send_email('MOISTURE LEVEL', 'Warning: The current moisture level is {}'.format(moisture_avg))

with SMBus(bus_number) as bus:
    while True:
        read_lux()		  
        read_temp_hum()           
        read_moisture_level()
        # Wait before taking another measurement
        time.sleep(10)
