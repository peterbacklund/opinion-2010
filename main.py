from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
import time
from datetime import date,datetime

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        url = 'http://chart.apis.google.com/chart?chs=600x300&cht=bvs&chbh=a&chds=0,50'

        parties = Party.all()
        polls = Poll.all()

        pieces = '&chd=t:'
        labels = '&chl='
        colors = '&chco='
        legends = '&chdl='
        for poll in polls:
            for party in parties:
                pieces += str(poll.percentage_of(party)) + ','
                labels += party.abbreviation + '|'
                colors += party.color + '|'
                legends += party.name + '|'
        pieces += '0.0'
        labels += 'NONE'
        colors += '123456'
        legends += 'NONE'


        self.response.out.write('<img src="%s" alt="FAIL"/>' % (url + pieces + labels + colors + legends))

application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def setup_sample_data():
    sifo = Institute(name = "SIFO")
    sifo.put()

    v = Party(name = "Vansterpartiet", abbreviation = "V", color = "#555")
    v.put()

    s = Party(name = "Socialdemokraterna", abbreviation = "S", color = "#F00")
    s.put()

    mp = Party(name = "Miljopartiet", abbreviation = "MP", color = "#123")
    mp.put()

    c = Party(name = "Centerpartiet", abbreviation = "C", color = "#234")
    c.put()

    fp = Party(name = "Folkpartiet", abbreviation = "FP", color = "#345")
    fp.put()

    m = Party(name = "Moderaterna", abbreviation = "M", color = "#456")
    m.put()

    kd = Party(name = "Kristdemokraterna", abbreviation = "KD", color = "#567")
    kd.put()

    pp = Party(name = "Piratpartiet", abbreviation = "PP", color = "#678")
    pp.put()

    fi = Party(name = "Feministiskt Initiativ", abbreviation = "FI", color = "#789")
    fi.put()

    sd = Party(name = "Sverigedemokraterna", abbreviation = "SD", color = "#89A")
    sd.put()

    ovr = Party(name = "Ovriga", abbreviation = "OVR", color = "#9AB")
    ovr.put()

    results = [
            PollingResult(party = s, percentage = 38.0),
            PollingResult(party = v, percentage = 5.0),
            PollingResult(party = mp, percentage = 5.0),    # 48
            PollingResult(party = c, percentage = 8.0),
            PollingResult(party = fp, percentage = 8.0),
            PollingResult(party = kd, percentage = 6.0),
            PollingResult(party = m, percentage = 24.0),    # 46
            PollingResult(party = fi, percentage = 1.0),
            PollingResult(party = sd, percentage = 2.0),
            PollingResult(party = pp, percentage = 3.0),    # 6
    ]
    list = []
    for result in results:
        result.put()
        list.append(result.key())

    poll = Poll(publish_date = datetime.today(), institute = sifo, results = list, sample_size = 2000, question_asked = "Vilket parti gillar du?")
    poll.put()

def main():
    #setup_sample_data()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()