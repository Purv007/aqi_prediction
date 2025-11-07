from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import boto3
import time
from decimal import Decimal

application = Flask(__name__)
CORS(application)

# DynamoDB configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('AQIReadings')

latest_data = None


@application.route("/")
def index():
    return render_template("index.html")


@application.route("/update", methods=["POST"])
def update():
    """
    Receives data from Arduino (via predict_serial.py)
    Converts floats to Decimals and stores in DynamoDB
    """
    global latest_data
    data = request.get_json()
    data["timestamp"] = int(time.time())
    latest_data = data

    try:
        # Convert float values to Decimal before writing to DynamoDB
        sensors = data.get("sensors", {})

        def safe_decimal(val):
            try:
                return Decimal(str(val))
            except:
                return Decimal("0")

        item = {
            "timestamp": data["timestamp"],
            "AQI": safe_decimal(data.get("aqi", 0)),
            "CO2": safe_decimal(sensors.get("CO2", 0)),
            "C6H6": safe_decimal(sensors.get("C6H6", 0)),
            "Alcohol": safe_decimal(sensors.get("Alcohol", 0)),
            "NH3": safe_decimal(sensors.get("NH3", 0)),
            "Temperature": safe_decimal(sensors.get("Temperature", 0)),
            "Relative_Humidity": safe_decimal(sensors.get("Relative_Humidity", 0))
        }

        table.put_item(Item=item)
        print(f"✅ Stored record at timestamp {data['timestamp']}")

    except Exception as e:
        print("❌ DynamoDB Error:", e)

    return jsonify({"status": "ok"})


@application.route("/latest")
def latest():
    """Returns the latest AQI data for web display"""
    if latest_data is None:
        return jsonify({"status": "waiting", "message": "No data received yet"}), 200
    return jsonify(latest_data)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)