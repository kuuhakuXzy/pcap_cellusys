import logging
from config.config_service import ConfigService
from container import container

config_service = container.get(ConfigService)
settings = config_service.init()

def setup_logging(level=settings.logging_level if hasattr(settings, "logging_level") else logging.INFO):
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(name)s: %(message)s')