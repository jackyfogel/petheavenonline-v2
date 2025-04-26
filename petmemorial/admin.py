from django.contrib import admin
from .models import PetMemorial, MemorialImage, CandleMessage


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


# Admin for gallery images
@admin.register(MemorialImage)
class MemorialImageAdmin(admin.ModelAdmin):
    list_display = ("memorial", "caption", "order")
    search_fields = ("caption", "memorial__pet_name")
    list_filter = ("memorial",)
    ordering = ("memorial", "order")

# Register CandleMessage model
admin.site.register(CandleMessage)
