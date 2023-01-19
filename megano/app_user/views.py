from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from app_cart.models import Cart
from app_user.forms import SignUpForm, LoginForm, RestorePasswordForm, UserProfileUpdate, UserDataUpdate
from app_user.forms import ChangePasswordForm
from app_user.models import Profile


class SignUpView(View):

	@classmethod
	def get(cls, request):
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
	def post(cls, request):
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

	@classmethod
	def get(cls, request):
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
	def post(cls, request):
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
				if user_cart.goods_in_carts.all() and request.POST.get('next_url') == '/order/':
					next_url = '/cart/'
				else:
					next_url = request.POST.get('next_url')
				if session_cart.goods_in_carts.all():
					for good in session_cart.goods_in_carts.all():
						if user_cart.goods_in_carts.filter(good=good.good):
							good_in_cart = user_cart.goods_in_carts.get(good=good.good)
							good_in_cart.quantity += good.quantity
							good_in_cart.save(update_fields=['quantity'])
							good.delete()
						else:
							good.cart = user_cart
							good.save(update_fields=['cart'])
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

	@classmethod
	def get(cls, request):
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
	def post(cls, request):
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


class LogoutUserView(LogoutView):
	next_page = '/'


class AccountView(View):

	@classmethod
	def get(cls, request):
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

	@classmethod
	def get(cls, request):
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
	def post(cls, request):
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

	@classmethod
	def get(cls, request):
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
