from django.urls import path
from . import views
app_name = 'user'
urlpatterns = [
    path('signup_page/', views.signup_page),
    path('signup/', views.signup),
    path('login_page/', views.logon_page),
    path('login/', views.logon),
    path('logout/', views.logoff),
    path('activate_page/<int:user_pk>', views.activate_account),
    path('lost_password/<str:email>', views.lost_password),
    path('reset_passwd_page/', views.reset_passwd_page),
    path('is_email_exists/<str:email>', views.is_email_exists),
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    path('is_duplicate_nickname/<str:nickname>', views.is_duplicate_nickname),
    path('modify_user_page/', views.modify_user_page),
    path('modify_user_info/', views.modify_user_info)
]