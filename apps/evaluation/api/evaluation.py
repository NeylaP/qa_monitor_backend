import pandas as pd
import torch
from transformers import BertTokenizer, BertModel
from ..models import Questions, EvaluationResults
from ...transcription.models import Transcriptions
from datetime import datetime

# Inicializar el tokenizador y modelo BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def load_questions():
    try:
        questions = Questions.objects.all()

        questions_df = pd.DataFrame([{
            'text': question.text,
            'keywords': question.keywords,
            'correct_score': question.correct_score,
            'incorrect_score': question.incorrect_score,
            'group': question.group['description'] if question.group else None
        } for question in questions])

        return questions_df

    except Exception as e:
        print(f"Error loading questions: {e}")
        return pd.DataFrame() 

def obtain_score(conversation_text, question_dataset):
    total_score = 0
    group_results = {}
    results = []

    for index, row in question_dataset.iterrows():
        question = row['text']
        keywords = row['keywords']
        correct_score = row['correct_score']
        incorrect_score = row['incorrect_score']
        group = row['group']

        is_correct = any(keyword.lower() in conversation_text.lower() for keyword in keywords)

        if group:
            if group not in group_results:
                group_results[group] = {
                    "scores": [],
                    "group_description": group,
                    "questions": []
                }

            group_results[group]["scores"].append(correct_score if is_correct else incorrect_score)
            group_results[group]["questions"].append({
                "question": question,
                "qualification": correct_score if is_correct else incorrect_score
            })
        else:
            total_score += correct_score if is_correct else incorrect_score
            results.append({
                "question": question,
                "qualification": correct_score if is_correct else incorrect_score
            })

    for group, result in group_results.items():
        lowest_score = min(result["scores"])
        total_score += lowest_score
        
        results.append({
            "question": result["group_description"],
            "qualification": lowest_score
        })

    return total_score, pd.DataFrame(results)


def analyze_conversation(conversation, questions):
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
        date= datetime.strptime(conversation.date, '%d-%m-%Y'),
        agent=conversation.agent,
        call_type=conversation.call_type
    )
    result_eval.save()

    update_review(conversation)

def update_review(conversation):
    conversation.is_revised = 1
    conversation.save()

def process_conversations():
    conversations = Transcriptions.objects(is_revised=0)
    questions = load_questions()
    for conversation in conversations:
        analyze_conversation(conversation, questions)
