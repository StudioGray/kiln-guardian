from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import os

class SafetyConfig(BaseModel):
    max_temp_c: float = Field(1250, ge=100, description="Absolute temperature cap")
    max_rate_c_per_min: float = Field(200, ge=1, description="Max allowed climb rate")
    abort_on_sensor_fault: bool = True
    stuck_ssr_detect: bool = True
    stuck_ssr_check_window_s: int = 60

class PIDConfig(BaseModel):
    p_gain: float = 10.0
    i_gain: float = 0.5
    d_gain: float = 0.0

class WebConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    basic_auth_enabled: bool = False
    basic_auth_user: str = "admin"
    basic_auth_pass: str = "change_me"

class TCConfig(BaseModel):
    chip: str = "MAX31856"  # or SIMULATED
    type: str = "K"
    spi_bus: int = 0
    spi_device: int = 0

class SSRConfig(BaseModel):
    gpio_bcm: int = 17
    cycle_time_s: float = 2.0

class AppSettings(BaseSettings):
    # Hardware / mode
    pi_model: str = "auto"
    simulate: bool = False

    # Thermocouple
    tc: TCConfig = TCConfig()

    # SSR
    ssr: SSRConfig = SSRConfig()

    # Safety
    safety: SafetyConfig = SafetyConfig()

    # PID
    pid: PIDConfig = PIDConfig()

    # Web
    web: WebConfig = WebConfig()

    class Config:
        env_prefix = ""
        env_nested_delimiter = "__"
        env_file = os.getenv("ENV_FILE", ".env")

settings = AppSettings()
