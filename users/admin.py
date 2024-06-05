from django.contrib import admin

from users.models import Funding, User, WalletSummary

# Register your models here.

admin.site.register(User)
admin.site.register(Funding)
admin.site.register(WalletSummary)
