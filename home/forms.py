from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import NewsletterSubscriber, ContactMessage

class NewsletterForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = NewsletterSubscriber
        fields = ['name', 'email']

  
    def send_confirmation_email(self):
        send_mail(
            subject="Newsletter Subscription Confirmation",
            message=f"Dear {self.cleaned_data['name']},\n\nThank you for subscribing to our newsletter! Stay tuned for our latest updates.\n\nBest regards,\nThe Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.cleaned_data['email']],
            fail_silently=False, 
        )

class ContactForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your message here',
            'rows': 4
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']

    def send_confirmation_email(self):
        send_mail(
            subject="Thank you for contacting us!",
            message=f"Dear {self.cleaned_data['name']},\n\nThank you for reaching out. We have received your message and will get back to you soon.\n\nBest regards,\nThe Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.cleaned_data['email']],
            fail_silently=False, 
        )
