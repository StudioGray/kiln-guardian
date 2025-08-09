import time
from dataclasses import dataclass

@dataclass
class SafetyState:
    last_temp: float = 25.0
    last_time: float = time.time()
    abort_reason: str | None = None

class Safety:
    def __init__(self, max_temp_c: float, max_rate_c_per_min: float, stuck_ssr_detect: bool, window_s: int):
        self.max_temp = max_temp_c
        self.max_rate = max_rate_c_per_min
        self.stuck_detect = stuck_ssr_detect
        self.window_s = window_s
        self.state = SafetyState()
        self._off_since = None

    def check(self, temp_c: float, heat_cmd: float) -> tuple[bool, str | None]:
        now = time.time()
        dt = max(1e-6, now - self.state.last_time)
        dC = temp_c - self.state.last_temp
        rate = (dC / dt) * 60.0

        # Hard over-temp
        if temp_c >= self.max_temp:
            return False, f"Over-temperature: {temp_c:.1f}C >= {self.max_temp:.1f}C"

        # Rate-of-rise limit (only if heating)
        if heat_cmd > 0.1 and rate > self.max_rate:
            return False, f"Rate-of-rise too high: {rate:.1f}C/min > {self.max_rate:.1f}"

        # Stuck-SSR heuristic: if command ~0 for window and temperature still rising steadily
        if self.stuck_detect:
            if heat_cmd < 0.05:
                if self._off_since is None:
                    self._off_since = now
                elif (now - self._off_since) >= self.window_s and dC > 1.0:
                    return False, "Heater may be stuck ON (temp rising while output is OFF)"
            else:
                self._off_since = None

        self.state.last_temp = temp_c
        self.state.last_time = now
        return True, None
