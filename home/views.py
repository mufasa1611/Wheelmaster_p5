from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.conf import settings
import os
from .forms import NewsletterForm, ContactForm

def index(request):
    form = NewsletterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Successfully subscribed to the newsletter!')
        return redirect('home')
    return render(request, 'home/index.html', {'newsletter_form': form})

def newsletter_signup(request):
    """Newsletter signup view"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            try:
                form.send_confirmation_email()
                messages.success(request, 'Successfully subscribed! Check your email.')
            except Exception:
                messages.error(request, 'Subscription successful, but email failed to send.')
            return redirect('home')
        else:
            messages.error(request, 'You are already subscribed.')
    
    return render(request, 'home/newsletter.html', {'form': NewsletterForm()})

def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            try:
                form.send_confirmation_email()
                messages.success(request, 'Your message has been sent successfully!')
            except Exception:
                messages.error(request, 'Failed to send confirmation email.')
            return redirect('contact')
        else:
            messages.error(request, 'Failed to send your message. Please try again.')

    return render(request, 'home/contact.html', {'form': ContactForm()})

def who_we_are(request):
    return render(request, 'home/who_we_are.html')

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def serve_sitemap(request):
    """
    Serve the sitemap.xml file
    """
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    if os.path.exists(sitemap_path):
        with open(sitemap_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/xml')
    return HttpResponse('Sitemap not found', status=404)
