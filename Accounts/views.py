from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

class SignUpView(View):
    template_name = "registration/signup.html"

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        email = request.POST.get("email", "").strip()
        if form.is_valid() and email:
            user = form.save(commit=False)
            user.email = email
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse("activate", kwargs={"uidb64": uid, "token": token})
            )
            subject = "Aktivácia účtu - Receptár"
            message = render_to_string("registration/activation_email.txt", {"user": user, "activate_url": activate_url})
            send_mail(subject, message, None, [user.email])

            return render(request, "registration/activation_sent.html", {"email": user.email})

        if not email:
            messages.error(request, "E-mail je povinný pre registráciu.")
        return render(request, self.template_name, {"form": form})

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Účet bol úspešne aktivovaný. Môžete sa prihlásiť.")
            return redirect("login")

        return render(request, "registration/activation_invalid.html")