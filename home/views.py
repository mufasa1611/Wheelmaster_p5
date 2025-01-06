from django.shortcuts import render

# Create your views here.

def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)
