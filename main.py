from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
import time
from datetime import date,datetime

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        repository = Repository()

        parties = Party.all()
        polls = repository.find_recent_polls(10)

        avg = PollingAverage(polls)

        partyAverageBarChart = PartyAverageBarChart(avg)
        self.response.out.write('<div style="width: 1000px"><img src="%s" alt="FAIL"/></div>' % partyAverageBarChart.build_url())

        partyResultLineChart = PartyResultLineChart(polls)
        self.response.out.write('<div style="width: 1200px"><img src="%s" alt="FAIL2"/>' % partyResultLineChart.build_url())

        blockPieChart = BlockPieChart(avg)
        self.response.out.write('<img src="%s" alt="FAIL3"/></div>' % blockPieChart.build_url())


application = webapp.WSGIApplication([('/', MainPage)], debug=True)

def main():
    #setup_sample_data()
    #setup_poll_1()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()