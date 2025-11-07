import serial
import joblib
import pandas as pd
import time
import requests
import os

model = joblib.load("aqi_model.pkl")

feature_names = [
    "CO2(ppm)", "C6H6(ppm)", "Alcohol(ppm)", "NH3(ppm)",
    "Temperature(C)", "Relative_Humidity(%)"
]

arduino = serial.Serial(port="COM4", baudrate=9600, timeout=1)
time.sleep(2)

API_URL = "http://aqi-env.eba-2xewf2jm.us-east-1.elasticbeanstalk.com/update"  # later change to your AWS URL

while True:
    try:
        line = arduino.readline().decode().strip()
        if not line:
            continue

        values = list(map(float, line.split(",")))
        if len(values) != 6:
            continue

        X = pd.DataFrame([values], columns=feature_names)
        aqi = model.predict(X)[0] * 18.5
        aqi_rounded = round(float(aqi), 2)

        payload = {
            "aqi": aqi_rounded,
            "sensors": {
                "CO2": round(values[0], 2),
                "C6H6": round(values[1], 2),
                "Alcohol": round(values[2], 2),
                "NH3": round(values[3], 2),
                "Temperature": round(values[4], 2),
                "Relative_Humidity": round(values[5], 2)
            }
        }

        requests.post(API_URL, json=payload, timeout=5)
        print(f"✅ Sent AQI: {aqi_rounded}")
        time.sleep(5)

    except Exception as e:
        print("⚠ Error:", e)
        time.sleep(3)