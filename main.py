from flask import Flask, render_template, request, jsonify
import os
import threading
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from deep_translator import GoogleTranslator
from google.transliteration import transliterate_text

app = Flask(__name__)

# Language dictionary
language_codes = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Spanish": "es", "Chinese (Simplified)": "zh-CN",
    "Russian": "ru", "Japanese": "ja", "Korean": "ko", "German": "de", "French": "fr",
    "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Gujarati": "gu", "Punjabi": "pa"
}

keep_running = False

def recognize_and_translate(input_lang, output_lang):
    global keep_running
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak Now!\n")
        audio = r.listen(source)

        try:
            speech_text = r.recognize_google(audio)
            transliterated_text = transliterate_text(speech_text, lang_code=input_lang) if input_lang not in ('auto', 'en') else speech_text
            if speech_text.lower() in {'exit', 'stop'}:
                keep_running = False
                return {"recognized": "Stopped", "translated": "Stopped"}

            translated_text = GoogleTranslator(source=input_lang, target=output_lang).translate(text=transliterated_text)

            voice = gTTS(translated_text, lang=output_lang)
            voice.save('voice.mp3')
            playsound('voice.mp3')
            os.remove('voice.mp3')

            return {"recognized": transliterated_text, "translated": translated_text}

        except sr.UnknownValueError:
            return {"recognized": "Could not understand!", "translated": "N/A"}
        except sr.RequestError:
            return {"recognized": "Could not request from Google!", "translated": "N/A"}

@app.route('/')
def home():
    return render_template('index.html', languages=language_codes.keys())

@app.route('/translate', methods=['POST'])
def translate():
    global keep_running
    if not keep_running:
        keep_running = True
        data = request.json
        input_lang = language_codes.get(data['input_lang'], "auto")
        output_lang = language_codes.get(data['output_lang'], "en")
        result = recognize_and_translate(input_lang, output_lang)
        return jsonify(result)
    return jsonify({"recognized": "", "translated": ""})

@app.route('/stop', methods=['POST'])
def stop():
    global keep_running
    keep_running = False
    return jsonify({"message": "Translation stopped!"})

if __name__ == '__main__':
    app.run(debug=True)
