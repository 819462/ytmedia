import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import yt_dlp

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r') as file:
                self.wfile.write(file.read().encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            video_url = urllib.parse.parse_qs(post_data.decode())['video_url'][0]

            try:
                mp3_file = download_youtube_video_as_mp3(video_url)
                self.send_response(200)
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(mp3_file)}"')
                self.send_header('Content-type', 'audio/mpeg')
                self.end_headers()
                with open(mp3_file, 'rb') as file:
                    self.wfile.write(file.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'An error occurred: {e}'.encode())

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
        info_dict = ydl.extract_info(video_url, download=False)
        mp3_file = os.path.join(output_path, f"{info_dict['title']}.mp3")

    return mp3_file

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
