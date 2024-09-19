# search_indexes.py
import datetime

from haystack import indexes

from .models import Record, MetadataElement

class RecordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    identifier = indexes.CharField(model_attr='identifier')
    hdr_datestamp = indexes.CharField(model_attr='hdr_datestamp')
    hdr_setSpec = indexes.CharField(model_attr='hdr_setSpec')

    def get_model(self):
        return Record

    def get_updated_field(self):
        return 'modified'
        
    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()	


# class MetadataElementIndex(indexes.SearchIndex, indexes.Indexable):
#     text = indexes.CharField(document=True, use_template=True)
#     element_data = indexes.CharField(model_attr='element_data')

#     def get_model(self):
#         return MetadataElement

#     def index_queryset(self, using=None):
#         """Used when the entire index for model is updated."""
#         return self.get_model().objects.all()