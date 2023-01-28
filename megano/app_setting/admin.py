import json
import os
from typing import Any

from django.conf import settings
from django.contrib import admin

from app_setting.models import Settings


@admin.register(Settings)
# SettingsAdmin определяет интерфейс администратора для модели Settings.
class SettingsAdmin(admin.ModelAdmin):
	list_display = ['title']

	def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
		settings_file = os.path.join(settings.BASE_DIR, 'site_settings.json')
		data = {
			'ALLOWED_HOSTS': obj.ALLOWED_HOSTS,
			'SERVER_EMAIL': obj.SERVER_EMAIL,
			'EMAIL_USE_TLS': obj.EMAIL_USE_TLS,
			'EMAIL_HOST': obj.EMAIL_HOST,
			'EMAIL_PORT': obj.EMAIL_PORT,
			'EMAIL_HOST_USER': obj.EMAIL_HOST_USER,
			'EMAIL_HOST_PASSWORD': obj.EMAIL_HOST_PASSWORD
		}
		with open(settings_file, 'w') as file:
			json.dump(data, file, indent=4)
		super().save_model(request, obj, form, change)
