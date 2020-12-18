from django.contrib import admin
from .models import Account, Transfer


class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance')


class TransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin_id', 'destination_id', 'balance', 'cancelled')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(Transfer, TransferAdmin)
