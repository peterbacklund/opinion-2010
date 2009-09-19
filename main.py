from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import logging
import time
import os
from datetime import date,datetime
from string import Template

from models import *
from sample_data import *
import sample_data

class MainPage(webapp.RequestHandler):

    def generate_index_html(self):
      parties = Party.all().order('position')
      polls = repository.find_recent_polls(10)
      avg = PollingAverage(polls)

      # TODO memcache this behind a UrlFactory
      partyAverage = PartyAverageBarChart(avg).build_url()
      partyResult = PartyResultLineChart(polls).build_url()
      block = BlockPieChart(avg).build_url()
      seats = SeatsChart(avg).build_url()

      # Not cool

      party_percentages_html = ''
      polls_reversed = []
      for poll in polls:
        polls_reversed.append(poll)
      polls_reversed.reverse()

      for party in parties:
          party_percentages_html += \
            '<tr><td class="party_img"><img src="/img/' + party.abbreviation + \
            '.jpg" alt="' + party.name + '" title="' + party.name + \
            '"/></td>'
          for poll in polls_reversed:
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

      return template.render('templates/index.html', template_values)

    def get(self):
      index_html = memcache.get('INDEX_HTML')
      if index_html is None:
        index_html = self.generate_index_html()
        memcache.add('INDEX_HTML', index_html)
        logging.info('Generated new index.html')
      else:
        logging.info('Using cached index.html')

      self.response.out.write(index_html)

class AddPoll(webapp.RequestHandler):
    def get(self):
        model = {
        'parties' : Party.all(),
        'institutes' : Institute.all()
        }
        self.response.out.write(template.render('templates/poll_form.html', model))

class StorePoll(webapp.RequestHandler):

    # TODO move to repository
    def store_poll(self):
      r = self.request
      publish_date = datetime.strptime(r.get('publish_date'), '%Y-%m-%d')
      institute_key = r.get('institute_key')
      institute = Institute.get(institute_key)
      polling_results = []
      for party in Party.all():
          percentage = float(r.get(party.abbreviation))
          pr = PollingResult(party=party, percentage=percentage)
          pr.save()
          polling_results.append(pr.key())
      poll = Poll(publish_date = publish_date, institute = institute, results = polling_results)
      poll.save()
      logging.info("Stored poll: " + str(publish_date) + ", " + institute.name)

    def post(self):
        try:
            self.store_poll()
            memcache.delete('INDEX_HTML')
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

class ClearCache(webapp.RequestHandler):

    def get(self):
        memcache.delete('INDEX_HTML')
        self.response.out.write('Cache cleared')

class SetPosition(webapp.RequestHandler):

    def do_it(self, abbr, pos):
      party = repository.find_party_by_abbreviation(abbr)
      party.position = pos
      party.save()

    def get(self):
        self.do_it('V',  1)
        self.do_it('S',  2)
        self.do_it('MP', 3)
        self.do_it('C',  4)
        self.do_it('FP', 5)
        self.do_it('M',  6)
        self.do_it('KD', 7)
        self.do_it('SD', 8)
        self.do_it('OVR',9)

        self.response.out.write('OK')


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
        #('/setup_polls', SetupPolls),
        #('/clear', ClearPage),
        #('/first', FirstPage),
        ('/poll/add', AddPoll),
        ('/poll/store', StorePoll),
        ('/set_position', SetPosition),
        ('/clear_cache', ClearCache),
        ], debug=False)

repository = Repository()

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()