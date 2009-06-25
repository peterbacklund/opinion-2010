from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
import time
from datetime import date,datetime

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'


        parties = Party.all()
        polls = Poll.all().fetch(10)

        avg = PollingAverage(polls)


        cutoff = 4.0/avg.max_percentage()
        url = 'http://chart.apis.google.com/chart?chs=1000x300&chxt=x,y&chxr=1,0,' + str(avg.max_percentage()) + '&chm=r,dddddd,0,0,' + str(cutoff) + '&cht=bvs&chbh=a,40&chds=0,' + str(avg.max_percentage())

        pieces = '&chd=t:'
        labels = '&chl='
        colors = '&chco='
        legends = '&chdl='
        for party in parties:
            pieces += str(avg.percentage_of(party)) + ','
            labels += party.abbreviation + '  ' + str(avg.percentage_of(party)) + ' %|'
            colors += party.color + '|'
            legends += party.name + '|'
        pieces += '0.0'
        labels += 'NONE'
        colors += '123456'
        legends += 'NONE'


        self.response.out.write('<img src="%s" alt="FAIL"/>' % (url + pieces + labels + colors))

        url2 = 'http://chart.apis.google.com/chart?chs=500x600&chxt=x,y&chxr=1,0,50|1,0,50&cht=lxy&chbh=a'
        y_values = '&chd=t:'
        colors = '&chco='
        legends = '&chdl='
        for party in parties:
            y_values += '5,20|'
            colors += party.color + '|'
            legends += party.name + '|'
            for poll in polls:
                y_values += str(poll.percentage_of(party)) + ','
            y_values = y_values[0:-1]
            y_values += '|'
        y_values = y_values[0:-1]            
        self.response.out.write('<img src="%s" alt="FAIL2"/>' % (url2 + y_values + legends))

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

def setup_poll_1():
    sifo = db.Query(Institute).filter('name = ', 'SIFO').get()

    s = Party.all().filter('abbreviation = ', 'S').get()
    v = Party.all().filter('abbreviation = ', 'V').get()
    mp = Party.all().filter('abbreviation = ', 'MP').get()
    c = Party.all().filter('abbreviation = ', 'C').get()
    fp = Party.all().filter('abbreviation = ', 'FP').get()
    kd = Party.all().filter('abbreviation = ', 'KD').get()
    m = Party.all().filter('abbreviation = ', 'M').get()
    fi = Party.all().filter('abbreviation = ', 'FI').get()
    sd = Party.all().filter('abbreviation = ', 'SD').get()
    pp = Party.all().filter('abbreviation = ', 'PP').get()

    results = [
            PollingResult(party = s, percentage = 36.5),
            PollingResult(party = v, percentage = 5.5),
            PollingResult(party = mp, percentage = 5.5),    # 47.5
            PollingResult(party = c, percentage = 9.0),
            PollingResult(party = fp, percentage = 6.0),
            PollingResult(party = kd, percentage = 8.0),
            PollingResult(party = m, percentage = 25.5),    # 48.5
            PollingResult(party = fi, percentage = 1.0),
            PollingResult(party = sd, percentage = 1.0),
            PollingResult(party = pp, percentage = 1.0),    # 3
    ]
    list = []
    for result in results:
        result.put()
        list.append(result.key())

    poll = Poll(publish_date = datetime.today(), institute = sifo, results = list, sample_size = 2500, question_asked = "Vilket parti gillar du?")
    poll.put()

def main():
    #setup_sample_data()
    #setup_poll_1()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()