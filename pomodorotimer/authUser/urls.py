from django.urls import path, include
from authUser.views import MyLoginView, MyUserCreationView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('signup/', MyUserCreationView.as_view(), name='signup'),
]
