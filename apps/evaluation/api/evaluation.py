import pandas as pd
import torch
from transformers import BertTokenizer, BertModel
from ..models import Questions, EvaluationResults
from ...transcription.models import Transcriptions

# Inicializar el tokenizador y modelo BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def load_questions():
    print("load_questions")
    questions = Questions.objects.all()
    print(f"Question: {questions}")
    questions_df = pd.DataFrame([{
            'text': question.text,
            'keywords': question.keywords,
            'correct_score': question.correct_score,
            'incorrect_score': question.incorrect_score
        } for question in questions])
    return questions_df

def obtain_score(conversation_text, question_dataset):
    print("obtain_score")
    total_score = 0
    results = []

    for index, row in question_dataset.iterrows():
        question = row['text']
        keywords = row['keywords']
        correct_score = row['correct_score']
        incorrect_score = row['incorrect_score']

        if any(keyword.lower() in conversation_text.lower() for keyword in keywords):
            total_score += correct_score
            results.append({"Pregunta": question, "Calificación": correct_score})
        else:
            total_score += incorrect_score
            results.append({"Pregunta": question, "Calificación": incorrect_score})

    return total_score, pd.DataFrame(results)

def analyze_conversation(conversation, questions):
    print("analyze_conversation")
    texts = [transcription['text'] for transcription in conversation.transcriptions]
    conversation_text = ' '.join(texts)
    
    # Tokenizar el texto de la conversación
    tokens = tokenizer(conversation_text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**tokens)

    total_score, results = obtain_score(conversation_text, questions)

    result_eval = EvaluationResults(
        file_name=conversation.file_name,
        results=results.to_dict(orient='records'),
        date=conversation.date,
        agent=conversation.agent,
        call_type=conversation.call_type
    )
    result_eval.save()
    
    # update_review(conversation)
    print(f"Puntuación total para la conversación {conversation.id}: {total_score}")
    print(results)

def update_review(conversation):
    print("Actualizando revisión para id:", conversation.id)
    conversation.is_revised = 1
    conversation.save()

def process_conversations():
    conversations = Transcriptions.objects(is_revised=0)
    print(f"Encontradas {conversations.count()} conversaciones no revisadas.")
    questions = load_questions()
    print(f"questions {questions}")
    for conversation in conversations:
        analyze_conversation(conversation, questions)
