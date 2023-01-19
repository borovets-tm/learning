from django.urls import path

from app_user.views import SignUpView, LoginView, RestorePasswordView, LogoutUserView, AccountView, ProfileView
from app_user.views import HistoryOrderView


urlpatterns = [
	# Это путь к странице личного кабинета.
	path('', AccountView.as_view(), name='account'),
	# Это путь к странице регистрации.
	path('signup/', SignUpView.as_view(), name='signup'),
	# Путь к странице входа в учетную запись.
	path('login/', LoginView.as_view(), name='login'),
	# Это путь к странице для восстановления пароля.
	path('restore_password/', RestorePasswordView.as_view(), name='restore_password'),
	# Путь к странице выхода из учетной записи.
	path('logout/', LogoutUserView.as_view(), name='logout'),
	# Путь к странице изменения личных данных.
	path('profile/', ProfileView.as_view(), name='profile'),
	# Путь к странице истории заказов.
	path('historyorder/', HistoryOrderView.as_view(), name='history_order'),
]
