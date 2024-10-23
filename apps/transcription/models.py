from mongoengine import Document, StringField, IntField, ListField

# Create your models here.
class Transcriptions(Document):
    file_name = StringField(required=True)
    date = StringField(required=True)
    agent = StringField(required=True)
    call_type = StringField(required=True)
    is_revised = IntField(default=0)
    transcriptions = ListField()

    def __str__(self):
        return self.file_name