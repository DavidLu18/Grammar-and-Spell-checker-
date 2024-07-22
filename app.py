from flask import Flask, request, render_template
import language_tool_python
from spellchecker import SpellChecker

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')
spell = SpellChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    text = request.form['text']
    matches = tool.check(text)

    corrected_text = text
    for match in matches:
        from_pos = match.offset
        to_pos = match.offset + match.errorLength
        if match.replacements:
            corrected_text = corrected_text[:from_pos] + match.replacements[0] + corrected_text[to_pos:]

    # Spell check
    misspelled = spell.unknown(text.split())
    for word in misspelled:
        corrected_text = corrected_text.replace(word, spell.correction(word))

    return render_template('result.html', original_text=text, corrected_text=corrected_text, matches=matches)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        text = file.read().decode('utf-8')
        matches = tool.check(text)

        corrected_text = text
        for match in matches:
            from_pos = match.offset
            to_pos = match.offset + match.errorLength
            if match.replacements:
                corrected_text = corrected_text[:from_pos] + match.replacements[0] + corrected_text[to_pos:]

        # Spell check
        misspelled = spell.unknown(text.split())
        for word in misspelled:
            corrected_text = corrected_text.replace(word, spell.correction(word))

        return render_template('result.html', original_text=text, corrected_text=corrected_text, matches=matches)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
