import os
import json
import urllib.request
from typing import Optional

class DiscordAlerter:
    def __init__(self, webhook_url: Optional[str] = None, enabled: bool = True):
        self.url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.enabled = enabled and bool(self.url)

    def send(self, content: str, username: str = "Kiln Guardian", **embeds):
        if not self.enabled:
            return False
        data = {"content": content, "username": username}
        if embeds:
            data["embeds"] = [embeds]
        req = urllib.request.Request(
            self.url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
            return True
        except Exception:
            return False

def make_alerter(webhook_url: Optional[str], enabled: bool) -> DiscordAlerter:
    return DiscordAlerter(webhook_url=webhook_url, enabled=enabled)
