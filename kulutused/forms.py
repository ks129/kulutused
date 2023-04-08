from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from django.forms import CharField, ModelForm, PasswordInput, TextInput

from kulutused.models import Debt


class UserLoginForm(AuthenticationForm):
    """Overwrite default AuthenticationForm to translate labels."""

    username = UsernameField(widget=TextInput(attrs={'autofocus': True}), label='Kasutajanimi')
    password = CharField(
        label="Parool",
        strip=False,
        widget=PasswordInput(attrs={'autocomplete': 'current-password'})
    )

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)


class DebtForm(ModelForm):
    """Translate Debt form fields."""

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(DebtForm, self).__init__(*args, **kwargs)
        self.fields['to_who'].label = 'Kellele võlgned?'
        self.fields['to_who'].label_from_instance = lambda obj: obj.get_full_name()
        self.fields['to_who'].queryset = User.objects.exclude(id=request.user.id)
        self.fields['amount'].label = 'Summa'
        self.fields['comments'].label = 'Kommentaar'

    class Meta:
        """Contains general information about DebtForm model."""

        model = Debt
        fields = ['to_who', 'amount', 'comments']
