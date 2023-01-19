from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from app_user.models import Profile

# Отменяем встроенную регистрацию модели User(AbstractUser)
admin.site.unregister(User)


class ProfileTabularInLine(admin.TabularInline):
	"""
	Класс ProfileTabularInLine создан для подключения к модифицированной версии UserAdmin и связанным управлением учетными
	данными
	"""
	model = Profile
	fields = ['full_name', 'phone']


@admin.register(User)
class MyUserAdmin(UserAdmin):
	"""
	Модификация UserAdmin, для административной панели оставляет для редактирования только логин и электронную почту.
	Также добавляется связанная модель Профиль для изменения связанных данных
	"""
	inlines = [ProfileTabularInLine]
	fieldsets = ((None, {'fields': ('username',)}), ('Персональная информация', {'fields': ('email',)}))

	def get_queryset(self, request: Any) -> Any:
		"""
		Даем возможность администратору управлять только собственными учетными данными.

		:param request: Объект запроса.
		:type request: Any
		:return: Набор запросов фильтруется по имени пользователя, вошедшего в систему.
		"""
		queryset = super().get_queryset(request)
		return queryset.filter(username=request.user.username)
