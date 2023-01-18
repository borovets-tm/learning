from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', 'app_shop.context_processor.get_allowed_hosts']

# настройки для работы службы восстановления пароля
SERVER_EMAIL = 'app_shop.context_processor.get_server_email'
EMAIL_USE_TLS = 'app_shop.context_processor.get_email_use_tls'
EMAIL_HOST = 'app_shop.context_processor.get_email_host'
EMAIL_PORT = 'app_shop.context_processor.get_email_port'
EMAIL_HOST_USER = 'app_shop.context_processor.get_email_host_user'
EMAIL_HOST_PASSWORD = 'app_shop.context_processor.get_email_host_password'
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
