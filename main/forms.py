from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    password_validators_help_texts,
    get_default_password_validators,
    validate_password
)
from django.core.exceptions import ValidationError
from .models import Song, Artist, Genre, Playlist, PlaylistSong

# Переопределяем стандартные сообщения валидации пароля
PASSWORD_VALIDATION_MESSAGES = {
    'password_too_short': 'Пароль слишком короткий. Он должен содержать минимум 8 символов.',
    'password_too_common': 'Этот пароль слишком распространен.',
    'password_entirely_numeric': 'Пароль не может состоять только из цифр.',
    'password_similar_to_username': 'Пароль слишком похож на имя пользователя.',
    'password_similar_to_email': 'Пароль слишком похож на email.',
    'password_similar_to_common': 'Пароль слишком похож на часто используемый пароль.',
    'password_similar_to_personal': 'Пароль слишком похож на вашу личную информацию.',
    'This password is too short. It must contain at least 8 characters.': 'Пароль слишком короткий. Он должен содержать минимум 8 символов.',
    'This password is too common.': 'Этот пароль слишком распространен.',
    'This password is entirely numeric.': 'Пароль не может состоять только из цифр.',
}

# Форма регистрации пользователя с дополнительной валидацией
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=30, min_length=3)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя',
            'maxlength': '30'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
        
        # текст подсказки для полей
        self.fields['username'].help_text = 'Обязательное поле. От 3 до 30 символов. Только буквы, цифры и @/./+/-/_'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Ваш пароль не должен быть слишком похож на другую вашу личную информацию.</li>
                <li>Ваш пароль должен содержать как минимум 8 символов.</li>
                <li>Ваш пароль не должен быть слишком простым.</li>
                <li>Ваш пароль не должен состоять только из цифр.</li>
            </ul>
        '''
        self.fields['password2'].help_text = 'Введите тот же пароль, что и выше, для проверки.'

        # текст ошибок для полей
        self.fields['username'].error_messages = {
            'required': 'Пожалуйста, введите имя пользователя.',
            'unique': 'Это имя пользователя уже занято.',
            'invalid': 'Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_',
            'max_length': 'Имя пользователя не должно превышать 30 символов.',
            'min_length': 'Имя пользователя должно содержать минимум 3 символа.'
        }
        self.fields['email'].error_messages = {
            'required': 'Пожалуйста, введите email.',
            'invalid': 'Пожалуйста, введите корректный email адрес.',
            'unique': 'Этот email уже зарегистрирован.'
        }
        self.fields['password1'].error_messages = {
            'required': 'Пожалуйста, введите пароль.',
            'password_too_short': PASSWORD_VALIDATION_MESSAGES['password_too_short'],
            'password_too_common': PASSWORD_VALIDATION_MESSAGES['password_too_common'],
            'password_entirely_numeric': PASSWORD_VALIDATION_MESSAGES['password_entirely_numeric'],
            'password_similar_to_username': PASSWORD_VALIDATION_MESSAGES['password_similar_to_username']
        }
        self.fields['password2'].error_messages = {
            'required': 'Пожалуйста, повторите пароль.',
            'password_mismatch': 'Пароли не совпадают.'
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('Имя пользователя должно содержать минимум 3 символа.')
        if len(username) > 30:
            raise forms.ValidationError('Имя пользователя не должно превышать 30 символов.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Это имя пользователя уже занято.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован.')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as error:
                # Заменяем стандартные сообщения на русские
                error_messages = []
                for message in error.messages:
                    if message in PASSWORD_VALIDATION_MESSAGES:
                        error_messages.append(PASSWORD_VALIDATION_MESSAGES[message])
                    else:
                        error_messages.append(message)
                raise forms.ValidationError(error_messages)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return password2

# Форма для создания/редактирования плейлиста
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '25',
                'placeholder': 'Введите название плейлиста'
            }),
        }
        error_messages = {
            'name': {
                'required': 'Пожалуйста, введите название плейлиста.',
                'max_length': 'Название плейлиста не должно превышать 25 символов.',
            }
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) > 25:
            raise forms.ValidationError('Название плейлиста не должно превышать 25 символов.')
        return name

# Форма для добавления песни в плейлист
class AddToPlaylistForm(forms.Form):
    def __init__(self, playlists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['playlist'] = forms.ChoiceField(
            choices=[(p.id, p.name) for p in playlists],
            widget=forms.RadioSelect,
            required=True
        )

# Форма для фильтрации по жанрам
class GenreFilterForm(forms.Form):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=''
    )

class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(
        max_length=30,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новое имя пользователя'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_username(self):
        new_username = self.cleaned_data.get('new_username')
        if len(new_username) < 3:
            raise forms.ValidationError('Имя пользователя должно содержать минимум 3 символа.')
        if len(new_username) > 30:
            raise forms.ValidationError('Имя пользователя не должно превышать 30 символов.')
        if User.objects.filter(username=new_username).exclude(id=self.user.id).exists():
            raise forms.ValidationError('Это имя пользователя уже занято.')
        return new_username

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Неверный текущий пароль.')
        return old_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            try:
                validate_password(new_password1, self.user)
            except ValidationError as error:
                error_messages = []
                for message in error.messages:
                    if message in PASSWORD_VALIDATION_MESSAGES:
                        error_messages.append(PASSWORD_VALIDATION_MESSAGES[message])
                    else:
                        error_messages.append(message)
                raise forms.ValidationError(error_messages)
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return new_password2 