from django.contrib import admin
from .models import Ad, IllegalLogin


class IllegalLoginInline(admin.TabularInline):
    model = IllegalLogin


class AdAdmin(admin.ModelAdmin):
    exclude = ('price_equation', )
    inlines = [IllegalLoginInline, ]



admin.site.register(Ad, AdAdmin)