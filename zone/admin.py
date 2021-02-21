from django.contrib import admin
from zone.models import Czone

# Register your models here.
@admin.register(Czone)
class CzoneAdmin(admin.ModelAdmin):
    list_display = ['domain', 'realm', 'user_domain']