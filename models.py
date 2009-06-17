import sys
sys.path.append("/Users/peter/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")
sys.path.append("/Users/peter/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib")
sys.path.append("/Users/peter/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/yaml/lib")

from google.appengine.ext import db

class Party(db.Model):
    name = db.StringProperty()
    abbreviation = db.StringProperty()
    color = db.StringProperty()


class Institute(db.Model):
    name = db.StringProperty()


class PollingResult(db.Model):
    party = db.ReferenceProperty(Party)
    percentage = db.FloatProperty()

    def my_validate(self, errors):
        if self.percentage > 100.0:
            errors.add('Percentage must be smaller than or equal to 100.0: ' + self.percentage)
        if self.percentage < 0.0:
            errors.add('Percentage must be large than or equal to 0.0: ' + self.percentage)
        if self.party == None:
            errors.add('Party is required')
        return errors


class Poll(db.Model):
    publish_date = db.DateTimeProperty()
    institute = db.ReferenceProperty(Institute)
    results = db.ListProperty(db.Key)
    sample_size = db.IntegerProperty()
    question_asked = db.StringProperty()

    def my_validate(self, errors):
        sum = 0.0
        for result in self.results:
            sum += result.percentage
        if sum != 100.0:
            errors.add('Sum of percentages must be 100.0: ' + sum)
        return errors
    
    def percentageOf(self, party):
        for result in self.results:
            loaded_result = db.get(result)
            if loaded_result.party.key() == party.key():
                return loaded_result.percentage
        return 0.0