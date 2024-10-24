from mongoengine import Document, StringField, IntField, ListField, DateTimeField
from django.utils import timezone

# Create your models here.
class Transcriptions(Document):
    file_name = StringField(required=True)
    date = StringField(required=True)
    agent = StringField(required=True)
    call_type = StringField(required=True)
    is_revised = IntField(default=0)
    transcriptions = ListField()
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file_name