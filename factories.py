# factories.py
import factory
from django.contrib.auth.models import User
from accounts.models import Profile
from teacher.models import Teacher
from student.models import Student
from video.models import Video
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    
    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if not create:
            return
        
        # Check if profile already exists
        if not hasattr(self, 'profile'):
            Profile.objects.create(user=self)

class TeacherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Teacher
    
    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: fake.name())
    username = factory.Sequence(lambda n: f'teacher{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    nos = 100

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student
    
    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: fake.name())
    username = factory.Sequence(lambda n: f'student{n}')

class VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Video
    
    title = factory.LazyAttribute(lambda _: fake.sentence())
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    teacher = factory.SubFactory(TeacherFactory)
    youtube_id = factory.Sequence(lambda n: f'abc123{n:03d}')
    subject = factory.LazyAttribute(lambda _: fake.word())
    duration = '10:30'
    like_count = 0