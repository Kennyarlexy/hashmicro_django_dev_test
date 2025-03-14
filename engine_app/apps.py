import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)

class EngineAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine_app'

    def ready(self):
        """Dynamically load user-installed apps from the database after Django initializes."""
        try:
            from engine_app.models import InstalledModule
            from django.db import connections

            db_conn = connections["default"]
            db_conn.ensure_connection()

            user_installed_module_apps = [module.name for module in InstalledModule.objects.all()]

            settings.INSTALLED_APPS += user_installed_module_apps

            logger.info(f"Loaded user-installed apps: {user_installed_module_apps}")

        except Exception as e:
            logger.warning(f"Could not load user-installed apps. Reason: {e}")
            