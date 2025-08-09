from typing import Optional, Tuple
import time

class Thermocouple:
    def read_celsius(self) -> float:
        raise NotImplementedError()
    def healthy(self) -> bool:
        return True
    def last_fault(self) -> Optional[str]:
        return None

class SimulatedTC(Thermocouple):
    def __init__(self):
        self.t = 25.0
        self._fault = None
    def read_celsius(self) -> float:
        # Basic slow drift to emulate heat
        self.t = min(self.t + 0.2, 1200.0)
        return self.t
    def healthy(self) -> bool:
        return self._fault is None

def make_thermocouple(chip: str, tc_type: str, spi_bus: int, spi_device: int, simulate: bool) -> Thermocouple:
    if simulate or chip.upper() == "SIMULATED":
        return SimulatedTC()
    if chip.upper() == "MAX31856":
        try:
            import board, busio
            import digitalio
            import adafruit_max31856
            # SPI wiring via /dev/spidev{bus}.{device}
            spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(getattr(board, f"CE{spi_device}"))
            sensor = adafruit_max31856.MAX31856(spi, cs, thermocouple_type=getattr(adafruit_max31856, f"TC_TYPE_{tc_type.upper()}"))
            class _Max31856TC(Thermocouple):
                def __init__(self, s): self.s = s
                def read_celsius(self) -> float:
                    return float(self.s.temperature)
                def healthy(self) -> bool:
                    return True  # library raises on fault
            return _Max31856TC(sensor)
        except Exception as e:
            # Fallback to simulated with fault note
            tc = SimulatedTC()
            tc._fault = f"MAX31856 init failed: {e}"
            return tc
    # Default fallback
    return SimulatedTC()
