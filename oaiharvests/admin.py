from django.contrib import admin

from .models import Repository, Community, Collection, MetadataElement, Record


class RecordInlineElementsAdmin(admin.StackedInline):
    model = MetadataElement
    fields = ('element_data',)
    readonly_fields = ('record', 'element_type', 'element_data',)
    extra = 0

class CollectionInlineRecordsAdmin(admin.StackedInline):
    model = Record
    fields = ('identifier', 'hdr_datestamp')
    readonly_fields = ('identifier', 'hdr_datestamp', 'hdr_setSpec',)
    extra = 0

class CommunityInlineCollectionsAdmin(admin.StackedInline):
    model = Collection
    fields = ('identifier', 'name', 'community')
    readonly_fields = ('identifier', 'name', 'community',)
    extra = 0

class CommunityAdmin(admin.ModelAdmin):
    inlines = [
            CommunityInlineCollectionsAdmin,
        ]

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'identifier', 'name', 'community',)
    list_display_links = ('pk',)
    list_editable = ['identifier', 'name', 'community',]
    
    inlines = [
            CollectionInlineRecordsAdmin,
        ]

class RecordAdmin(admin.ModelAdmin):
    inlines = [
            RecordInlineElementsAdmin,
        ]
    list_display = ('identifier', 'hdr_setSpec', 'hdr_datestamp',)
    readonly_fields = ('identifier', 'hdr_setSpec', 'hdr_datestamp',)
    list_editable = ['hdr_setSpec',]
    list_filter = ('hdr_setSpec',)

class MetadataElementAdmin(admin.ModelAdmin):
    list_display = ('record', 'element_type', 'element_data',)
    list_filter = ('record__hdr_setSpec',)
    list_editable = ['element_data',]


admin.site.register(Repository)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(MetadataElement, MetadataElementAdmin)