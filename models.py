import sys
import logging
from google.appengine.ext import db

class Repository:

    def find_party_by_abbreviation(self, abbr):
        return db.Query(Party).filter('abbreviation =', abbr).get()

    def find_institute_by_name(self, name):
        return db.Query(Institute).filter('name = ', name).get()

    def find_recent_polls(self, count):
        return db.Query(Poll).order('-publish_date').fetch(count)

    def remove_all_polling_data(self):
        for result in PollingResult.all():
            result.delete()
        for poll in Poll.all():
            poll.delete()

class Party(db.Model):
    name = db.StringProperty(required=True)
    abbreviation = db.StringProperty(required=True)
    color = db.StringProperty(required=True)
    position = db.IntegerProperty()

    def find_by_abbreviation(self, abbr):
        return db.GqlQuery("")

    def is_left(self):
        return self.abbreviation in ['S','V','MP']

    def is_right(self):
        return self.abbreviation in ['M','FP','C','KD']


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

    def left_block_percentage(self):
        sum = 0
        for k in self.results:
            result = db.get(k)
            if result.party.is_left():
                sum += result.percentage
        return sum

    def right_block_percentage(self):
        sum = 0
        for k in self.results:
            result = db.get(k)
            if result.party.is_right():
                sum += result.percentage
        return sum

    def other_block_percentage(self):
        sum = 0
        for k in self.results:
            result = db.get(k)
            if not (result.party.is_left()) and not (result.party.is_right()):
                sum += result.percentage
        return sum

