from django.urls import path
from django.conf.urls import include

from django.contrib import admin
from django.contrib.auth import views as authViews
from django.urls import path, include
from users import views as userViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('designthinking.urls')),
    path('', authViews.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', authViews.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('reset/', authViews.PasswordResetView.as_view(template_name='users/forgot-password.html'), name='forgot'),
    path('reset/done', authViews.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/confirm/<uidb64>/<token>/',
         authViews.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/complete',
         authViews.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('register/', userViews.register, name='register'),
]
    
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
