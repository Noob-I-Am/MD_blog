from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, nickname, email, password=None):
        if not email and not nickname :
            raise ValueError('昵称，邮箱，密码是必填项')
        user = self.model(email=self.normalize_email(email), nickname=nickname)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, nickname, email, password):
        user = self.create_user(email=email, nickname=nickname, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


def upload_to_user_path(instance, filename):
    return 'user/avatar/%s/%s' % ('user_'+str(instance.email), filename)


class User(AbstractBaseUser):

    # id = models.AutoField(primary_key=True)
    # email = models.CharField(max_length=50, unique=True, null=False, verbose_name='电子邮箱')
    email = models.EmailField(verbose_name='电子邮箱', unique=True, null=False)
    avatar = models.ImageField(upload_to=upload_to_user_path, null=True)
    nickname = models.CharField(max_length=10, blank=False, unique=True, verbose_name='昵称')
    profile = models.CharField(max_length=200, verbose_name='个人简介', blank=True, null=False)
    is_active = models.BooleanField(default=True, )
    is_admin = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        if not isinstance(value, bool):
            raise ValueError('score must be an bool value')
        self.is_admin = value

    @property
    def is_superuser(self):
        return self.is_admin

    @is_superuser.setter
    def is_superuser(self, value):
        if not isinstance(value, bool):
            raise ValueError('score must be an bool value')
        self.is_admin = value

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    REQUIRED_FIELDS = ['nickname', 'password']

    class Meta:
        db_table = 'user'


