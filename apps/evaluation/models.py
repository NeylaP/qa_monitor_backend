from mongoengine import Document, StringField, IntField, ListField, DateTimeField
from django.utils import timezone
# Create your models here.
class EvaluationResults(Document):
    file_name = StringField(required=True)
    results = ListField()
    date = DateTimeField(required=True)
    agent = StringField(required=True)
    call_type = StringField(required=True)
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Evaluation for {self.file_name}"

class GroupQuestion(Document):
    description = StringField(required=True)
class Questions(Document):
    text = StringField(required=True)
    keywords = ListField(StringField(), required=True)
    correct_score = IntField(required=True)
    incorrect_score = IntField(required=True)
    group = ListField(StringField(), required=True) 
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    def __str__(self):
        return self.text
