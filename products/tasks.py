from celery import shared_task
from django.core.management import call_command

@shared_task
def cleanup_expired_sessions():
    """
    Task to clean up expired sessions and release reserved stock.
    This task is scheduled to run every 15 minutes.
    """
    call_command('session_cleanup')
