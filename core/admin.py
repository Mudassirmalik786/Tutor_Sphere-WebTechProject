from django.contrib import admin

from core.models import About, FrequentlyAskedQuestion

# Register your models here.

admin.site.register(FrequentlyAskedQuestion)
admin.site.register(About)
