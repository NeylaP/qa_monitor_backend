import os
import whisper
import torch
import shutil
import pandas as pd
import numpy as np
import librosa
from pymongo import MongoClient
from difflib import get_close_matches
from pyannote.audio import Pipeline

DEFAULT_MODEL = "small"
client = MongoClient('mongodb://localhost:27017/')
db = client['qa_monitor']
collection = db['transcriptions']

class DiarizationPipeline:
    def __init__(self, model_name="pyannote/speaker-diarization-3.1", device="cpu"):
        self.device = torch.device(device) if isinstance(device, str) else device
        self.model = Pipeline.from_pretrained(model_name).to(self.device)

    def __call__(self, audio):
        audio_data = {
            'waveform': torch.from_numpy(audio[None, :]),
            'sample_rate': 16000
        }
        segments = self.model(audio_data)
        diarize_df = pd.DataFrame(segments.itertracks(yield_label=True), columns=['segment', 'label', 'speaker'])
        diarize_df['start'] = diarize_df['segment'].apply(lambda x: x.start)
        diarize_df['end'] = diarize_df['segment'].apply(lambda x: x.end)
        return diarize_df

def load_dictionary(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        words = {line.strip().lower() for line in f}
    return words

def load_replacement_dict(file_path):
    df = pd.read_csv(file_path)
    return dict(zip(df['original'], df['replacement']))

def correct_transcription(transcription, word_dict, replacement_dict):
    for phrase, replacement in replacement_dict.items():
        transcription = transcription.replace(phrase.lower(), str(replacement))

    corrected_text = []
    for word in transcription.split():
        if word_dict and word.lower() not in word_dict:
            close_match = get_close_matches(word.lower(), word_dict, n=1, cutoff=0.6)
            corrected_text.append(close_match[0] if close_match else word)
        else:
            corrected_text.append(word)

    return ' '.join(corrected_text)

def assign_word_speakers(diarize_df, transcript_result):
    for seg in transcript_result["segments"]:
        diarize_df['intersection'] = np.minimum(diarize_df['end'], seg['end']) - np.maximum(diarize_df['start'], seg['start'])
        dia_tmp = diarize_df[diarize_df['intersection'] > 0]
        if not dia_tmp.empty:
            speaker = dia_tmp.groupby("speaker")["intersection"].sum().idxmax()
            seg["speaker"] = speaker
    return transcript_result

def detect_initial_silence(audio_path):
    audio, sr = librosa.load(audio_path, sr=16000)
    energy = librosa.feature.rms(y=audio)[0]
    threshold = 0.01
    non_silent_indices = np.where(energy > threshold)[0]
    first_speech_time = librosa.frames_to_time(non_silent_indices[0], sr=sr, hop_length=512) if len(non_silent_indices) > 0 else 0
    return first_speech_time

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def generate_transcription_files(source_dir, target_dir, reviewed_dir, model_name=DEFAULT_MODEL, word_dict=None, replacement_dict=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Dispositivo:", device)
    whisper_model = whisper.load_model(model_name, device=device)
    diarization_model = DiarizationPipeline(device=device)

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(reviewed_dir, exist_ok=True)
    supported_extensions = ('.mp3', '.wav', '.m4a', '.aac', '.mp4', '.mov', '.avi', '.mkv', '.flac')
    
    for date_folder in os.listdir(source_dir):
        date_path = os.path.join(source_dir, date_folder)
        if not os.path.isdir(date_path):
            continue

        for agent_folder in os.listdir(date_path):
            agent_path = os.path.join(date_path, agent_folder)
            if not os.path.isdir(agent_path):
                continue

            for file_name in os.listdir(agent_path):
                if not file_name.lower().endswith(supported_extensions):
                    continue

                audio_path = os.path.join(agent_path, file_name)
                print(f"Transcribiendo: {file_name}")

                first_speech_time = detect_initial_silence(audio_path)
                transcription_result = whisper_model.transcribe(audio_path)
                print("Estoy aquiiii")
                print(word_dict)
                if word_dict or replacement_dict:
                    for segment in transcription_result['segments']:
                        segment['text'] = correct_transcription(segment['text'], word_dict, replacement_dict)

                df_transcription = pd.DataFrame(transcription_result['segments'])[['id', 'start', 'end', 'text']]
                df_transcription['start'] += first_speech_time
                df_transcription['end'] += first_speech_time

                audio, _ = librosa.load(audio_path, sr=16000)
                diarize_df = diarization_model(audio)
                transcript_with_speakers = assign_word_speakers(diarize_df, transcription_result)

                df_transcription['speaker'] = [seg.get('speaker', 'Unknown') for seg in transcript_with_speakers['segments']]
                df_transcription['duration'] = df_transcription['end'] - df_transcription['start']
                df_transcription['silence_after'] = df_transcription['start'].shift(-1) - df_transcription['end']
                df_transcription['silence_after'] = df_transcription['silence_after'].fillna(0).where(
                    df_transcription['silence_after'] >= 0, 0)

                df_transcription['start'] = df_transcription['start'].apply(format_time)
                df_transcription['end'] = df_transcription['end'].apply(format_time)
                df_transcription['duration'] = df_transcription['duration'].apply(format_time)
                df_transcription['silence_after'] = df_transcription['silence_after'].apply(format_time)

                output_file = os.path.join(target_dir, f"{os.path.splitext(file_name)[0]}_transcription.csv")
                df_transcription.to_csv(output_file, index=False, sep=';')
                print(f"Finalizada la transcripción: {file_name}")

                all_transcriptions = {
                    "file_name": file_name,
                    "transcriptions": df_transcription.to_dict(orient='records'),
                    "date": date_folder,
                    "agent": agent_folder,
                    "call_type": file_name.split('-')[1].strip().rsplit('.', 1)[0] if '-' in file_name else "Unknown",
                    "is_revised": 0
                }
                collection.insert_one(all_transcriptions)
                print(f"Guardado en MongoDB: {file_name}")

                reviewed_agent_path = os.path.join(reviewed_dir, date_folder, agent_folder)
                os.makedirs(reviewed_agent_path, exist_ok=True)
                shutil.move(audio_path, os.path.join(reviewed_agent_path, file_name))

            if not os.listdir(agent_path):
                os.rmdir(agent_path)
                print(f"Carpeta vacía eliminada: {agent_path}")

        if not os.listdir(date_path):
            os.rmdir(date_path)
            print(f"Carpeta vacía eliminada: {date_path}")