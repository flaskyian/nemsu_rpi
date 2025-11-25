from flask import Flask, render_template, redirect, url_for, flash
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
app.secret_key = "secret"

GPIO.setmode(GPIO.BCM)

LIVING_LIGHT = 17
BUZZER = 27

GPIO.setup(LIVING_LIGHT, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

LIVING_LIGHT_STATE = False

@app.route('/')
def home():
    return render_template('index.html', light_on=LIVING_LIGHT_STATE)

@app.route('/light/on')
def light_on():
    global LIVING_LIGHT_STATE
    GPIO.output(LIVING_LIGHT, GPIO.HIGH)
    LIVING_LIGHT_STATE = True
    flash('Living Room Light turned ON.', 'success')
    return redirect(url_for('home'))

@app.route('/light/off')
def light_off():
    global LIVING_LIGHT_STATE
    GPIO.output(LIVING_LIGHT, GPIO.LOW)
    LIVING_LIGHT_STATE = False
    flash('Living Room Light turned OFF.', 'danger')
    return redirect(url_for('home'))

@app.route('/buzz')
def buzz():
    flash('Buzzer pressed!', 'warning')
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(BUZZER, GPIO.LOW)
    return redirect(url_for('home'))

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')
    finally:
        GPIO.cleanup()
