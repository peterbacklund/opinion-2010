from django.http import HttpResponse
from django.utils.html import escape

def index(request):
    return HttpResponse('<h1>Maktsifte 2010 (?)</h1>')

