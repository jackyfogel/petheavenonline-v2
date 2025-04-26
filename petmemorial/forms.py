from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from .models import PetMemorial
import re
from datetime import datetime

class MultipleImageInput(Widget):
    template_name = 'django/forms/widgets/file.html'
    
    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['multiple'] = True
        attrs['class'] = 'form-control'
        attrs['accept'] = 'image/*'
        attrs['type'] = 'file'
        attrs['name'] = name
        final_attrs = self.build_attrs(attrs)
        return mark_safe(f'<input{forms.utils.flatatt(final_attrs)}>')

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label=''
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label=''
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label=''
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        labels = {
            'email': '',
            'password1': '',
            'password2': ''
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def generate_unique_username(self, email):
        # Extract the part before @ and remove special characters
        base_username = re.sub(r'[^a-zA-Z0-9]', '', email.split('@')[0])
        
        # If base_username is empty after cleaning, use 'user' as base
        if not base_username:
            base_username = 'user'
        
        # Truncate to ensure room for numbers if needed (max length 150)
        base_username = base_username[:30]
        
        username = base_username
        counter = 1
        
        # Keep trying until we find a unique username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
            # If we somehow exceed username max length, truncate base and try again
            if len(username) > 150:
                base_username = base_username[:(150 - len(str(counter)) - 1)]
                username = f"{base_username}{counter}"
        
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        
        # Generate and set unique username
        username = self.generate_unique_username(email)
        user.username = username
        user.email = email
        
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label=''
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label=''
    )

    error_messages = {
        'invalid_login': 'Invalid email or password. Please try again.',
        'inactive': 'This account is inactive.',
    }

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            # Find user by email
            try:
                user = User.objects.get(email=email)
                # Use the username (email) for authentication
                self.user_cache = authenticate(
                    self.request, 
                    username=user.username, 
                    password=password
                )
                if self.user_cache is None:
                    raise self.get_invalid_login_error()
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                raise self.get_invalid_login_error()

        return self.cleaned_data 

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MemorialSubmissionForm(forms.ModelForm):
    species = forms.ChoiceField(
        choices=[('', 'Select your pet\'s species')] + PetMemorial.SPECIES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    year_of_birth = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Year of birth',
            'min': 1900,
            'max': datetime.now().year
        })
    )
    year_of_death = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Year of death',
            'min': 1900,
            'max': datetime.now().year
        })
    )
    images = MultipleFileField(
        required=False,
        help_text='You can select multiple images (max 10 images)',
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = PetMemorial
        fields = [
            'pet_name', 'species', 'breed', 'year_of_birth', 'year_of_death',
            'tribute_quote', 'dominant_traits', 'about_pet', 'photo',
            'video_url', 'owner_display_name'
        ]
        widgets = {
            'pet_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your pet\'s name'
            }),
            'species': forms.Select(attrs={
                'class': 'form-control'
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Breed (optional)'
            }),
            'tribute_quote': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'A special quote or message for your pet'
            }),
            'dominant_traits': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Personality traits (optional)'
            }),
            'about_pet': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your pet\'s story',
                'rows': 5
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube or Vimeo URL (optional)'
            }),
            'owner_display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'How you want your name displayed (optional)'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        year_of_birth = cleaned_data.get('year_of_birth')
        year_of_death = cleaned_data.get('year_of_death')
        current_year = datetime.now().year

        if year_of_birth:
            if year_of_birth < 1900:
                raise ValidationError({
                    'year_of_birth': 'Year of birth cannot be earlier than 1900.'
                })
            if year_of_birth > current_year:
                raise ValidationError({
                    'year_of_birth': f'Year of birth cannot be later than {current_year}.'
                })

        if year_of_death:
            if year_of_death < 1900:
                raise ValidationError({
                    'year_of_death': 'Year of death cannot be earlier than 1900.'
                })
            if year_of_death > current_year:
                raise ValidationError({
                    'year_of_death': f'Year of death cannot be later than {current_year}.'
                })

        if year_of_birth and year_of_death:
            if year_of_death < year_of_birth:
                raise ValidationError({
                    'year_of_death': 'Year of death cannot be earlier than year of birth.'
                })

        # Validate gallery images
        gallery_images = self.files.getlist('images')
        if len(gallery_images) > 10:
            raise ValidationError({
                'images': 'You can upload a maximum of 10 gallery images.'
            })

        return cleaned_data 