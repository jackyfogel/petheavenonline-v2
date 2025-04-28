from django.contrib import admin
from .models import PetMemorial, MemorialImage, CandleMessage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


# Inline gallery image uploader inside PetMemorial edit form
class PetMemorialGalleryImageInline(admin.TabularInline):
    model = MemorialImage
    extra = 1  # Show 1 empty image slot by default

class CandleMessageInline(admin.TabularInline):
    model = CandleMessage
    extra = 1  # Show 1 empty candle row by default


# Admin for PetMemorial (main model)
@admin.register(PetMemorial)
class PetMemorialAdmin(admin.ModelAdmin):
    list_display = ("pet_name", "species", "user", "year_of_birth", "year_of_death")
    search_fields = ("pet_name", "user__username", "species", "breed")
    list_filter = ("species", "year_of_death")
    ordering = ("-year_of_death",)
    inlines = [PetMemorialGalleryImageInline, CandleMessageInline]

    def save_model(self, request, obj, form, change):
        # Check if status is being changed from pending to published
        if change:
            old_obj = PetMemorial.objects.get(pk=obj.pk)
            if old_obj.status == 'pending' and obj.status == 'published':
                # Send email to user
                memorial_url = request.build_absolute_uri(reverse('memorial', args=[obj.slug]))
                context = {
                    'memorial': obj,
                    'user': obj.user,
                    'memorial_url': memorial_url,
                }
                html_message = render_to_string('petmemorial/email/memorial_published_notification.html', context)
                plain_message = strip_tags(html_message)
                send_mail(
                    subject=f"Your Memorial for {obj.pet_name} is Now Live!",
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.user.email],
                    fail_silently=False,
                )
        super().save_model(request, obj, form, change)


# Admin for gallery images
@admin.register(MemorialImage)
class MemorialImageAdmin(admin.ModelAdmin):
    list_display = ("memorial", "caption", "order")
    search_fields = ("caption", "memorial__pet_name")
    list_filter = ("memorial",)
    ordering = ("memorial", "order")

# Register CandleMessage model
admin.site.register(CandleMessage)
