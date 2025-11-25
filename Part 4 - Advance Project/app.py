# app.py
from flask import Flask, render_template, jsonify, request
import threading
import time
import os

try:
    import RPi.GPIO as GPIO
    ON_PI = True
except (ImportError, RuntimeError):
    ON_PI = False

    class MockGPIO:
        BCM = 'BCM'
        OUT = 'OUT'
        LOW = False
        HIGH = True

        def __init__(self):
            self._state = {}

        def setmode(self, mode):
            print("[MockGPIO] setmode:", mode)

        def setup(self, pin, mode):
            self._state[pin] = False
            print(f"[MockGPIO] setup pin {pin} as {mode}")

        def output(self, pin, value):
            self._state[pin] = bool(value)
            print(f"[MockGPIO] output pin {pin} -> {value}")

        def input(self, pin):
            return self._state.get(pin, False)

        def cleanup(self):
            print("[MockGPIO] cleanup")

    GPIO = MockGPIO()

LIVING_ROOM_PIN = int(os.getenv("PIN_LIVING", 17))
KITCHEN_PIN     = int(os.getenv("PIN_KITCHEN", 27))
BUZZER_PIN      = int(os.getenv("PIN_BUZZER", 22))

app = Flask(__name__, static_folder='static', template_folder='templates')

state = {
    "livingroom": False,
    "kitchen": False,
    "buzz": False
}

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIVING_ROOM_PIN, GPIO.OUT)
GPIO.setup(KITCHEN_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.output(LIVING_ROOM_PIN, GPIO.LOW)
GPIO.output(KITCHEN_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

def set_device(pin, value):
    GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)


def buzzer_pulse(duration=0.35):
    def _pulse():
        try:
            state['buzz'] = True
            set_device(BUZZER_PIN, True)
            time.sleep(duration)
            set_device(BUZZER_PIN, False)
        finally:
            state['buzz'] = False

    t = threading.Thread(target=_pulse, daemon=True)
    t.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status', methods=['GET'])
def api_status():
    return jsonify({
        "livingroom": bool(state['livingroom']),
        "kitchen": bool(state['kitchen']),
        "buzz": bool(state['buzz'])
    })


@app.route('/livingroom/on', methods=['POST'])
def living_on():
    state['livingroom'] = True
    set_device(LIVING_ROOM_PIN, True)
    return jsonify({"device": "livingroom", "state": True, "message": "Living room ON"})


@app.route('/livingroom/off', methods=['POST'])
def living_off():
    state['livingroom'] = False
    set_device(LIVING_ROOM_PIN, False)
    return jsonify({"device": "livingroom", "state": False, "message": "Living room OFF"})


@app.route('/kitchen/on', methods=['POST'])
def kitchen_on():
    state['kitchen'] = True
    set_device(KITCHEN_PIN, True)
    return jsonify({"device": "kitchen", "state": True, "message": "Kitchen ON"})


@app.route('/kitchen/off', methods=['POST'])
def kitchen_off():
    state['kitchen'] = False
    set_device(KITCHEN_PIN, False)
    return jsonify({"device": "kitchen", "state": False, "message": "Kitchen OFF"})


@app.route('/alert', methods=['POST'])
def alert_buzzer():
    buzzer_pulse(duration=0.4)
    return jsonify({"buzz": True, "message": "Buzzer triggered"})

def cleanup_on_exit():
    try:
        GPIO.output(LIVING_ROOM_PIN, GPIO.LOW)
        GPIO.output(KITCHEN_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass


import atexit
atexit.register(cleanup_on_exit)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
