import sys
import logging
from google.appengine.ext import db

class Repository(db.Model):

    def find_party_by_abbreviation(self, abbr):
        return db.Query(Party).filter('abbreviation =', abbr).get()

    def find_institute_by_name(self, name):
        return db.Query(Institute).filter('name = ', name).get()

    def find_recent_polls(self, count):
        return db.Query(Poll).order('-publish_date').fetch(count)


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
    left_parties = ['S','V','MP']
    right_parties = ['C','FP','M','KD']

    def __init__(self, polls):
        self.percentages = {}
        for poll in polls:
            for resultkey in poll.results:
                result = db.get(resultkey)
                if result.party.key() in self.percentages:
                    prev = self.percentages[result.party.key()]
                else:
                    prev = 0.0  

                self.percentages[result.party.key()] = prev + result.percentage
        for k, v in self.percentages.iteritems():
            self.percentages[k] = v/len(polls)

    def percentage_of(self, party):
        if party.key() in self.percentages:
            return self.percentages[party.key()]
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
            party = db.get(k)
            if party.abbreviation in self.left_parties:
                sum += v
        return sum

    def right_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            party = db.get(k)
            if party.abbreviation in self.right_parties:
                sum += v
        return sum

    def other_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            party = db.get(k)
            if not (party.abbreviation in self.left_parties) and not (party.abbreviation in self.right_parties):
                sum += v
        return sum                

    def parties(self):
        return db.get(self.percentages.keys())
        
class Chart:
    chart_api_url = 'http://chart.apis.google.com/chart?'
    param_type = 'cht='
    param_dimension = 'chs='
    param_data = 'chd=t:'
    param_marker = 'chm='
    param_axes = 'chxt='
    param_ranges = 'chxr='
    param_colors = 'chco='
    param_labels = 'chl='
    param_scaling = 'chds='
    param_legends = 'chdl='

    def __init__(self, dimension, type):
        self.dimension = dimension
        self.type = type

    def add(self, param, value):
        return param + value

    def base_url(self):
        return self.chart_api_url + \
               self.add(self.param_type, self.type) + '&' + \
               self.add(self.param_dimension, self.dimension) + '&'


class PartyAverageBarChart(Chart):
    margin = 10
    param_bar_width = 'chbh='
    marker_color = 'dddddd'

    def __init__(self, avg):
        Chart.__init__(self, '1000x300', 'bvs')
        self.avg = avg

    def build_url(self):
        cutoff_ratio = 4.0/self.avg.max_percentage()
        ceil = self.avg.max_percentage() + self.margin
        url = Chart.base_url(self) + '&' + \
              Chart.add(self, Chart.param_marker, 'r,' + self.marker_color + ',0,0,' + str(cutoff_ratio)) + '&' + \
              Chart.add(self, self.param_bar_width, 'a,20') + '&' + \
              Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&'

        data = colors = labels = ''
        for party in Party.all():
            data += str(self.avg.percentage_of(party)) + ','
            labels += party.abbreviation + ' ' + str(self.avg.percentage_of(party)) + ' %|'
            colors += party.color + '|'

        return url + Chart.add(self, Chart.param_data, data[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_colors, colors[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_labels, labels[0:-1])


class PartyResultLineChart(Chart):
    margin = 10

    def __init__(self, polls):
        Chart.__init__(self, '500x400', 'lxy')
        self.polls = polls
        self.avg = PollingAverage(polls)

    def build_url(self):
        ceil = self.avg.max_percentage() + self.margin
        url = Chart.base_url(self) + \
              Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
              Chart.add(self, Chart.param_ranges, '1,0,50|1,0,' + str(ceil)) + '&' + \
              Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&'
        data = colors = legends = ''

        for party in Party.all():
            data += '5,20|'
            colors += party.color + ','
            legends += party.name + '|'
            for poll in self.polls:
                data += str(poll.percentage_of(party)) + ','
            data = data[0:-1] + '|'

        return url + Chart.add(self, Chart.param_data, data[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_colors, colors[0:-1]) + '&' + \
                     Chart.add(self, self.param_legends, legends[0:-1])


class BlockPieChart(Chart):

    def __init__(self, avg):
        Chart.__init__(self, '600x300', 'p')
        self.avg = avg

    def build_url(self):
        left_sum = self.avg.left_block_percentage()
        right_sum = self.avg.right_block_percentage()
        other_sum = self.avg.other_block_percentage()

        data = str(left_sum) + ',' + str(right_sum) + ',' + str(other_sum)
        colors = 'fd3131|85cbeb|adadad'
        legends = 'S/V/MP ' + str(left_sum) + '%|C/FP/M/KD ' + str(right_sum) + '%|SD/FI/PP/OVR ' + str(other_sum) + '%'

        return Chart.base_url(self) + '&' + \
               Chart.add(self, Chart.param_data, data) + '&' + \
               Chart.add(self, Chart.param_colors, colors) + '&' + \
               Chart.add(self, self.param_legends, legends)                       
