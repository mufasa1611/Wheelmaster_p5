from django.db import models
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, default='')
    email = models.EmailField(unique=True)
    created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.name} - {self.email}" if self.name else self.email

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'


class Newsletter(models.Model):
    subject = models.CharField(max_length=200, default='')
    content = models.TextField(default='')
    created = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject



class EmailDeliveryLog(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ], default='SENT')
    error_message = models.TextField(blank=True, null=True, default='')

    class Meta:
        verbose_name = 'Email Delivery Log'
        verbose_name_plural = 'Email Delivery Logs'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
