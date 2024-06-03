from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView





from .models import MyUser
from .form import CustomUserCreationForm

class UserCreateView(CreateView):
    model = MyUser
    form_class = CustomUserCreationForm
    template_name='registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
