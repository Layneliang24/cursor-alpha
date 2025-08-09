from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False, initial=True)
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), required=False
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email") or ""
        user.first_name = self.cleaned_data.get("first_name") or ""
        user.last_name = self.cleaned_data.get("last_name") or ""
        user.is_active = self.cleaned_data.get("is_active", True)
        user.is_staff = self.cleaned_data.get("is_staff", False)
        user.is_superuser = self.cleaned_data.get("is_superuser", False)

        if commit:
            user.save()
            groups = self.cleaned_data.get("groups")
            if groups is not None:
                user.groups.set(groups)
        return user




