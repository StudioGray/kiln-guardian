import time
from typing import Optional

class SSRDriver:
    def set_power(self, on: bool):
        raise NotImplementedError()

class SimulatedSSR(SSRDriver):
    def __init__(self): self.state=False
    def set_power(self, on: bool):
        self.state = on

def make_ssr(gpio_bcm: int, simulate: bool) -> SSRDriver:
    if simulate:
        return SimulatedSSR()
    try:
        from gpiozero import OutputDevice
        class _GPIOZeroSSR(SSRDriver):
            def __init__(self, pin: int):
                self.relay = OutputDevice(pin, active_high=True, initial_value=False)
            def set_power(self, on: bool):
                if on: self.relay.on()
                else: self.relay.off()
        return _GPIOZeroSSR(gpio_bcm)
    except Exception:
        return SimulatedSSR()

class WindowedSSRController:
    """Time-proportioning control with a fixed cycle time (s)."""
    def __init__(self, driver: SSRDriver, cycle_time_s: float):
        self.drv = driver
        self.cycle = max(1.0, float(cycle_time_s))
        self._last_window_start = time.time()

    def apply_output(self, duty_0_to_1: float):
        duty = min(max(duty_0_to_1, 0.0), 1.0)
        now = time.time()
        if now - self._last_window_start >= self.cycle:
            self._last_window_start = now
        on_time = self._last_window_start + duty * self.cycle
        self.drv.set_power(now < on_time)
