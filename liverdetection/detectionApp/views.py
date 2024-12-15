from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    # return HttpResponse('<h4>Проверка</h4>')
    return render(request, "detectionApp/index.html")