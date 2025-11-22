import subprocess
import logging
import json
import re
import asyncio
from decorators import service

@service
class PcapParser:
    def parse_pcap_sync(self, path):
        cmd = ["tshark", "-r", path, "-q", "-z", "io,phs"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            output = res.stdout.strip()
            err = res.stderr.strip()

            if "cut short" in err:
                logging.warning(f"Truncated file: {path}")

            if not output:
                return {}

            stats = {}
            table_open = False

            for line in output.splitlines():
                if "Protocol Hierarchy Statistics" in line:
                    table_open = True
                    continue

                if not table_open or not line.strip() or line.startswith("="):
                    continue

                match = re.search(r"(\S+).*frames:(\d+)", line)
                if match:
                    stats[match.group(1)] = int(match.group(2))

            return stats
        except Exception as e:
            logging.error(f"tshark failed: {e}")
            return None

    async def parse_pcap(self, path):
        return await asyncio.to_thread(self.parse_pcap_sync, path)
