# kiln-guardian

Safety-first Raspberry Pi kiln controller (fork scaffold of `kiln-controller`).

**Hardware target (your setup):**
- Raspberry Pi Zero W (works on other Pi models too — auto-detect at runtime)
- Single-phase SSR (GPIO-driven)
- Thermocouple: **K type** via **MAX31856** (SPI)
- Optional simulate mode (no hardware)

## Features in this scaffold
- Safe defaults + guardrails (over-temp, max rate-of-rise, sensor fault handling, optional stuck-SSR heuristic)
- Clean config via `.env` + validation (Pydantic)
- Simple PID loop using a windowed SSR control (cycle time) to avoid fast-chatter
- Flask web UI (read-only starter) and REST API for status; ready for future auth
- Systemd service for robust startup
- CI config (ruff + pytest + bandit) — optional
- Runs on Pi Zero W; also detects newer Pis

> ⚠️ **High voltage safety disclaimer**: This software controls equipment that can cause fire, property damage, or injury. Use at your own risk. Add independent hardware over-temperature protection where possible.

## Quick start
1. Enable SPI on the Pi: `sudo raspi-config` → Interface Options → SPI → Enable
2. Clone repo on the Pi and create `.env` from sample:
   ```bash
   cp .env.sample .env
   # set SSR pin, safety limits, etc.
   ```
3. Install deps (on Pi OS):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev
   pip3 install -r requirements.txt
   ```
4. Test in simulate mode first:
   ```bash
   SIMULATE=true python3 -m kiln_guardian.app
   ```
5. Install as a service:
   ```bash
   sudo cp scripts/kiln-guardian.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable kiln-guardian
   sudo systemctl start kiln-guardian
   ```

## Wiring (summary)
- **SSR control** from Pi GPIO (default `GPIO17`, BCM). SSR output must switch the kiln's heater circuit: **mains voltage – dangerous**. Use a qualified electrician.
- **MAX31856** on SPI0 (CE0): `CLK=GPIO11`, `MISO=GPIO9`, `MOSI=GPIO10`, `CS=GPIO8` (defaults).

## Config (.env)
See `.env.sample` for all options. Key ones:
- `SSR_GPIO_BCM=17`
- `MAX_TEMP_C=1250` (hard safety cap, software)
- `MAX_RATE_C_PER_MIN=200`
- `CYCLE_TIME_S=2.0` (good for SSRs, **do not** use mechanical relays)
- `SIMULATE=false`

## Roadmap (next PRs you can opt into)
- Editable firing profiles + state machine (Ramp/Soak UI)
- Basic auth
- Slack/webhook alerts
- Energy/kWh + cost estimates (AUD tariffs)
