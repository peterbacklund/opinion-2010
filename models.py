import sys
import logging
from google.appengine.ext import db

class Party(db.Model):
    name = db.StringProperty(required=True)
    abbreviation = db.StringProperty(required=True)
    color = db.StringProperty(required=True)

    def find_by_abbreviation(self, abbr):
        return db.GqlQuery("")

class Institute(db.Model):
    name = db.StringProperty(required=True)


class PollingResult(db.Model):
    party = db.ReferenceProperty(Party, required=True)
    percentage = db.FloatProperty(required=True)

    #def my_validate(self, errors):
    #    if self.percentage > 100.0:
    #        errors.add('Percentage must be smaller than or equal to 100.0: ' + self.percentage)
    #    if self.percentage < 0.0:
    #        errors.add('Percentage must be large than or equal to 0.0: ' + self.percentage)
    #    if self.party == None:
    #        errors.add('Party is required')
    #    return errors


class Poll(db.Model):
    publish_date = db.DateTimeProperty(required=True)
    institute = db.ReferenceProperty(Institute, required=True)
    results = db.ListProperty(db.Key, required=True)
    sample_size = db.IntegerProperty(required=True)
    question_asked = db.StringProperty(required=True)

    #def my_validate(self, errors):
    #    sum = 0.0
    #    for result in self.results:
    #        sum += result.percentage
    #    if sum != 100.0:
    #        errors.add('Sum of percentages must be 100.0: ' + sum)
    #    return errors

    def percentage_of(self, party):
        results = db.get(self.results)
        for result in results:
            if result.party.key() == party.key():
                return result.percentage
        return 0.0

class PollingAverage:

    def __init__(self, polls):
        self.left_parties = ['S','V','MP']
        self.right_parties = ['C','FP','M','KD']
        self.percentages = {}
        for poll in polls:
            for resultkey in poll.results:
                result = db.get(resultkey)
                if result.party.abbreviation in self.percentages:
                    prev = self.percentages[result.party.abbreviation]
                else:
                    prev = 0.0  

                self.percentages[result.party.abbreviation] = prev + result.percentage
        for k, v in self.percentages.iteritems():
            self.percentages[k] = v/len(polls)

    def percentage_of(self, party):
        if party.abbreviation in self.percentages:
            return self.percentages[party.abbreviation]
        else:
            return 0.0

    def max_percentage(self):
        max = 0.0
        for k, v in self.percentages.iteritems():
            if v > max:
                max = v
        return max

    def left_block_percentage(self):    
        sum = 0
        for k, v in self.percentages.iteritems():
            if k in self.left_parties:
                sum += v
        return sum

    def right_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            if k in self.right_parties:
                sum += v
        return sum

    def other_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            if not (k in self.left_parties) and not (k in self.right_parties):
                sum += v
        return sum                


class Chart:
    chart_api_url = 'http://chart.apis.google.com/chart?'
    pass

class PartyAverageBarChart(Chart):
    width = 1000
    height = 300
    pass

class PartyResultLineChart(Chart):
    pass

class BlockPieChart(Chart):
    pass
