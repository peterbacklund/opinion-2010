import sys

from google.appengine.ext import db

class Party(db.Model):
    name = db.StringProperty(required=True)
    abbreviation = db.StringProperty(required=True)
    color = db.StringProperty(required=True)


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