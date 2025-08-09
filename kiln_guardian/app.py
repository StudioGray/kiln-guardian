import threading, time, os
from flask import Flask, jsonify, request
from dotenv import load_dotenv

from .config import settings
from .hw.thermocouple import make_thermocouple
from .hw.ssr import make_ssr, WindowedSSRController
from .control.pid import make_pid
from .safety import Safety

load_dotenv(settings.Config.env_file)

app = Flask(__name__)

state = {
    "setpoint_c": 100.0,
    "temp_c": 25.0,
    "duty": 0.0,
    "healthy": True,
    "abort": None,
}

def control_thread():
    tc = make_thermocouple(settings.tc.chip, settings.tc.type, settings.tc.spi_bus, settings.tc.spi_device, settings.simulate)
    ssr_drv = make_ssr(settings.ssr.gpio_bcm, settings.simulate)
    ssr = WindowedSSRController(ssr_drv, settings.ssr.cycle_time_s)
    pid = make_pid(settings.pid.p_gain, settings.pid.i_gain, settings.pid.d_gain, state["setpoint_c"])
    safety = Safety(settings.safety.max_temp_c, settings.safety.max_rate_c_per_min, settings.safety.stuck_ssr_detect, settings.safety.stuck_ssr_check_window_s)

    while True:
        try:
            t = tc.read_celsius()
            state["temp_c"] = float(t)
            state["healthy"] = bool(tc.healthy())
        except Exception as e:
            state["healthy"] = False
            state["abort"] = f"Sensor error: {e}"

        if not state["healthy"] and settings.safety.abort_on_sensor_fault:
            ssr.apply_output(0.0)
            time.sleep(0.5)
            continue

        duty = pid(state["temp_c"])
        ok, reason = safety.check(state["temp_c"], duty)
        if not ok:
            state["abort"] = reason
            duty = 0.0
        else:
            state["abort"] = None

        state["duty"] = float(duty)
        ssr.apply_output(duty)
        time.sleep(0.25)

@app.route("/api/status")
def api_status():
    return jsonify(state | {
        "config": {
            "max_temp_c": settings.safety.max_temp_c,
            "max_rate_c_per_min": settings.safety.max_rate_c_per_min,
            "cycle_time_s": settings.ssr.cycle_time_s,
            "simulate": settings.simulate,
        }
    })

@app.route("/api/setpoint", methods=["POST"])
def api_setpoint():
    data = request.get_json(force=True)
    sp = float(data.get("setpoint_c", state["setpoint_c"]))
    state["setpoint_c"] = sp
    return jsonify({"ok": True, "setpoint_c": sp})

def run():
    t = threading.Thread(target=control_thread, daemon=True)
    t.start()
    app.run(host=settings.web.host, port=settings.web.port)

if __name__ == "__main__":
    run()
