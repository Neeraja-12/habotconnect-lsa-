from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "HabotConnect API"

    def ready(self):
        self.run_startup_checks()

    def run_startup_checks(self):
        import logging
        from django.conf import settings

        logger = logging.getLogger(__name__)

        if not hasattr(settings, 'PAYMENT_GATEWAY_KEY'):
            logger.warning(
                "PAYMENT_GATEWAY_KEY not set in settings. "
                "Payment features may not work."
            )

        if not settings.EMAIL_HOST_USER:
            logger.info(
                "Email not configured. Email notifications will be disabled."
            )

        logger.info("HabotConnect API app initialized successfully.")