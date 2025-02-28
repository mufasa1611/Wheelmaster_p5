from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import transaction
from products.models import Product
from django.contrib.auth.models import User
from datetime import timedelta
from django.conf import settings

class Command(BaseCommand):
    help = 'Clean up expired sessions and release their reserved quantities'

    def handle(self, *args, **options):
        """
        Clean up expired sessions and release their reserved quantities.
        Different handling for anonymous and authenticated users.
        """
        try:
            # Get all expired sessions
            expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
            
            with transaction.atomic():
                corrupted_sessions = 0
                processed_sessions = 0
                
                for session in expired_sessions:
                    try:
                        # Get the bag from the session
                        session_data = session.get_decoded()
                        
                        # Check if this is an anonymous user session
                        is_anonymous = True
                        if '_auth_user_id' in session_data:
                            is_anonymous = False
                            
                            # For authenticated users, check session security timeout
                            if 'last_activity' in session_data:
                                last_activity = timezone.datetime.fromisoformat(session_data['last_activity'])
                                if timezone.now() - last_activity < timedelta(seconds=settings.SESSION_SECURITY_EXPIRE_AFTER):
                                    # Session not expired yet for authenticated user
                                    continue
                        else:
                            # For anonymous users, check anonymous session timeout
                            if 'last_activity' in session_data:
                                last_activity = timezone.datetime.fromisoformat(session_data['last_activity'])
                                if timezone.now() - last_activity < timedelta(seconds=settings.ANONYMOUS_SESSION_COOKIE_AGE):
                                    # Session not expired yet for anonymous user
                                    continue
                        
                        bag = session_data.get('bag', {})
                        
                        if not isinstance(bag, dict):
                            self.stdout.write(f"Skipping session {session.pk} - invalid bag format")
                            corrupted_sessions += 1
                            continue
                        
                        # Release reserved quantities for each product in the bag
                        for item_id, item_data in bag.items():
                            try:
                                product = Product.objects.get(pk=item_id)
                                
                                # Handle both sized and non-sized products
                                if isinstance(item_data, dict):
                                    # Product with sizes
                                    total_qty = sum(item_data.get('items_by_size', {}).values())
                                else:
                                    # Product without sizes
                                    total_qty = int(item_data) if str(item_data).isdigit() else 0
                                    
                                # Release the reserved quantity
                                if total_qty > 0:
                                    product.reserved_qty = max(0, product.reserved_qty - total_qty)
                                    product.save()
                                    self.stdout.write(
                                        f"Released {total_qty} units for product {product.name} "
                                        f"from {'anonymous' if is_anonymous else 'authenticated'} session"
                                    )
                            except Product.DoesNotExist:
                                self.stdout.write(f"Product {item_id} not found")
                                continue
                            except (ValueError, TypeError) as e:
                                self.stdout.write(f"Invalid quantity data for product {item_id}: {str(e)}")
                                continue
                                
                        processed_sessions += 1
                        # Delete the session after processing
                        session.delete()
                            
                    except Exception as e:
                        corrupted_sessions += 1
                        self.stdout.write(f"Error processing session {session.pk}: {str(e)}")
                        continue
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cleanup complete:\n"
                        f"- Processed {processed_sessions} sessions\n"
                        f"- Found {corrupted_sessions} corrupted sessions\n"
                    )
                )
                
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error cleaning up expired sessions: {str(e)}")
            )
