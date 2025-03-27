from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AnonymousUser

class AnonymousSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is available and is anonymous
        if hasattr(request, 'user') and isinstance(request.user, AnonymousUser):
            # Set session expiry to 1 hour for anonymous users
            request.session.set_expiry(settings.ANONYMOUS_SESSION_COOKIE_AGE)
            
            # Check if session is expired for anonymous users
            if 'last_activity' in request.session:
                last_activity = request.session['last_activity']
                # Convert string to datetime if needed
                if isinstance(last_activity, str):
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                
                # If more than 1 hour has passed since last activity
                if timezone.now() - last_activity > timedelta(seconds=settings.ANONYMOUS_SESSION_COOKIE_AGE):
                    # Clear the session
                    request.session.flush()
            
            # Update last activity time
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response
