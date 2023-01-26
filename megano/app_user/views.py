from typing import Any

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import View

from app_cart.models import Cart
from app_user.forms import SignUpForm, LoginForm, RestorePasswordForm, UserProfileUpdate, UserDataUpdate
from app_user.forms import ChangePasswordForm
from app_user.models import Profile


class SignUpView(View):
	"""
	Если пользователь уже вошел в систему, перенаправьте его на главную страницу. Если они не вошли в систему,
	отобразить страницу регистрации. Если форма действительна, создайте нового пользователя, войдите в систему и
	перенаправить его на домашнюю страницу. Если форма недействительна, снова отобразите страницу регистрации.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь уже вошел в систему, перенаправьте его на домашнюю страницу, в противном случае отобразите
		страницу регистрации.

		:param cls: Класс представления.
		:param request: Объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
		form_signup = SignUpForm()
		return render(
			request,
			'app_user/signup.html',
			context={
				'form_signup': form_signup,
				'next_url': next_url
			}
		)

	@classmethod
	def post(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь вошел в систему, перенаправить на домашнюю страницу. Если пользователь не вошел в систему,
		проверить, действительна ли форма. Если форма действительна, проверить, не используется ли уже адрес электронной
		почты или номер телефона. Если адрес электронной почты или номер телефона уже используются, добавить в форму
		сообщение об ошибке. Если адрес электронной почты и номер телефона не используются, создать нового
		пользователя, новый профиль и войти в систему пользователя. Если форма недействительна,
		отобразить страницу регистрации с формой.

		:param cls: Класс представления
		:param request: Объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		session_id = request.META.get('CSRF_COOKIE')
		form_signup = SignUpForm(request.POST)
		if form_signup.is_valid():
			email = form_signup.cleaned_data.get('email')
			password = form_signup.cleaned_data.get('password1')
			full_name = form_signup.cleaned_data.get('full_name')
			phone = form_signup.cleaned_data.get('phone')
			if User.objects.filter(email=email):
				form_signup.add_error('__all__', 'Пользователь с таким email уже существует!')
				return render(
					request,
					'app_user/signup.html',
					context={
						'form_signup': form_signup
					}
				)
			elif Profile.objects.filter(phone=phone):
				form_signup.add_error('__all__', 'Указанный номер принадлежит другому пользователю')
				return render(
					request,
					'app_user/signup.html',
					context={
						'form_signup': form_signup
					}
				)
			user = User.objects.create_user(username=email, email=email, password=password)
			User.groups.through.objects.create(user_id=user.id, group_id=2)
			Profile.objects.create(user=user, phone=phone, full_name=full_name)
			user_cart = Cart.objects.get(session=session_id)
			user_cart.user = user
			user_cart.session = user.id
			user_cart.save(update_fields=['user', 'session'])
			user = authenticate(username=email, password=password)
			login(request, user)
			if request.POST.get('next_url'):
				return HttpResponseRedirect(request.POST.get('next_url'))
			return HttpResponseRedirect('/')
		else:
			form_signup = SignUpForm()
			return render(
				request,
				'app_user/signup.html',
				context={
					'form_signup': form_signup
				}
			)


class LoginView(View):
	"""
	Если пользователь уже вошел в систему, перенаправить его на главную страницу.
	Если пользователь не вошел в систему, отобразить страницу входа.
	Если пользователь не вошел в систему и отправил форму входа,
	аутентифицировать пользователя и войти в систему.
	Если пользователь не вошел в систему и отправил форму входа,
	и форма недействительна, визуализировать страницу входа с ошибками формы.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь вошел в систему, перенаправить его на домашнюю страницу, в противном случае отобразить
		страницу входа.

		:param cls: Класс представления
		:param request: Объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
		form_login = LoginForm()
		return render(
			request,
			'app_user/login.html',
			context={
				'form_login': form_login,
				'next_url': next_url
			}
		)

	@classmethod
	def post(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь вошел в систему, перенаправить на домашнюю страницу. Если пользователь не вошел в систему,
		проверить действительна ли форма входа. Если форма входа действительна, аутентифицировать пользователя. Если
		пользователь аутентифицирован, войти в систему, удалить корзину сеанса и перенаправьте на следующую страницу.
		Если пользователь не аутентифицирован, добавить ошибку в форму входа и отобразить страницу входа. Если форма
		входа недействительна, визуализировать страницу входа.

		:param cls: Класс представления
		:param request: Объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		session_id = request.META.get('CSRF_COOKIE')
		session_cart = Cart.objects.get(session=session_id)
		form_login = LoginForm(request.POST)
		if form_login.is_valid():
			username = form_login.cleaned_data['username']
			password = form_login.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user:
				login(request, user)
				user_cart = user.user_cart
				if user_cart.products_in_carts.all() and request.POST.get('next_url') == '/order/':
					next_url = '/cart/'
				else:
					next_url = request.POST.get('next_url')
				if session_cart.products_in_carts.all():
					for product in session_cart.products_in_carts.all():
						if user_cart.products_in_carts.filter(product=product.product):
							product_in_cart = user_cart.products_in_carts.get(product=product.product)
							product_in_cart.quantity += product.quantity
							product_in_cart.save(update_fields=['quantity'])
							product.delete()
						else:
							product.cart = user_cart
							product.save(update_fields=['cart'])
				session_cart.delete()
				if next_url:
					return HttpResponseRedirect(next_url)
				return HttpResponseRedirect('/')
			else:
				form_login.add_error('__all__', 'Ошибка! Проверьте правильность ввода логина и пароля')
				return render(
					request,
					'app_user/login.html',
					context={
						'form_login': form_login
					}
				)
		else:
			form_login = LoginForm()
			return render(
				request,
				'app_user/login.html',
				context={
					'form_login': form_login
				}
			)


class RestorePasswordView(View):
	"""
	Представление принимает объект запроса, проверяет, вошел ли пользователь в систему, если нет.
	Проверяет, является ли запрос запросом GET или POST, если это запрос GET, он отображает шаблон restore_password.html
	с формой, если это POST запрос, проверяет, действительна ли форма, если да, то получает адрес электронной почты
	пользователя, генерирует новый пароль, устанавливает новый пароль, отправляет электронное письмо с новым паролем и
	отображает шаблон restore_password.html с формой и сообщение об успехе, если форма недействительна, отображает шаблон
	restore_password.html с формой и сообщением об ошибке.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь вошел в систему, перенаправить на домашнюю страницу, в противном случае отобразить форму
		восстановления пароля.

		:param cls: Класс представления
		:param request: Любой - объект запроса
		:type request: Any
		:return: визуализация страницы restore_password.html.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		next_url = request.META.get('HTTP_REFERER').split(request.META.get('HTTP_HOST'))[1]
		form_restore = RestorePasswordForm()
		return render(
			request,
			'app_user/restore_password.html',
			context={
				'form_restore': form_restore,
				'next_url': next_url
			}
		)

	@classmethod
	def post(cls, request: Any) -> HttpResponse:
		"""
		Если пользователь вошел в систему, перенаправить на домашнюю страницу.
		Если форма действительна, получить адрес электронной почты пользователя, сгенерировать новый пароль, получить
		пользователя, установить новый пароль, сохранить пользователя, отправить электронное письмо с новым паролем,
		добавить сообщение в форму и отобразить форму. Если форма недействительна, добавить ошибку в форму и отобразить
		форму.

		:param cls: Класс представления
		:param request: Текущий объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if request.user.id:
			return HttpResponseRedirect('/')
		form_restore = RestorePasswordForm(request.POST)
		if form_restore.is_valid():
			user_email = form_restore.cleaned_data['email']
			new_password = User.objects.make_random_password()
			current_user = User.objects.get(email=user_email)
			if current_user:
				current_user.set_password(new_password)
				current_user.save()
				send_mail(
					subject='Восстановление пароля',
					from_email='t.m.borovets@lenta.ru',
					message='Ваш новый пароль %s. Вы можете изменить его после входа в систему' % new_password,
					recipient_list=[form_restore.cleaned_data['email']],
					fail_silently=False
				)
				form_restore.add_error('__all__', 'Письмо с новым паролем было успешно отправлено')
				return render(
					request,
					'app_user/restore_password.html',
					context={
						'form_restore': form_restore
					}
				)
		form_restore.add_error('__all__', 'Пользователь не найден')
		return render(
			request,
			'app_user/restore_password.html',
			context={
				'form_restore': form_restore
			}
		)


# Представление для выхода пользователя из системы.
class LogoutUserView(LogoutView):
	next_page = '/'


class AccountView(View):
	"""
	Представления для отображения личного кабинета пользователя
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Метод отображает страницу учетной записи для пользователя.

		:param cls: Класс представления.
		:param request: Объект запроса является экземпляром HttpRequest. Он содержит всю информацию о текущем запросе.
		:type request: Any
		:return: ответ на запрос.
		"""
		if not request.user.id:
			return HttpResponseRedirect('/')
		user = request.user
		user_profile = user.user_profile
		order_list = user.user_orders.all()
		return render(
			request,
			'app_user/account.html',
			context={
				'user': user,
				'user_profile': user_profile,
				'order_list': order_list
			}
		)


class ProfileView(View):
	"""
	Представление для отображения страницы изменения личных данных пользователя.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Отрисовывает шаблон с кучей форм для редактирования персональных данных и профилем пользователя

		:param cls: Класс представления.
		:param request: Объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		if not request.user.id:
			return HttpResponseRedirect('/')
		user = request.user
		user_profile = user.user_profile
		form_edit_profile = UserProfileUpdate(instance=user_profile)
		form_edit_user = UserDataUpdate(instance=user)
		form_change_pass = ChangePasswordForm(user=user)
		return render(
			request,
			'app_user/profile.html',
			context={
				'form_edit_profile': form_edit_profile,
				'form_edit_user': form_edit_user,
				'form_change_pass': form_change_pass,
				'user_profile': user_profile,
				'user': user
			}
		)

	@classmethod
	def post(cls, request: Any) -> HttpResponse:
		"""
		Метод обрабатывает все три формы изменения персональных данных отдельно и в зависимости от заполнения

		:param cls: Класс представления
		:param request: Текущий объект запроса.
		:type request: Any
		:return: ответ на запрос.
		"""
		user = request.user
		user_profile = user.user_profile
		form_edit_profile = UserProfileUpdate(request.POST, request.FILES)
		form_edit_user = UserDataUpdate(request.POST)
		form_change_pass = ChangePasswordForm(request.POST)
		if form_edit_profile.is_valid():
			user_profile.full_name = form_edit_profile.cleaned_data['full_name']
			user_profile.phone = form_edit_profile.cleaned_data['phone']
			user_profile.save(update_fields=['full_name', 'phone'])
			if request.FILES:
				user_profile.user_photo = request.FILES['user_photo']
				user_profile.save(update_fields=['user_photo'])
		if form_edit_user.is_valid():
			user.username = form_edit_user.cleaned_data['email']
			user.email = form_edit_user.cleaned_data['email']
			user.save(update_fields=['username', 'email'])
		if form_change_pass.is_valid():
			user.set_password(raw_password=form_change_pass.new_password1)
		return render(
			request,
			'app_user/profile.html',
			context={
				'form_edit_profile': form_edit_profile,
				'form_edit_user': form_edit_user,
				'form_change_pass': form_change_pass,
				'user_profile': user_profile,
				'user': user,
				'ok_messages': 'Профиль успешно сохранен'
			}
		)


class HistoryOrderView(View):
	"""
	Представление принимает объект запроса, проверяет, вошел ли пользователь в систему, и если да, то отображает шаблон
	со списком заказов.
	"""

	@classmethod
	def get(cls, request: Any) -> HttpResponse:
		"""
		Метод используется для получения истории заказов пользователя.

		:param cls: Класс представления
		:param request: Объект запроса
		:type request: Any
		:return: Объект HttpResponse.
		"""
		if not request.user.id:
			return HttpResponseRedirect('/')
		user = request.user
		order_list = user.user_orders.all()
		return render(
			request,
			'app_user/historyorder.html',
			context={
				'user': user,
				'order_list': order_list
			}
		)
