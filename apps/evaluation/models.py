from mongoengine import Document, StringField, IntField, ListField

# Create your models here.
class EvaluationResults(Document):
    file_name = StringField(required=True)
    results = ListField()
    date = StringField(required=True)
    agent = StringField(required=True)
    call_type = StringField(required=True)

    def __str__(self):
        return f"Evaluation for {self.file_name}"

class Questions(Document):
    text = StringField(required=True)
    keywords = ListField(StringField(), required=True)
    correct_score = IntField(required=True)
    incorrect_score = IntField(required=True)

    def __str__(self):
        return self.text