# File encoding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.forms.extras.widgets import SelectDateWidget
import accounts.models as models
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

fio_regexp = r'(?u)\w+(-\w+)?'
generic_error = {"invalid": "Неправильно введены данные"}

class UserForm(forms.ModelForm):
    email = forms.EmailField(label='Контактный E-mail', max_length=50)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(render_value=False), max_length=30, min_length=5)
    password_confirm = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(render_value=False), max_length=30, min_length=5)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).count() > 0:
           # raise forms.ValidationError('Пользователь с таким адресом уже существует')
		   raise forms.ValidationError('Неправильно введены данные')
        return email

    def clean_password_confirm(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            # raise forms.ValidationError('Пароль и подтверждение не совпадают')
			raise forms.ValidationError('Неправильно введены данные')
        return password_confirm


class JurCustomerRegForm(UserForm):
    type = forms.CharField(widget=forms.HiddenInput, initial='j')
    repr_surname = forms.RegexField(label="Фамилия заказчика", max_length=80, regex=fio_regexp, error_messages=generic_error)
    repr_first_name = forms.RegexField(label="Имя заказчика", max_length=30, regex=fio_regexp, error_messages=generic_error)
    repr_second_name = forms.RegexField(label="Отчество заказчика", max_length=50, required=False, regex=fio_regexp, error_messages=generic_error)
    pay_type = forms.ModelMultipleChoiceField(label="Способ оплаты", queryset=models.PayingType.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = models.JurCustomer
        exclude = ['customer']
        fields = ['type', 'email', 'password', 'password_confirm'] + [f.name for f in models.JurCustomer._meta.fields[2:]] + [f.name for f in models.JurCustomer._meta.many_to_many]

    def save(self, *args, **kwargs):
        assert(self.is_valid())
        # Вызов оригинального save
        data = self.cleaned_data
        jurcustomer = super(JurCustomerRegForm, self).save(*args, **kwargs)
        user = jurcustomer.customer.user
        user.set_password(data['password'])
        user.save()
        return jurcustomer


class PhysCustomerRegForm(UserForm):
    type = forms.CharField(widget=forms.HiddenInput, initial='p')
    surname = forms.RegexField(label="Фамилия заказчика", max_length=80, regex=fio_regexp, error_messages=generic_error)
    first_name = forms.RegexField(label="Имя заказчика", max_length=30, regex=fio_regexp, error_messages=generic_error)
    second_name = forms.RegexField(label="Отчество заказчика", max_length=50, required=False, regex=fio_regexp, error_messages=generic_error)
    pay_type = forms.ModelMultipleChoiceField(label="Способ оплаты", queryset=models.PayingType.objects.all(), widget=forms.CheckboxSelectMultiple)
    passport_when = forms.DateField(label="Дата выдачи", widget=SelectDateWidget(years=range(2010, 1900, -1)))

    class Meta:
        model = models.PhysCustomer
        exclude = ['customer']
        fields = ['type', 'email', 'password', 'password_confirm'] + [f.name for f in models.PhysCustomer._meta.fields[2:]] + [f.name for f in models.PhysCustomer._meta.many_to_many]

    def save(self, *args, **kwargs):
        assert(self.is_valid())
        # Вызов оригинального save
        data = self.cleaned_data
        physcustomer = super(PhysCustomerRegForm, self).save(*args, **kwargs)
        user = physcustomer.customer.user
        user.set_password(data['password'])
        user.save()
        return physcustomer


class TesterRegForm(UserForm):
    surname = forms.RegexField(label="Фамилия", max_length=80, regex=fio_regexp, error_messages=generic_error)
    first_name = forms.RegexField(label="Имя", max_length=30, regex=fio_regexp, error_messages=generic_error)
    second_name = forms.RegexField(label="Отчество", max_length=30, required=False, regex=fio_regexp, error_messages=generic_error)
    description = forms.CharField(label="О себе", widget=forms.Textarea, required=False, max_length=300)
    os = forms.ModelMultipleChoiceField(label="Операционные системы", queryset=models.OSystem.objects.all(), widget=FilteredSelectMultiple(u'ОС', False))
    program_languages = forms.ModelMultipleChoiceField(label="Языки программирования", queryset=models.ProgramLang.objects.all(), widget=FilteredSelectMultiple(u'языки', False))
    testing_types = forms.ModelMultipleChoiceField(label="Типы тестирования", queryset=models.TestingType.objects.all(), widget=FilteredSelectMultiple(u'типы', False))
    browsers = forms.ModelMultipleChoiceField(label="Браузеры", queryset=models.Browser.objects.all(), widget=FilteredSelectMultiple(u'браузеры', False))

    class Meta:
        model = models.Tester
        fields = ['email', 'password', 'password_confirm', 'osystems', 'program_languages', 'testing_types', 'browsers', 'description']
    
    def save(self, *args, **kwargs):
        assert(self.is_valid())
        # Вызов оригинального save
        data = self.cleaned_data
        tester = super(TesterRegForm, self).save(*args, **kwargs)
        user = tester.user
        user.set_password(data['password'])
        user.save()
        return tester


class TesterChangeForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(render_value=False), max_length=30, min_length=5)
    password_confirm = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(render_value=False), max_length=30, min_length=5)
    osystems = forms.ModelMultipleChoiceField(label="Операционные системы", queryset=models.OSystem.objects.all())
    program_languages = forms.ModelMultipleChoiceField(label="Языки программирования", queryset=models.ProgramLang.objects.all())
    testing_types = forms.ModelMultipleChoiceField(label="Типы тестирования", queryset=models.TestingType.objects.all())
    browsers = forms.ModelMultipleChoiceField(label="Браузеры", queryset=models.Browser.objects.all())
    description = forms.CharField(label="О себе", widget=forms.Textarea, required=False, max_length=300)

    class Meta:
        model = models.Tester
        fields = ['password', 'password_confirm', 'osystems', 'program_languages', 'testing_types', 'browsers', 'description']

    def save(self, *args, **kwargs):
        """Обновление тестера с учетом смены пароля"""
        assert(self.is_valid())
        # Вызов оригинального save
        data = self.cleaned_data
        tester = super(TesterChangeForm, self).save(*args, **kwargs)
        # Проверка на смену пароля
        if data['password']:
            # Пароль изменился
            user = tester.user
            user.set_password(data['password'])
            user.save()
        return tester

    def clean(self):
        # Вызов оригинального clean()
        data = super(TesterChangeForm, self).clean()
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        if password != password_confirm:
            # raise forms.ValidationError('Пароль и подтверждение не совпадают')
			raise forms.ValidationError('Неправильно введены данные')
        return data