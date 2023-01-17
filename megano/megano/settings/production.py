from .base import *
from app_shop.models import Settings

current_settings = Settings.objects.first()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', current_settings.ALLOWED_HOSTS]

# настройки для работы службы восстановления пароля
SERVER_EMAIL = current_settings.SERVER_EMAIL
EMAIL_USE_TLS = current_settings.EMAIL_USE_TLS
EMAIL_HOST = current_settings.EMAIL_HOST
EMAIL_PORT = current_settings.EMAIL_PORT
EMAIL_HOST_USER = current_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = current_settings.EMAIL_HOST_PASSWORD
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
