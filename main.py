from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
import time
import os
from datetime import date,datetime
from google.appengine.ext.webapp import template
from string import Template


class MainPage(webapp.RequestHandler):
    def get(self):
        parties = Party.all()
        polls = repository.find_recent_polls(10)
        avg = PollingAverage(polls)

        # TODO memcache this
        partyAverage = PartyAverageBarChart(avg).build_url()
        partyResult = PartyResultLineChart(polls).build_url()
        block = BlockPieChart(avg).build_url()

        # Not cool
        party_percentages_html = ''
        for party in parties:
            party_percentages_html += '<tr><td>' + party.name + '</td>'
            for poll in polls:
                party_percentages_html += '<td>' + str(poll.percentage_of(party)) + '</td>'
            party_percentages_html += '</tr>'

        template_values = {
            'partyAverage' : partyAverage,
            'partyResult' : partyResult,
            'block' : block,
            'polls' : polls,
            'parties' : parties,
            'party_percentages_html' : party_percentages_html
        }

        self.response.out.write(template.render('templates/index.html', template_values))

application = webapp.WSGIApplication([('/', MainPage)], debug=True)
repository = Repository()

def main():
    #setup_sample_data()
    #setup_poll_1()
    run_wsgi_app(application)

if __name__ == "__main__":
    main()