class PollingAverage:

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

    def top_party(self, parties):
        top_percentage = 0.0
        top_party = None
        for party, percentage in parties.iteritems():
            if percentage >= top_percentage:
                top_party = party
                top_percentage = percentage

        return top_party

    def seats(self):
        limit = 4.0
        qualified = {}
        seats = {}
        for party, percentage in self.percentages.iteritems():
            seats[party] = 0
            if percentage >= limit:
                qualified[party] = percentage / 1.4

        remaining = 349
        while remaining > 0:
            top = self.top_party(qualified)
            seats[top] += 1
            qualified[top] = self.percentages[top] / (1.0 + seats[top] * 2.0)
            remaining -= 1

        return seats

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
            if party.is_left():
                sum += v
        return sum

    def right_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            party = db.get(k)
            if party.is_right():
                sum += v
        return sum

    def other_block_percentage(self):
        sum = 0
        for k, v in self.percentages.iteritems():
            party = db.get(k)
            if not (party.is_left()) and not (party.is_right()):
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
    bar_width = 'a' # Automatic
    bar_spacing = '20'
    marker_color = 'dddddd'

    def __init__(self, avg):
        Chart.__init__(self, '500x400', 'bvs')
        self.avg = avg

    def build_url(self):
        ceil = 40.0
        cutoff_ratio = 4.0/ceil 
        url = Chart.base_url(self) + '&' + \
              Chart.add(self, 'chtt=', 'Procent') + '&' + \
              Chart.add(self, Chart.param_marker, 'r,' + self.marker_color + ',0,0,' + str(cutoff_ratio)) + '&' + \
              Chart.add(self, self.param_bar_width, self.bar_width + ',' + self.bar_spacing) + '&' + \
              Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&'

        data = colors = labels = ''
        for party in Party.all().order('position'):
            data += str(self.avg.percentage_of(party)) + ','
            labels += party.abbreviation + ' ' + ('%.1f' % self.avg.percentage_of(party)) + '|'
            colors += party.color + '|'

        return url + Chart.add(self, Chart.param_data, data[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_colors, colors[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
                     Chart.add(self, Chart.param_ranges, '0,0,0|1,0,' + str(ceil)) + '&' + \
                     Chart.add(self, Chart.param_labels, labels[0:-1])


class PartyResultLineChart(Chart):
    margin = 10
    param_line_style = 'chls='

    def __init__(self, polls):
        Chart.__init__(self, '500x400', 'lxy')
        self.polls = []
        for poll in polls:
          self.polls.append(poll)
        self.polls.reverse()   
        self.avg = PollingAverage(polls)

    def build_url(self):
        ceil = 40.0
        url = Chart.base_url(self) + \
              Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
              Chart.add(self, Chart.param_ranges, '1,0,' + str(len(self.polls)) + '|1,0,' + str(ceil)) + ',5&' + \
              Chart.add(self, 'chtt=', 'Utveckling') + '&' + \
              Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&'

        data = colors = legends = line_style = ''

        for party in Party.all().order('position'):
            data += '-1|'
            colors += party.color + ','
            legends += party.abbreviation + '|'
            line_style += '3|'
            for poll in self.polls:
                data += str(poll.percentage_of(party)) + ','
            data = data[0:-1] + '|'
        x_axis = ''
        i = len(self.polls)
        for poll in self.polls:
            x_axis += '|' + str(i)
            i -= 1

        return url + Chart.add(self, Chart.param_data, data[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_colors, colors[0:-1]) + '&' + \
                     Chart.add(self, self.param_legends, legends[0:-1]) + '&' + \
                     Chart.add(self, 'chxl=0:', x_axis) + '&' + \
                     Chart.add(self, self.param_line_style, line_style[0:-1])


class BlockLineChart(Chart):
    margin = 10
    param_line_style = 'chls='

    def __init__(self, polls):
        Chart.__init__(self, '500x400', 'lxy')
        self.polls = []
        for poll in polls:
          self.polls.append(poll)
        self.polls.reverse()
        self.avg = PollingAverage(polls)

    def build_url(self):
        ceil = 60.0
        url = Chart.base_url(self) + \
              Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
              Chart.add(self, Chart.param_ranges, '1,0,' + str(len(self.polls)) + '|1,0,' + str(ceil)) + ',5&' + \
              Chart.add(self, 'chtt=', 'Utveckling') + '&' + \
              Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&'

        data = colors = legends = line_style = ''

        colors = 'fd3131,85cbeb,adadad'
        legends = 'Soc.|Borg|Ovr.'
        line_style = '3|3|3'

        data += '-1|'
        for poll in self.polls:
            data += str(poll.left_block_percentage()) + ','

        data = data[0:-1]
        data += '|-1|'
        for poll in self.polls:
            data += str(poll.right_block_percentage()) + ','

        data = data[0:-1]
        data += '|-1|'
        for poll in self.polls:
            data += str(poll.other_block_percentage()) + ','

        x_axis = ''
        i = len(self.polls)
        for poll in self.polls:
            x_axis += '|' + str(i)
            i -= 1

        return url + Chart.add(self, Chart.param_data, data[0:-1]) + '&' + \
                     Chart.add(self, Chart.param_colors, colors) + '&' + \
                     Chart.add(self, self.param_legends, legends) + '&' + \
                     Chart.add(self, 'chxl=0:', x_axis) + '&' + \
                     Chart.add(self, self.param_line_style, line_style)


class BlockPieChart(Chart):

    def __init__(self, avg):
        Chart.__init__(self, '250x400', 'bvs')
        self.avg = avg

    def build_url(self):
        ceil = 50.0
        left_sum = self.avg.left_block_percentage()
        right_sum = self.avg.right_block_percentage()
        other_sum = self.avg.other_block_percentage()

        data = str(left_sum) + ',' + str(right_sum) + ',' + str(other_sum)
        colors = 'fd3131|85cbeb|adadad'
        labels = 'Soc. ' + ('%.1f' % left_sum) + '|Borg. ' + ('%.1f' % right_sum) + '|&Ouml;vr. ' + ('%.1f' % other_sum)

        return Chart.base_url(self) + '&' + \
               Chart.add(self, Chart.param_data, data) + '&' + \
               Chart.add(self, Chart.param_colors, colors) + '&' + \
               Chart.add(self, 'chbh=', 'a,30') + '&' + \
               Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
               Chart.add(self, Chart.param_ranges, '0,0,0|1,0,' + str(ceil)) + '&' + \
               Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&' + \
               Chart.add(self, 'chtt=', 'Procent') + '&' + \
               Chart.add(self, Chart.param_labels, labels)


class SeatsChart(Chart):

    def __init__(self, avg):
        Chart.__init__(self, '250x400', 'bvs')
        self.avg = avg

    def build_url(self):
        ceil = 200.0

        left_sum = right_sum = other_sum = 0
        #bars = [[],[],[]]
        #colors = ''
        for k, v in self.avg.seats().iteritems():
            party = db.get(k)
            if party.is_left():
                #bars[0].append(v)
                left_sum += v
            elif party.is_right():
                #bars[1].append(v)
                right_sum += v
            elif party.abbreviation == 'SD':
                #bars[2].append(v)
                other_sum += v
            #colors += party.color + '|'

        #data = ''
        #for i in range(0,4):
        #    for bar in bars:
        #        if len(bar) > 0:
        #            data += str(bar.pop()) + ','
        #        else:
        #            data += '0,'
        #    data = data[0:-1] + '|'

        #data = data[0:-1]
        #colors = colors[0:-1]

        data = str(left_sum) + ',' + str(right_sum) + ',' + str(other_sum)
        labels = 'Soc. ' + str(left_sum) + ' |Borg. ' + str(right_sum) + ' |SD ' + str(other_sum)
        colors = 'fd3131|85cbeb|729cb6'

        return Chart.base_url(self) + '&' + \
               Chart.add(self, Chart.param_data, data) + '&' + \
               Chart.add(self, Chart.param_colors, colors) + '&' + \
               Chart.add(self, 'chbh=', 'a,30') + '&' + \
               Chart.add(self, Chart.param_axes, 'x,y') + '&' + \
               Chart.add(self, Chart.param_ranges, '0,0,0|1,0,' + str(ceil)) + ',25&' + \
               Chart.add(self, Chart.param_scaling, '0,' + str(ceil)) + '&' + \
               Chart.add(self, 'chtt=', 'Mandat') + '&' + \
               Chart.add(self, Chart.param_labels, labels)
