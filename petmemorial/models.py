from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import uuid
import os





def pet_memorial_profile_photo_path(instance, filename):
    memorial_id = instance.id or 'new'
    return f'users/{instance.user.id}/petmemorial/{memorial_id}/memorial-photo.webp'

def gallery_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'users/{instance.memorial.user.id}/petmemorial/{instance.memorial.id}/gallery/{uuid.uuid4()}{ext}'

# Create your models here.
class PetMemorial(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('published', 'Published'),
    ]

    SPECIES_CHOICES = [
        ("dog", "Dog"),
        ("cat", "Cat"),
        ("rabbit", "Rabbit"),
        ("hamster", "Hamster"),
        ("guinea_pig", "Guinea Pig"),
        ("ferret", "Ferret"),
        ("bird", "Bird"),
        ("parrot", "Parrot"),
        ("turtle", "Turtle"),
        ("lizard", "Lizard"),
        ("snake", "Snake"),
        ("fish", "Fish"),
        ("horse", "Horse"),
        ("goat", "Goat"),
        ("pig", "Pig"),
        ("chicken", "Chicken"),
        ("duck", "Duck"),
        ("frog", "Frog"),
        ("hedgehog", "Hedgehog"),
        ("other", "Other"),
    ]

    photo = models.ImageField(upload_to=pet_memorial_profile_photo_path, null=True, blank=True)
    pet_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    year_of_birth = models.IntegerField()
    year_of_death = models.IntegerField()
    tribute_quote = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.CharField(choices=SPECIES_CHOICES, max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    dominant_traits = models.CharField(max_length=100, blank=True, null=True)
    about_pet = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    owner_display_name = models.CharField(blank=True, null=True, max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        if self.year_of_death < self.year_of_birth:
            raise ValidationError('Year of death cannot be earlier than year of birth.')

    def save(self, *args, **kwargs):
        # First: Generate unique slug
        base_slug = slugify(self.pet_name)
        slug = base_slug
        num = 1
        while PetMemorial.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        self.slug = slug

        # Run validation
        self.clean()

        # If new object and has photo — save without image first to get ID
        if not self.pk and self.photo:
            temp_photo = self.photo  # save uploaded image temporarily
            self.photo = None  # clear it for now
            super().save(*args, **kwargs)  # save to get ID
            self.photo = temp_photo  # restore the image

        # Now convert to webp and save it with correct path
        if self.photo:
            img = Image.open(self.photo)
            img = img.convert('RGB')
            img.thumbnail((500, 500))

            buffer = BytesIO()
            img.save(buffer, format='WEBP')
            buffer.seek(0)

            self.photo.save('memorial-photo.webp', ContentFile(buffer.read()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pet_name}'s Memorial"

    def get_absolute_url(self):
        return f"/memorial/{self.slug}/"

class MemorialImage(models.Model):
    memorial = models.ForeignKey(PetMemorial, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to=gallery_image_upload_path)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            img = img.convert('RGB')
            img.thumbnail((1000, 1000))  # Resize if needed

            buffer = BytesIO()
            img.save(buffer, format='WEBP')
            buffer.seek(0)

            # Save as webp with random filename
            new_name = f"{uuid.uuid4()}.webp"
            self.image.save(new_name, ContentFile(buffer.read()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Gallery image for {self.memorial.pet_name}"

    class Meta:
        ordering = ['order']

class CandleMessage(models.Model):
    pet_memorial = models.ForeignKey(PetMemorial, on_delete=models.CASCADE, related_name='candles')
    name = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Candle by {self.name} for {self.pet_memorial.pet_name}"