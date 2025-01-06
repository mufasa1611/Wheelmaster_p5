from django.contrib import admin
from django.core.mail import send_mass_mail
from django.utils import timezone
from .models import NewsletterSubscriber, Newsletter

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created', 'sent_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('created', 'sent_at')
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for newsletter in queryset:
            subscribers = NewsletterSubscriber.objects.filter(active=True)
            if subscribers.exists():
                emails = [(
                    newsletter.subject,
                    newsletter.content.replace('[Subscriber\'s Name]', subscriber.name),
                    'noreply@wheel-master.alhanein.net',
                    [subscriber.email]
                ) for subscriber in subscribers]

                send_mass_mail(emails, fail_silently=False)
                newsletter.sent_at = timezone.now()
                newsletter.save()
                self.message_user(request, f"Newsletter sent to {len(emails)} subscribers")
            else:
                self.message_user(request, "No active subscribers found")

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('email', 'name')
