from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .admin import UserCreationForm
from user.models import User

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .token import account_activation_token
from django.core.mail import EmailMessage
# Create your views here.


def signup_page(request):
    return render(request, 'user/signup.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = User.objects.get(email=form.cleaned_data.get('email'))
            user.is_active = False
            user.save()
            return redirect('/user/activate_page/'+str(user.pk))
        return HttpResponseBadRequest('注册信息无效')


def logon_page(request):
    return render(request, 'user/login.html')


def logon(request):
    username = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            auth = request.user.is_authenticated
            # return HttpResponseRedirect('/app/blog/base/')
            return HttpResponse('/index/')
        else:
            return HttpResponse('/user/activate_page/'+str(user.pk))
    else:
        return HttpResponseBadRequest('登录失败')


def logoff(request):
    auth = request.user.is_authenticated
    logout(request)
    # return JsonResponse({'result': 'logging out succeed'})
    return render(request, 'user/login.html')


# @login_required(login_url='/app/blog/base/')
@login_required
def doing(request):
    isauth = request.user.is_authenticated
    print('doing sth : ', isauth)
    return JsonResponse({'auth': isauth})



# Create your views here.
def  show(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['565223635@qq.com', ]
    send_mail(subject, message, email_from, recipient_list)
    return HttpResponse('已发送成功')


def activate_account(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    if user.is_active:
        return HttpResponseBadRequest('已完成用户验证')
    current_site = get_current_site(request)
    subject = '感谢注册MDblog站点，请激活您的账号'
    message = render_to_string('activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user_pk)),
        'token': account_activation_token.make_token(user)
    })
    email = EmailMessage(
        subject, message, to=[user.email]
    )
    email.send()
    if request.method == 'GET':
        return render(request, 'user/user_activation.html', {'user': user})
    if request.method == 'POST':
        return HttpResponse('success')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'showmsg.html', {'message': '激活成功', 'jump': '/index/'})
    else:
        return render(request, 'showmsg.html', {'message': '激活链接无效', 'jump': '/index/'})


def is_email_exists(request, email):
    try:
        user = User.objects.get(email=email)
        return HttpResponse('True')
    except User.DoesNotExist as e:
        return HttpResponse('False')


def reset_passwd_page(request):
    return render(request,'user/reset_passwd.html')


def lost_password(request, email):
    user = get_object_or_404(User, email=email)
    passwd = User.objects.make_random_password()
    user.set_password(passwd)
    user.save()
    message = '你的账号密码已重置为: '+passwd+' \n请进入资料修改页面修改密码'
    subject = 'MDBlog账号密码重置'
    email = EmailMessage(
        subject, message, to=[user.email]
    )
    email.send()
    return render(request, 'showmsg.html', {'message':'你的账号密码已更新，含有新密码的邮件已发送至你的邮箱，请查收', 'jump': '/user/login_page/'})


def is_duplicate_nickname(request, nickname):
    count = User.objects.filter(nickname__exact=nickname).count()
    if count > 0:
        return HttpResponse('True')
    else:
        return HttpResponse('False')


def modify_user_page(request):
    user = request.user
    return render(request, 'user/modify_user.html', {'user': user})


def modify_user_info(request):
    user = request.user
    nickname = request.POST.get('nickname')
    if nickname:
        user.nickname = nickname
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    if password1:
        if password1 == password2:
            user.set_password(password1)
        else:
            return HttpResponseBadRequest('两次密码不一致')
    profile = request.POST.get('profile')
    if profile:
        user.profile = profile

    user.save()
    return HttpResponse('修改完成')
