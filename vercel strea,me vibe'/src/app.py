from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import re


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Video Downloader API is running!"

    @app.route('/download', methods=['POST'])
    def download():
        try:
            url = request.form.get('url')
            if not url:
                return jsonify({'error': 'Please provide a URL'}), 400

            # Your existing download logic here
            # ...

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app

app = Flask(__name__)

def sanitize_filename(filename):
    # Remove invalid characters from filename
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def get_video_formats(url):
    """Get available formats for the video"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'nocheckcertificate': True,
        'no_cache_dir': True,
        'cookiefile': 'cookies.txt'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")
            return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form.get('url')
        if not url:
            return jsonify({'error': 'Please provide a URL'}), 400

        # Create downloads directory if it doesn't exist
        download_path = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_path, exist_ok=True)

        # First, try to get video information
        info = get_video_formats(url)
        if not info:
            return jsonify({'error': 'Could not fetch video information'}), 400

        # Configure yt-dlp options for direct streaming
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Simplified format selection
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'no_cache_dir': True,
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Get video info without downloading
                info = ydl.extract_info(url, download=False)
                if not info:
                    return jsonify({'error': 'Failed to get video info'}), 400

                video_title = info.get('title', 'video')
                video_url = info.get('url')
                
                if not video_url:
                    return jsonify({'error': 'Could not get video URL'}), 400

                # Return the direct video URL for client-side download
                return jsonify({
                    'success': True,
                    'title': video_title,
                    'url': video_url
                })

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                if 'Sign in' in error_msg:
                    return jsonify({'error': 'This video requires authentication. Please try a different video.'}), 403
                elif 'This video is unavailable' in error_msg:
                    return jsonify({'error': 'This video is unavailable. It might be private or deleted.'}), 404
                elif 'Video unavailable' in error_msg:
                    return jsonify({'error': 'Video is unavailable. Please check if the video exists and is public.'}), 404
                else:
                    return jsonify({'error': f'Download failed: {error_msg}'}), 400

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    port = os.environ.get('PORT', 3000)
    app.run(host='0.0.0.0', port=port, debug=False)
