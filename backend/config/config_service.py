import os
from dynaconf import Dynaconf
from decorators import service

@service
class ConfigService:
    def __init__(self):
        self.settings = None

    def init(self):
        if self.settings:
            return self.settings  # Prevent re-init

        # Default configuration
        default_config = {
            "pcap_directory": "/app/pcaps",
            "host_pcap_directory": "/app/pcaps",
            "redis_host": "localhost",
            "redis_port": 6379,
            "logging_level": "INFO",
            "backend": {
                "public_base_url": None,
                "allowed_origins": ["*"]
            }
        }

        # Get the absolute path to the config file relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, ".config", "config.yaml")

        settings = Dynaconf(
            envvar_prefix="PCAP",
            settings_files=[config_path],
            load_dotenv=True,
        )

        # Load defaults first
        for key, value in default_config.items():
            if isinstance(value, dict):
                # Handle nested dictionaries
                for nested_key, nested_value in value.items():
                    current_value = settings.get(f"{key}.{nested_key}")
                    if not current_value:
                        settings.set(f"{key}.{nested_key}", nested_value)
            else:
                # Handle simple values
                current_value = settings.get(key)
                if not current_value:
                    settings.set(key, value)

        # --- Set computed properties ---
        settings.PCAP_DIRECTORY = settings.get("pcap_directory")
        settings.HOST_PCAP_DIRECTORY = settings.get("host_pcap_directory")

        # --- Normalize FULL_BASE_URL ---
        base_url = settings.get("backend.public_base_url")
        if base_url:
            if not base_url.startswith(("http://", "https://")):
                base_url = f"http://{base_url}"
            settings.FULL_BASE_URL = base_url
        else:
            settings.FULL_BASE_URL = None

        # Lock in
        self.settings = settings
        return settings
