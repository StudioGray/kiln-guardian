from simple_pid import PID

def make_pid(p: float, i: float, d: float, setpoint: float):
    pid = PID(p, i, d, setpoint=setpoint)
    pid.output_limits = (0.0, 1.0)  # duty cycle
    return pid
