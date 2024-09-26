from flask import Flask, request, send_file, render_template
from pytube import YouTube
import os
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path='downloads')
        
        # Convert to MP3
        base, ext = os.path.splitext(out_file)
        mp3_file = base + '.mp3'
        AudioSegment.from_file(out_file).export(mp3_file, format='mp3')
        
        # Remove the original file
        os.remove(out_file)
        
        return send_file(mp3_file, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True, port=49152)  # Specify the port here
