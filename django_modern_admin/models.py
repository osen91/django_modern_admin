from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _, gettext_lazy


class AdminProfile(models.Model):
    user = models.OneToOneField(to=User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='userAvatars', null=True, blank=True)
    phoneNumber = models.CharField(max_length=18, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = _("Admin Profile")
        verbose_name_plural = _("Admin Profile")


@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff is True:
        AdminProfile.objects.create(user=instance)


class AdminNavLogo(models.Model):
    logo = models.ImageField(upload_to='AdminNavLogo')

    def logo_img(self):
        return '<img style="width:200px;" src="%s"/>' % self.logo.url
    logo_img.allow_tags = True

    class Meta:
        verbose_name = _("Admin Logo")
        verbose_name_plural = _("Admin Logo")


class AdminLoginLogo(models.Model):
    logo = models.ImageField(upload_to='AdminLoginLogo')

    def logo_img(self):
        return '<img style="width:200px;" src="%s"/>' % self.logo.url
    logo_img.allow_tags = True

    class Meta:
        verbose_name = _("Admin Login Logo")
        verbose_name_plural = _("Admin Login Logo")


class AdminTasks(models.Model):
    user = models.ForeignKey(to=User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    date = models.DateField()
    isDone = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Admin Task")
        verbose_name_plural = _("Admin Tasks")