from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import SignupForm
from django import forms


class CustomLoginForm(AllauthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs["placeholder"] = "Email or Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"


class CustomSignupForm(SignupForm):
    full_name = forms.CharField(
        max_length=150,
        required=False,
        label="Full Name",
        widget=forms.TextInput(attrs={"placeholder": "Full Name", "autocomplete": "name"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = "Email Address"
        if "username" in self.fields:
            self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"

    def save(self, request):
        user = super().save(request)
        name = (self.cleaned_data.get("full_name") or "").strip()
        if name:
            parts = name.split(None, 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
            user.save(update_fields=["first_name", "last_name"])
        return user
