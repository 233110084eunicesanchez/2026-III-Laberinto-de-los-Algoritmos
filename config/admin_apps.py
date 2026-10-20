from django.contrib.admin.apps import AdminConfig

class LabAdminConfig(AdminConfig):
    default_site = 'core.admin_site.LabAdminSite'
