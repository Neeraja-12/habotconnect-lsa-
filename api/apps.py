from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "HabotConnect API"
    
    
    def ready(self):
        """
        Perform initialization tasks when Django starts.
        This runs automatically when the app is loaded.
        """
        # Import signals (if you have signals.py)
        # import api.signals
        
        # Import management commands (if any)
        # from api import management
        
        # Run startup checks
        self.run_startup_checks()
    
    def run_startup_checks(self):
        """
        Perform application startup checks.
        Logs warnings for critical configuration issues.
        """
        import logging
        from django.conf import settings
        
        logger = logging.getLogger(__name__)
        
        # Check if payment gateway is configured (if using payments)
        if not hasattr(settings, 'PAYMENT_GATEWAY_KEY'):
            logger.warning(
                "PAYMENT_GATEWAY_KEY not set in settings. "
                "Payment features may not work."
            )
        
        # Check for email configuration (if sending emails)
        if not settings.EMAIL_HOST_USER:
            logger.info(
                "Email not configured. Email notifications will be disabled."
            )
        
        logger.info("HabotConnect API app initialized successfully.")
