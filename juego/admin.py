from django.contrib import admin
from .models import Attempt


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "mode", "category", "state", "score", "created_at"]
    list_filter = ["mode", "state", "category"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
