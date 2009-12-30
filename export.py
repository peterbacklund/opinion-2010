from google.appengine.ext import db
from google.appengine.tools import bulkloader
from models import *
import datetime

class InstituteExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Institute',
                                     [('name', str, None)])

class PartyExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Party',
                                     [('name', str, None),
                                      ('abbreviation', str, None),
                                      ('color', str, None),
                                      ('position', str, None)])

def serialize_polling_results(result_keys):
    retval = ''
    results = db.get(result_keys)
    # Moderaterna=28.2|Socialdemokraterna=35.4|...
    for result in results:
        retval += result.party.name + '=' + str(result.percentage) + '|'
    return retval

class PollExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Poll',
                                     [('institute', lambda k: db.get(k).name, None),
                                      ('publish_date', lambda d: d.isoformat(), None),
                                      ('results', serialize_polling_results, None)])

class PollingResultExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'PollingResult',
                                     [('party', str, None),
                                      ('percentage', str, None)])


exporters = [InstituteExporter, PartyExporter, PollExporter, PollingResultExporter]    