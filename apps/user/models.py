from mongoengine import Document, StringField, DateTimeField, BooleanField
from django.utils import timezone
# Create your models here.

class CallTaker(Document):
    first_name = StringField(required=True, max_length=50)
    last_name = StringField(required=False, max_length=50)
    code = StringField(required=True, max_length=20)
    area = StringField(required=True, max_length=20)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.updated_at = timezone.now()
        return super(CallTaker, self).save(*args, **kwargs)