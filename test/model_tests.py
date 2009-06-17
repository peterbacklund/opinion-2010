import unittest
from models import *

class SimpleTestCase(unittest.TestCase):
    def testSimple(self):
        a = Party(name = "TEST", abbreviation = "T", color = "")
        a.put()
        self.assertEqual("TEST", a.name)

        b = Institute(name = "SIFO")
        b.put()
        self.assertEqual("SIFO", b.name)

        c = Poll(institute = b)
        self.assertEqual("SIFO", c.institute.name)

class PollingResultTestCase(unittest.TestCase):

    def setUp(self):
        self.s = Party(name = "Socialdemokraterna", abbreviation = "S", color = "#F00")
        self.s.put()

    def testValid(self):
        pollingResult = PollingResult(party = self.s, percentage = 35.0)

    def testPercentageTooLarge(self):
        self.assertRaises(Exception, PollingResult(party = self.s, percentage = 110.0))

    def testPercentageTooSmall(self):
        self.assertRaises(Exception, PollingResult(party = self.s, percentage = -10.0))


class PollTestCase(unittest.TestCase):
    def setUp(self):
        self.institute = Institute(name = "SIFO")
        self.institute.put()

        self.s = Party(name = "Socialdemokraterna", abbreviation = "S", color = "#F00")
        self.s.put()
        self.m = Party(name = "Moderaterna", abbreviation = "M", color = "")
        self.m.put()
        self.pp = Party(name = "Piratpartiet", abbreviation = "PP", color = "")
        self.pp.put()
        self.ka = Party(name = "Kalle Anka", abbreviation = "KA", color = "")
        self.ka.put()
        
        self.result_s  = PollingResult(party = self.s, percentage = 50.0)
        self.result_s.put()
        self.result_m  = PollingResult(party = self.m, percentage = 40.0)
        self.result_m.put()
        self.result_pp = PollingResult(party = self.pp, percentage = 20.0)
        self.result_pp.put()
        self.result_ka = PollingResult(party = self.pp, percentage = 10.0)
        self.result_ka.put()

    def testValid(self):
        poll = Poll(results = [self.result_s.key(), self.result_m.key(), self.result_pp.key()])
        self.assertEquals(50.0, poll.percentageOf(self.s))
        self.assertEquals(40.0, poll.percentageOf(self.m))
        self.assertEquals(20.0, poll.percentageOf(self.pp))

    def testDuplicatePartyNotAllowed(self):
        self.assertRaises(Exception, Poll(results = [self.result_s.key(), self.result_s.key()]))

    def testTotalPercentageTooLarge(self):
        self.assertRaises(Exception, Poll(results = [self.result_s.key(), self.result_m.key(), self.result_pp.key(), self.result_ka.key()]))

    def testTotalPercentageTooSmall(self):
        self.assertRaises(Exception, Poll(results = [self.result_s.key(), self.result_m.key()]))

if __name__ == '__main__':
    unittest.main()
