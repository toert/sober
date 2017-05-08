from django.contrib import admin
from .models import Ad



class AdAdmin(admin.ModelAdmin):
    exclude = ('price_equation', )


admin.site.register(Ad, AdAdmin)