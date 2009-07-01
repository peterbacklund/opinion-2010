from models import *
import time
import os
from datetime import date,datetime


repository = Repository()

def setup_parties_and_institutes():
    Institute(name='Sifo').put()
    Institute(name='SCB').put()
    Institute(name='Synovate').put()
    Institute(name='Skop').put()
    Institute(name='Novus').put()
    Institute(name='Demoskop').put()

    Party(name='Vansterpartiet', abbreviation='V', color='cb2e2e').put()
    Party(name='Socialdemokraterna', abbreviation='S', color='fd3131').put()
    Party(name='Miljopartiet', abbreviation='MP', color='339a33').put()
    Party(name='Centerpartiet', abbreviation='C', color='83bb4b').put()
    Party(name='Folkpartiet', abbreviation='FP', color='5caeff').put()
    Party(name='Moderaterna', abbreviation='M', color='85cbeb').put()
    Party(name='Kristdemokraterna', abbreviation='KD', color='497dc1').put()
    Party(name='Sverigedemokraterna', abbreviation='SD', color='729cb6').put()
    Party(name='Ovriga', abbreviation='OVR', color='adadad').put()


def setup_polls():
    results_sifo_2009_06_15 = {
        'S': 32.8,
        'V': 5.2,
        'MP': 8.5,
        'M': 28.2,
        'C': 5.0,
        'FP': 8.8,
        'KD': 4.2,
        'SD': 3.1,
        'OVR': 4.2
    }
    store_poll(datetime(2009, 6, 15), 'Sifo', results_sifo_2009_06_15)

    results_sifo_2009_05_18 = {
        'S': 34.8,
        'V': 5.8,
        'MP': 8.1,
        'M': 28.8,
        'C': 5.8,
        'FP': 6.4,
        'KD': 4.1,
        'SD': 3.0,
        'OVR': 3.3
    }
    store_poll(datetime(2009, 5, 18), 'Sifo', results_sifo_2009_05_18)

    results_sifo_2009_04_19 = {
        'S': 34.6,
        'V': 5.3,
        'MP': 8.6,
        'M': 30.6,
        'C': 5.8,
        'FP': 6.8,
        'KD': 4.1,
        'SD': 2.8,
        'OVR': 1.5
    }
    store_poll(datetime(2009, 4, 19), 'Sifo', results_sifo_2009_04_19)

    results_scb_2009_06_17  = {
        'S': 36.6,
        'V': 5.7,
        'MP': 6.0,
        'M': 29.9,
        'C': 5.5,
        'FP': 5.5,
        'KD': 4.3,
        'SD': 3.0,
        'OVR': 3.0
    }
    store_poll(datetime(2009, 4, 19), 'SCB', results_scb_2009_06_17)

    results_synovate_2009_05_29  = {
        'S': 33.7,
        'V': 7.0,
        'MP': 6.5,
        'M': 29.3,
        'C': 6.1,
        'FP': 6.8,
        'KD': 4.5,
        'SD': 3.6,
        'OVR': 2.6
    }
    store_poll(datetime(2009, 5, 29), 'Synovate', results_synovate_2009_05_29)


    results_skop_2009_05_29  = {
        'S': 33.4,
        'V': 5.3,
        'MP': 7.8,
        'M': 31.6,
        'C': 5.0,
        'FP': 6.4,
        'KD': 4.5,
        'SD': 3.8,
        'OVR': 2.2
    }
    store_poll(datetime(2009, 5, 29), 'Skop', results_skop_2009_05_29)


    results_novus_2009_05_23  = {
        'S': 34.6,
        'V': 7.4,
        'MP': 7.3,
        'M': 29.5,
        'C': 5.4,
        'FP': 6.5,
        'KD': 4.3,
        'SD': 2.6,
        'OVR': 2.4
    }
    store_poll(datetime(2009, 5, 23), 'Novus', results_novus_2009_05_23)


    results_demoskop_2009_05_11  = {
        'S': 34.2,
        'V': 6.1,
        'MP': 6.6,
        'M': 34.5,
        'C': 4.3,
        'FP': 5.4,
        'KD': 3.7,
        'SD': 3.4,
        'OVR': 0.0  # TODO
    }
    store_poll(datetime(2009, 5, 11), 'Demoskop', results_demoskop_2009_05_11)


    results_novus_2009_05__01  = {
        'S': 35.0,
        'V': 7.3,
        'MP': 6.7,
        'M': 29.6,
        'C': 5.4,
        'FP': 5.4,
        'KD': 4.5,
        'SD': 4.4,
        'OVR': 1.9
    }
    store_poll(datetime(2009, 5, 1), 'Novus', results_novus_2009_05__01)


    results_synovate_2009_04_24  = {
        'S': 33.5,
        'V': 7.3,
        'MP': 6.4,
        'M': 32.1,
        'C': 5.7,
        'FP': 5.6,
        'KD': 3.8,
        'SD': 3.6,
        'OVR': 2.1
    }
    store_poll(datetime(2009, 4, 24), 'Synovate', results_synovate_2009_04_24)



def store_poll(date, institute_name, results):
    institute = repository.find_institute_by_name(institute_name)
    pollingResults = []
    for abbr, percentage in results.iteritems():
        party = repository.find_party_by_abbreviation(abbr)
        pollingResult = PollingResult(party = party, percentage = percentage)
        pollingResult.put()
        pollingResults.append(pollingResult.key())
    Poll(publish_date = date, institute = institute, results = pollingResults).put()
