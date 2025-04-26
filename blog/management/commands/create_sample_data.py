from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Category, BlogPost
from petmemorial.models import PetMemorial
import datetime

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            email='test@example.com'
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Create blog category
        category, _ = Category.objects.get_or_create(name='Pet Care Tips')

        # Create a sample blog post
        post = BlogPost.objects.create(
            title='How to Remember Your Pet',
            content='''
            <h2>Creating Lasting Memories of Your Beloved Pet</h2>
            <p>Losing a pet is never easy. Here are some meaningful ways to honor their memory:</p>
            <ul>
                <li>Create a photo album or scrapbook</li>
                <li>Write down your favorite memories</li>
                <li>Plant a memorial garden</li>
                <li>Commission a pet portrait</li>
                <li>Create a memorial shadow box</li>
            </ul>
            <p>Remember, it's okay to grieve and take time to heal. Your pet will always hold a special place in your heart.</p>
            ''',
            category=category,
            status='published',
            published_at=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f'Created blog post: {post.title}'))

        # Create a sample memorial
        memorial = PetMemorial.objects.create(
            pet_name='Max',
            year_of_birth=2010,
            year_of_death=2023,
            tribute_quote='Forever in our hearts, the most loyal friend we could ask for.',
            user=user,
            species='dog',
            breed='Golden Retriever',
            dominant_traits='Loving, Playful, Gentle',
            about_pet='''
            Max was more than just a pet; he was family. His golden fur and warm brown eyes brought joy to everyone he met.
            He loved playing fetch in the park, swimming in the lake, and cuddling on the couch during movie nights.
            Though he's no longer with us physically, his pawprints will forever remain on our hearts.
            '''
        )
        self.stdout.write(self.style.SUCCESS(f'Created memorial for: {memorial.pet_name}')) 