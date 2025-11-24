from flask import Flask, render_template
import RPi.GPIO as GPIO

app = Flask(__name__)

LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/on")
def turn_on():
    GPIO.output(LED_PIN, GPIO.HIGH)
    return render_template("index.html", status="on")

@app.route("/off")
def turn_off():
    GPIO.output(LED_PIN, GPIO.LOW)
    return render_template("index.html", status="off")

@app.route("/cleanup")
def cleanup():
    GPIO.cleanup()
    return "GPIO cleaned up."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
