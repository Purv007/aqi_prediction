#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define MQ_PIN A0
#define RL 10.0
float Ro = 4.77;   // fixed pre-set value

float getPPM(float ratio, float a, float b) {
  return a * pow(ratio, b);
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(MQ_PIN, INPUT);
}

void loop() {
  // --- Read DHT22 ---
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // --- Read MQ135 with temp & humidity correction ---
  int adcValue = analogRead(MQ_PIN);
  float correctedADC = adcValue * (1.0 + 0.01 * (t - 20)) * (1.0 + 0.02 * (h - 50));
  if (correctedADC > 1023) correctedADC = 1023;

  float vrl = (correctedADC / 1023.0) * 5.0;
  float rs = (5.0 - vrl) * RL / vrl;
  float ratio = rs / Ro;

  // --- Gas concentrations ---
  float co2_ppm     = getPPM(ratio, 110.47, -2.862);
  float nh3_ppm     = getPPM(ratio, 102.2,  -2.473);
  float alcohol_ppm = getPPM(ratio, 77.255, -3.18);
  float benzene_ppm = getPPM(ratio, 44.947, -3.445); // this is your C6H6

  // --- Print in CSV format for Python ---
  if (!isnan(h) && !isnan(t)) {
    Serial.print(co2_ppm);     Serial.print(",");
    Serial.print(benzene_ppm); Serial.print(",");
    Serial.print(alcohol_ppm); Serial.print(",");
    Serial.print(nh3_ppm);     Serial.print(",");
    Serial.print(t);           Serial.print(",");
    Serial.println(h);
  }

  delay(5000); // every 5 seconds
}
