from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterForm

def index(request):
    """ A view to return the index page """
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully subscribed to newsletter!')
            return redirect('home')
        else:
            messages.error(request, 'Failed to subscribe. Please check your input.')
    else:
        form = NewsletterForm()

    context = {
        'newsletter_form': form,
    }
    return render(request, 'home/index.html', context)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully subscribed to our newsletter!')
            return redirect('home')
        else:
            messages.error(request, 'Failed to subscribe. Please check your input.')
    else:
        form = NewsletterForm()
    
    context = {
        'form': form,
    }
    return render(request, 'home/newsletter.html', context)

def who_we_are(request):
    return render(request, 'home/who_we_are.html')

def contact(request):
    return render(request, 'home/contact.html')
