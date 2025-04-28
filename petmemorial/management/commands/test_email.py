from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Send a test email to verify email configuration.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(f'Current ADMIN_EMAIL: {settings.ADMIN_EMAIL}'))
        try:
            send_mail(
                subject='Test Email from Pet Heaven',
                message='This is a test email to verify your Django email configuration.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {settings.ADMIN_EMAIL}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {e}')) 