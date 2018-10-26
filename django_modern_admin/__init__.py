# ACTION_CHECKBOX_NAME is unused, but should stay since its import from here
# has been referenced in documentation.
from django_modern_admin.sites import site
from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules('admin', register_to=site)


default_app_config = 'django_modern_admin.apps.AdminConfig'
