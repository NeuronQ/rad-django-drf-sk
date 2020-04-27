from django.shortcuts import render
from django.http import HttpResponse


# def index(request):
#     return HttpResponse("Let there be light!")

def index(request):
    return render(request, 'coreapp/index.html', {
        "answer": 196883,
    })
