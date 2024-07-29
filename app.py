from flask import Flask, request, render_template, redirect, url_for
from spellchecker import SpellChecker
import speech_recognition as sr
from pydub import AudioSegment
import io
import g4f  # Importing the g4f library

app = Flask(__name__)
spell = SpellChecker()

def check_grammar(text):
    try:
        response = g4f.Completion.create(
            model='gpt-4o',
            prompt=f'Correct the grammar and spelling of the following text:\n\n"{text}"\n\nCorrected Text:',
            max_tokens=1024,
            n=1,
            stop=["\n"]
        )
        # Debugging: Print the full response from g4f API
        print(f"g4f API response: {response}")
        
        if response and 'choices' in response and len(response['choices']) > 0:
            corrected_text = response['choices'][0]['text'].strip()
            return corrected_text
        else:
            print(f"Invalid response from g4f: {response}")
            return text
    except Exception as e:
        print(f"Error using g4f: {e}")
        return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    text = request.form['text']
    corrected_text = check_grammar(text)

    # Spell check the corrected text
    corrected_text = spell_check(corrected_text)

    return render_template('result.html', original_text=text, corrected_text=corrected_text)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        text = file.read().decode('utf-8')
        corrected_text = check_grammar(text)

        # Spell check
        corrected_text = spell_check(corrected_text)

        return render_template('result.html', original_text=text, corrected_text=corrected_text)
    return redirect(url_for('index'))

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    file = request.files['audio']
    if file:
        try:
            audio_data = file.read()
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            corrected_text = check_grammar(text)

            # Spell check
            corrected_text = spell_check(corrected_text)

            return render_template('result.html', original_text=text, corrected_text=corrected_text)
        except Exception as e:
            return render_template('result.html', original_text=f"Error processing audio file: {e}", corrected_text="")
    return redirect(url_for('index'))

def spell_check(text):
    misspelled = spell.unknown(text.split())
    for word in misspelled:
        correct_word = spell.correction(word)
        text = text.replace(word, correct_word)
    return text

if __name__ == '__main__':
    app.run(debug=True)