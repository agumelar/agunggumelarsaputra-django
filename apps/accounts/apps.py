from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Manajemen Akun & Otentikasi'

    def ready(self):
        from django.contrib import admin

        from .forms_admin import FormMasukAdmin

        admin.site.login_form = FormMasukAdmin
