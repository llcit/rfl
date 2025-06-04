# lltsite/admin.py
from django.contrib import admin

from .models import StoryPage, Subscriber, ImpactFactor

class ExtraMedia:
    js = [
        '/static/nflrc-slrp/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
        '/static/js/tinymce_setup.js',
    ]

class StoryPageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'featured', 'get_absolute_url', 'slug')
    list_editable = ('slug',)
    list_display_links = ('pk',)

class SubscriberListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'first_name', 'last_name')
    list_editable = ('first_name', 'last_name')
    search_fields = ['first_name', 'last_name', 'email']

admin.site.register(StoryPage, StoryPageAdmin, Media = ExtraMedia)
admin.site.register(Subscriber, SubscriberListAdmin)
admin.site.register(ImpactFactor)
