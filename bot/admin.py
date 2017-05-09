from django.contrib import admin
from .models import Ad, LocalUser



class AdAdmin(admin.ModelAdmin):
    exclude = ('price_equation', 'current_amount')


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ad, AdAdmin)
admin.site.register(LocalUser, UserAdmin)