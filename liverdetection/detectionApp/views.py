from django.shortcuts import render, redirect
from .forms import ImageUploadForm


def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, "detectionApp/results.html")
    else:
        form = ImageUploadForm()
    return render(request, 'detectionApp/index.html', {'form': form})


def results(request):
    return render(request, 'detectionApp/results.html')

