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
            html_message = render_to_string('petmemorial/email/welcome.html', {'user': user})
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
                messages.success(request, 'Registration successful! Please check your email for a welcome message.')
            except Exception as e:
                messages.warning(request, 'Account created successfully, but we could not send the welcome email. Please contact support if needed.')
            # Redirect to success page (do NOT log in the user)
            return redirect('registration_success')
        else:
            messages.error(request, 'Please correct the errors below.')
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
            memorial.status = 'pending'  # Set status to pending
            memorial.save()

            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for index, image in enumerate(gallery_images):
                MemorialImage.objects.create(
                    memorial=memorial,
                    image=image,
                    order=index
                )

            # Send email notification to admin
            context = {
                'memorial': memorial,
                'user': request.user,
                'request': request,
                'description_preview': memorial.about_pet[:200] + '...' if len(memorial.about_pet) > 200 else memorial.about_pet,
                'pet_name': memorial.pet_name,
                'year_of_death': memorial.year_of_death,
                'species': memorial.species,
                'breed': memorial.breed,
                'submission_date': memorial.created_at.strftime('%B %d, %Y'),
            }
            html_message = render_to_string('petmemorial/email/new_memorial_notification.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                # Send email to admin
                send_mail(
                    subject=f'New Memorial Submission: {memorial.pet_name} ({memorial.species})',
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=False,
                )

                # Send confirmation email to user
                user_context = {
                    'memorial': memorial,
                    'user': request.user,
                    'pet_name': memorial.pet_name,
                    'species': memorial.species,
                    'breed': memorial.breed,
                    'submission_date': memorial.created_at.strftime('%B %d, %Y'),
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

                # Redirect to a new success page
                return redirect('memorial_submission_success')
            except Exception as e:
                messages.warning(
                    request, 
                    'Your memorial was submitted successfully, but we encountered an issue notifying our review team. '
                    'Rest assured, they will still review your submission shortly.'
                )
                return redirect('memorial_list')
    else:
        form = MemorialSubmissionForm()
    
    return render(request, 'petmemorial/submit_memorial.html', {'form': form})

def memorial_submission_success(request):
    return render(request, 'petmemorial/memorial_submission_success.html')

