from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import PetMemorial, MemorialImage
from .forms import RegisterForm, EmailAuthenticationForm, MemorialSubmissionForm
import os
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.conf import settings
import logging
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.template.loaders.app_directories import get_app_template_dirs

logger = logging.getLogger(__name__)

# Create your views here.

def home(request):
    return render(request, 'petmemorial/index.html')

def memorial_list(request):
    memorials = PetMemorial.objects.all().order_by('-year_of_death')
    return render(request, 'petmemorial/memorial_list.html', {'memorials': memorials})

def memorial(request, slug):
    p = get_object_or_404(PetMemorial, slug=slug)
    return render(request, 'petmemorial/memorial.html', {'p': p})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Prepare email
            html_message = render_to_string('petmemorial/email/welcome.html', {
                'user': user,
                'site_url': request.build_absolute_uri('/')
            })
            plain_message = strip_tags(html_message)
            # Send welcome email
            try:
                send_mail(
                    subject='Welcome to Pet Heaven 🐾',
                    message=plain_message,
                    html_message=html_message,
                    from_email=os.getenv('EMAIL_HOST_USER'),
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.warning(f'Account created for {user.email} but welcome email failed: {str(e)}')
            # Clear any pending messages
            messages.get_messages(request)
            # Redirect to success page (do NOT log in the user)
            return redirect('registration_success')
    else:
        form = RegisterForm()
    return render(request, 'petmemorial/register.html', {'form': form})

def registration_success(request):
    return render(request, 'petmemorial/registration_success.html')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

@login_required
def submit_memorial(request):
    if request.method == 'POST':
        form = MemorialSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            memorial = form.save(commit=False)
            memorial.user = request.user
            memorial.status = 'pending'
            memorial.save()
            
            # Handle gallery images
            images = request.FILES.getlist('gallery_images')
            for image in images:
                MemorialImage.objects.create(memorial=memorial, image=image)
            
            # Prepare email context
            context = {
                'memorial': memorial,
                'user': request.user,
                'pet_name': memorial.pet_name,
                'species': memorial.species,
                'breed': memorial.breed,
                'submission_date': memorial.created_at.strftime('%B %d, %Y'),
                'site_url': request.build_absolute_uri('/'),
            }
            
            try:
                logger.error(f"Starting email process for memorial {memorial.pet_name}")
                logger.error(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
                logger.error(f"Admin email: {settings.ADMIN_EMAIL}")
                
                # Try both template locations
                template_paths = [
                    'petmemorial/email/memorial_submission_notification.html',
                    'email/memorial_submission_notification.html',
                ]
                
                html_message = None
                for template_path in template_paths:
                    try:
                        html_message = render_to_string(template_path, context)
                        logger.error(f"Successfully rendered template: {template_path}")
                        break
                    except Exception as template_error:
                        logger.error(f"Failed to render template {template_path}: {str(template_error)}")
                        continue
                
                if html_message is None:
                    raise Exception("Could not find template in any location")
                
                plain_message = strip_tags(html_message)
                
                # Send email to admin
                logger.error("Attempting to send admin notification email...")
                send_mail(
                    subject=f'New Memorial Submission: {memorial.pet_name} ({memorial.species})',
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                logger.error("Admin notification email sent successfully")

                # Send confirmation email to user
                logger.error(f"Attempting to send confirmation email to {request.user.email}...")
                user_context = {
                    'memorial': memorial,
                    'user': request.user,
                    'pet_name': memorial.pet_name,
                    'species': memorial.species,
                    'breed': memorial.breed,
                    'submission_date': memorial.created_at.strftime('%B %d, %Y'),
                    'site_url': request.build_absolute_uri('/'),
                }
                user_html_message = render_to_string('petmemorial/email/memorial_submission_confirmation.html', user_context)
                user_plain_message = strip_tags(user_html_message)
                
                send_mail(
                    subject=f'Memorial Submission Received: {memorial.pet_name}',
                    message=user_plain_message,
                    html_message=user_html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                logger.error("User confirmation email sent successfully")

                # Redirect to a new success page
                return redirect('memorial_submission_success')
            except Exception as e:
                logger.error(f'Memorial submission email error: {str(e)}')
                logger.error(f'Email settings - HOST: {settings.EMAIL_HOST}, PORT: {settings.EMAIL_PORT}, TLS: {settings.EMAIL_USE_TLS}')
                logger.error(f'From email: {settings.EMAIL_HOST_USER}, To admin: {settings.ADMIN_EMAIL}')
                # Still redirect to success even if email fails
                return redirect('memorial_submission_success')
    else:
        form = MemorialSubmissionForm()
    
    return render(request, 'petmemorial/submit_memorial.html', {'form': form})

def memorial_submission_success(request):
    return render(request, 'petmemorial/memorial_submission_success.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailAuthenticationForm

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

