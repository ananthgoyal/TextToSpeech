from datetime import datetime, timedelta
import os
import cmath
import pathlib
from flask import Flask, flash, request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import threading



global fileName
fileName = ""

app=Flask(__name__)

app.secret_key = "secret key"

path = os.getcwd()



# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')
OUTPUT_FOLDER = os.path.join(path, 'output')
CHUNKS_FOLDER = os.path.join(path, 'audio-chunks')

#schedule.every(2).minutes.do(lambda: "test")
# create a speech recognition object
r = sr.Recognizer()

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

if not os.path.isdir(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)

if not os.path.isdir(CHUNKS_FOLDER):
    os.mkdir(CHUNKS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['mp3'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_large_audio_transcription(global_filename):
    #schedule.run_pending()
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """

    for f in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, f))
    # open the audio file using pydub

    uploaded = True
    with open(OUTPUT_FOLDER + '/' + global_filename + '.txt', 'w') as f:
        print('Collecting Output ... ')
        print()
        print('Approx. Line by Line:')
        print()
        f.write('Collecting Output ... ')   
        f.write('\n')
        f.write('Approx. Line by Line:')
        f.write('\n')
        sound = AudioSegment.from_mp3(UPLOAD_FOLDER + '/' + global_filename)  
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
            # experiment with this value for your target audio file
            min_silence_len = 500,
            # adjust this per requirement
            silence_thresh = sound.dBFS-14,
            # keep the silence for 1 second, adjustable as well
            keep_silence=500,
        )
        folder_name = CHUNKS_FOLDER
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk 
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.mp3")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                # try converting it to text
                try:
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:   
                    print("Error:", str(e))
                    f.write("Error: " + str(e))
                    f.write('\n')
                else:
                    text = f"{text.capitalize()}. "
                    print("->", text)
                    f.write("-> " + text)
                    f.write('\n')
                    whole_text += text
            os.remove(os.path.join(CHUNKS_FOLDER, chunk_filename))


        # return the text for all chunks detected
        f.write('Condensed Output:')
        f.write('\n')
        f.write(whole_text)

        #remove file after conversion complete
        os.remove(os.path.join(UPLOAD_FOLDER, global_filename))
        #send_file(OUTPUT_FOLDER + '/' + path, as_attachment=True)
        #return whole_text

@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
        global global_filename
        # check if the post request has the file part       
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            global fileName
            fileName = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #global_filename = filename
            
            #get_large_audio_transcription(filename)
            threading.Thread(target=get_large_audio_transcription, args=(filename,)).start()
            return render_template('download.html')
        else:
            flash('Allowed file type(s) are .mp3. Please use an online audio file converter to mp3.')
            return redirect(request.url)

@app.route('/output', methods=['POST'])
def download():
    global fileName
    for file in os.listdir(OUTPUT_FOLDER):
        return send_file(OUTPUT_FOLDER + "/" + file, as_attachment=True)


if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 5001)