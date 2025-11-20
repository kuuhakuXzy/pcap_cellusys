import os
from dynaconf import Dynaconf

class ConfigService:
    settings = None

    @staticmethod
    def init():
        if ConfigService.settings:
            return ConfigService.settings  # Prevent re-init

        # Get the absolute path to the config file relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, ".config", "config.yaml")

        settings = Dynaconf(
            envvar_prefix="PCAP",
            settings_files=[config_path],
            load_dotenv=True,
        )

        # --- Normalize PCAP_DIRECTORIES ---
        dirs = settings.get("pcap_mounted_directory", "pcaps")
        if isinstance(dirs, str):
            settings.PCAP_DIRECTORIES = [d.strip() for d in dirs.split(",")]
        else:
            settings.PCAP_DIRECTORIES = dirs

        # --- Normalize FULL_BASE_URL ---
        base_url = settings.get("backend.base_url")
        base_port = settings.get("backend.base_port")

        if base_url:
            if not base_url.startswith(("http://", "https://")):
                base_url = f"http://{base_url}"
            settings.FULL_BASE_URL = (
                f"{base_url}:{base_port}" if base_port else base_url
            )
        else:
            settings.FULL_BASE_URL = None

        # Lock in
        ConfigService.settings = settings
        return settings
