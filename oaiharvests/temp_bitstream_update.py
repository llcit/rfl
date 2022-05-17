# temp_bitstream_update.py
from oaiharvests.utils import *
from oaiharvests.models import *

# Namespaces
rdf_ns = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
atom_ns = '{http://www.w3.org/2005/Atom}'
dc_ns = '{http://purl.org/dc/terms/}'

# OAI repo
base_url = 'http://scholarspace.manoa.hawaii.edu/dspace-oai/request'
sickle = Sickle(base_url)
sickle.class_mapping['GetRecord'] = LltRecordBitstream_v2

def bitstream_update(record_obj=None):
	try:
		record_xml = sickle.GetRecord(metadataPrefix='ore', identifier=record_obj.identifier)
		bitstreams = record_xml.metadata
		try:
			e = record_obj.data.filter(element_type='bitstream')[0]
			e.element_data = json.dumps([bitstreams['bitstream']])
			e.save()
		except Exception as e:
			print(e)

		try:
			e = record_obj.data.filter(element_type='bitstream_txt')[0]
			e.element_data = json.dumps([bitstreams['bitstream_txt']])
			e.save()
		except Exception as ex:
			print(ex)
	except Exception as ex:
		print(record_obj, ex)