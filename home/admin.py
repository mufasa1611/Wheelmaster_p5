from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
from .models import NewsletterSubscriber, Newsletter, ContactMessage, EmailDeliveryLog
from django.conf import settings

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created', 'sent_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('created', 'sent_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('name', 'email', 'message', 'created_at')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'active', 'created')
    search_fields = ('name', 'email')
    list_filter = ('active',)
    actions = ['send_selected_newsletter']

    def send_selected_newsletter(self, request, queryset):
        newsletters = Newsletter.objects.all()
        if not newsletters:
            self.message_user(request, "No newsletters available to send")
            return

        latest_newsletter = newsletters.latest('created')
        success_count = 0

        for subscriber in queryset:
            if subscriber.active:
                personalized_message = (
                    f"Dear {subscriber.name},\n\n"  
                    f"{latest_newsletter.content}\n\n"
                    f"Best regards,\nThe Team"
                )
                try:
                    send_mail(
                        subject=latest_newsletter.subject,
                        message=personalized_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=False,
                    )
                    success_count += 1
                    EmailDeliveryLog.objects.create(
                        newsletter=latest_newsletter,
                        subscriber=subscriber,
                        status='SENT'
                    )
                except Exception as e:
                    EmailDeliveryLog.objects.create(
                        newsletter=latest_newsletter,
                        subscriber=subscriber,
                        status='FAILED',
                        error_message=str(e)
                    )

        self.message_user(
            request, 
            f"Newsletter sent successfully to {success_count} recipients: {', '.join(subscriber.name or subscriber.email for subscriber in queryset if subscriber.active)}"
        )

    send_selected_newsletter.short_description = "Send newsletter to selected subscribers"
@admin.register(EmailDeliveryLog)
class EmailDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('newsletter', 'subscriber', 'sent_at', 'status')
    list_filter = ('status', 'sent_at')
    search_fields = ('subscriber__email', 'newsletter__subject')
    readonly_fields = ('newsletter', 'subscriber', 'sent_at', 'status')