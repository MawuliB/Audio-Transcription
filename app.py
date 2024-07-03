from flask import Flask, request, render_template, redirect, url_for, session
import os
from pydub import AudioSegment
from flask_session import Session
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

"""
ffmpeg_path = r'C:\ffmpeg-7.0.1-essentials_build\bin' # Path to the ffmpeg executable
os.environ["PATH"] += os.pathsep + ffmpeg_path
""" # Uncomment this block if you are using Windows and ffmpeg can't be found

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def convert_to_wav(file_path):
    # AudioSegment.converter = ffmpeg_path + r'\ffmpeg.exe' # Path to the ffmpeg executable # Uncomment this line if you are using Windows and ffmpeg can't be found
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    audio = AudioSegment.from_file(file_path)
    wav_path = file_path.rsplit('.', 1)[0] + '.wav'
    audio.export(wav_path, format='wav')
    return wav_path

@app.route('/')
def index():
    transcription = session.pop('transcription', None)
    return render_template('index.html', transcription=transcription)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        session['file_path'] = file_path
        return redirect(url_for('transcribe'))

@app.route('/transcribe', methods=['GET'])
def transcribe():
    file_path = session.pop('file_path', None)
    if not file_path or not os.path.exists(file_path):
        return redirect(url_for('index'))
    
    wav_path = convert_to_wav(file_path)
    
    # Set the AssemblyAI API key
    aai.api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    transcriber = aai.Transcriber()
    transcription = transcriber.transcribe(wav_path)

    session['transcription'] = transcription.text
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
