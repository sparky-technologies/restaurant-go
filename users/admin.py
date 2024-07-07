from django.contrib import admin

from users.models import Funding, Tray, TrayItem, User, WalletSummary

# Register your models here.


class TrayAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "created_at"]


admin.site.register(User)
admin.site.register(Funding)
admin.site.register(WalletSummary)
admin.site.register(Tray, TrayAdmin)
admin.site.register(TrayItem)
