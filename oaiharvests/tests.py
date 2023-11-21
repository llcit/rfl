from django.test import TestCase

# Create your tests here.

from oaiharvests.utils import *
from oaiharvests.models import *
from sickle import Sickle

# com = Community.objects.all()[0]

# oai = OAIUtils()
# oai.list_oai_collections(com)

# base_url = 'http://scholarspace.manoa.hawaii.edu/dspace-oai/request'
# llt_id = 'com_10125_27123'

# s = Sickle(base_url)

# record_headers = list(s.ListIdentifiers(metadataPrefix='oai_dc', set=llt_id))

# community_collections = {}  
# for i in record_headers:
#     # Iterate over associated sets looking for collections 
#     for j in i.setSpecs:     
#         if j[:3] == 'col':
#             community_collections[j] = None  # register id in map

# for i in s.ListSets():
#     try:
#         print community_collections[i.setSpec]
#         community_collections[i.setSpec] = i.setName
#         print i.setSpec, '==>', community_collections[i.setSpec]
#         print i
#     except KeyError as e:
#         pass
#         # print e, 'not a collection in llt ...'

# sample = 'oai:scholarspace.manoa.hawaii.edu:10125/54329'
# s.GetRecord(identifier=sample, metadataPrefix='oai_dc')

