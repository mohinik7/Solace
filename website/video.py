from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
import json

video = Blueprint('video', __name__)

# Configuration for videos
VIDEO_FOLDER = 'videos'
ALLOWED_EXTENSIONS = {'mp4'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper to get the current video filename
def get_current_video():
    config_path = os.path.join(current_app.static_folder, 'videos', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('current_video')
    return None

# Route to upload and manage videos
@video.route('/admin/video', methods=['GET', 'POST'])
@login_required
def video_upload():
    if not current_user.is_admin:
        flash('Only administrators can access this page.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'video' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['video']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Ensure the videos directory exists
            videos_path = os.path.join(current_app.static_folder, VIDEO_FOLDER)
            if not os.path.exists(videos_path):
                os.makedirs(videos_path)
            
            # Save the file
            file_path = os.path.join(videos_path, filename)
            file.save(file_path)
            
            # Update the config to use this video
            config_path = os.path.join(videos_path, 'config.json')
            config = {'current_video': filename}
            
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('video.video_upload'))
    
    # Get current video if it exists
    current_video = get_current_video()
    
    return render_template('video_upload.html', current_video=current_video)

# Route to remove the current video
@video.route('/admin/video/remove', methods=['POST'])
@login_required
def remove_video():
    if not current_user.is_admin:
        flash('Only administrators can access this page.', 'danger')
        return redirect(url_for('index'))
    
    current_video = get_current_video()
    
    if current_video:
        # Delete the video file
        video_path = os.path.join(current_app.static_folder, VIDEO_FOLDER, current_video)
        if os.path.exists(video_path):
            os.remove(video_path)
        
        # Update config
        config_path = os.path.join(current_app.static_folder, VIDEO_FOLDER, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'w') as f:
                json.dump({'current_video': None}, f)
        
        flash('Video removed successfully!', 'success')
    else:
        flash('No video to remove.', 'warning')
    
    return redirect(url_for('video.video_upload')) 