from flask import Flask, request, render_template, send_file
import os
import yt_dlp

app = Flask(__name__)

def download_youtube_video_as_mp3(video_url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Return the path of the downloaded file
    return os.path.join(output_path, f"{ydl.prepare_filename(ydl.extract_info(video_url))}.mp3")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        try:
            mp3_file = download_youtube_video_as_mp3(video_url)
            return send_file(mp3_file, as_attachment=True)
        except Exception as e:
            return f'An error occurred: {e}'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
