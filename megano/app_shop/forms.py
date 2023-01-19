from django import forms

from app_shop.models import Review


# Форма добавления отзыва о товаре
class ReviewForm(forms.ModelForm):
	class Meta:
		model = Review
		fields = ['full_name', 'email', 'text']
		widgets = {
			'full_name': forms.TextInput(
				attrs={
					'class': 'form-input'
				}
			),
			'email': forms.TextInput(
				attrs={
					'class': 'form-input'
				}
			),
			'text': forms.Textarea(
				attrs={
					'class': 'form-textarea',
					'placeholder': 'Review'
				}
			)
		}
