from django.shortcuts import render

# Create your views here.
def index(request):
    # A view to return the bag page 
    return render(request, 'bag/bag.html')