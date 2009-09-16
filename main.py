from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
from sample_data import *
import time
import os
from datetime import date,datetime
from google.appengine.ext.webapp import template
from string import Template
import sample_data
import logging

class MainPage(webapp.RequestHandler):
    def get(self):
        parties = Party.all()
        polls = repository.find_recent_polls(10)
        avg = PollingAverage(polls)

        # TODO memcache this behind a UrlFactory
        partyAverage = PartyAverageBarChart(avg).build_url()
        partyResult = PartyResultLineChart(polls).build_url()
        block = BlockPieChart(avg).build_url()
        seats = SeatsChart(avg).build_url();

        # Not cool
        party_percentages_html = ''
        for party in parties:
            party_percentages_html += '<tr><td>' + party.abbreviation + '</td>'
            for poll in polls:
                party_percentages_html += '<td>' + str(poll.percentage_of(party)) + '</td>'
            party_percentages_html += '<td><strong>' + ("%10.1f" % avg.percentage_of(party)) + '</strong></td>'
            party_percentages_html += '</tr>'

        template_values = {
        'partyAverage' : partyAverage,
        'partyResult' : partyResult,
        'block' : block,
        'polls' : polls,
        'parties' : parties,
        'seats' : seats,
        'party_percentages_html' : party_percentages_html
        }

        self.response.out.write(template.render('templates/index.html', template_values))

class AddPoll(webapp.RequestHandler):
    def get(self):
        model = {
        'parties' : Party.all(),
        'institutes' : Institute.all()
        }
        self.response.out.write(template.render('templates/poll_form.html', model))

class StorePoll(webapp.RequestHandler):

    # TODO move to repository (?)
    def do_work(self, request):
      institute_key = request.get('institute_key')
      publish_date = datetime.strptime(request.get('publish_date'), '%Y-%m-%d')

      institute = Institute.get(institute_key)
      polling_results = []
      for party in Party.all():
          percentage = float(request.get(party.abbreviation))
          pr = PollingResult(party=party, percentage=percentage)
          pr.save()
          polling_results.append(pr.key())

      logging.info(str(publish_date) + ", " + institute.name + ", " + str(polling_results))
      poll = Poll(publish_date = publish_date, institute = institute, results = polling_results)
      poll.save()

    def post(self):
        try:
            db.run_in_transaction(self.do_work(self.request))
            self.redirect('/')
        except:
            self.response.out.write('Error: ' + str(sys.exc_info()))

class SetupPolls(webapp.RequestHandler):
    def get(self):
        sample_data.setup_polls()
        self.response.out.write('Sample data inserted')

class ClearPage(webapp.RequestHandler):
    def get(self):
        repository.remove_all_polling_data()
        self.response.out.write('Sample data cleared')

class FirstPage(webapp.RequestHandler):
    def get(self):
        for party in Party.all():
            party.delete()
        for institute in Institute.all():
            institute.delete()
        sample_data.setup_parties_and_institutes()
        for party in Party.all():
            self.response.out.write(party.name)

application = webapp.WSGIApplication([
        ('/', MainPage),
        ('/setup_polls', SetupPolls),
        ('/clear', ClearPage),
        ('/first', FirstPage),
        ('/poll/add', AddPoll),
        ('/poll/store', StorePoll),
        ], debug=False)

repository = Repository()

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()