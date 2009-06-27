from models import *

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
