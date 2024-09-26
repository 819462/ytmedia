from flask import Flask, request, send_file, render_template
from pytube import YouTube
import os
from pydub import AudioSegment
import socket

app = Flask(__name__)

def find_open_port(start_port=5000, end_port=65535):
    """Find an open port in the specified range."""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('0.0.0.0', port)) != 0:  # Port is open
                return port
    return None  # No open port found

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')  # Use get to avoid KeyError
    if not url:
        return "Error: No URL provided.", 400
    
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        if not video:
            return "Error: No audio streams available.", 400
        
        out_file = video.download(output_path='downloads')
        
        # Convert to MP3
        base, ext = os.path.splitext(out_file)
        mp3_file = base + '.mp3'
        AudioSegment.from_file(out_file).export(mp3_file, format='mp3')
        
        # Remove the original file
        os.remove(out_file)
        
        return send_file(mp3_file, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 400

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    open_port = find_open_port(5000, 65535)  # Scan for open ports starting from 5000
    if open_port:
        print(f"Starting Flask app on port {open_port}")
        app.run(debug=True, host='0.0.0.0', port=open_port)  # Use the found open port
    else:
        print("No open ports found.")
