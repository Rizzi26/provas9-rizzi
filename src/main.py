from flask import Flask, request, render_template
import cv2
import tempfile

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['POST'])
def input():
    if 'video' not in request.files:
        return "No video file", 400
    
    video_file = request.files['video']
    video_bytes = video_file.read()

    identify_faces(video_bytes)

    return "processando", 200

def identify_faces(data):
    classifier_frontal = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    classifier_profile = cv2.CascadeClassifier('haarcascade_profileface.xml')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(data)
        temp_video_path = temp_video.name

    video_capture = cv2.VideoCapture(temp_video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = 'output.mp4'
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(video_capture.get(3)), int(video_capture.get(4))))

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces_frontal = classifier_frontal.detectMultiScale(gray, 1.3, 5)
        faces_profile = classifier_profile.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces_frontal:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        for (x, y, w, h) in faces_profile:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        out.write(frame)

    video_capture.release()
    out.release()

    return output_path

if __name__ == '__main__':
    app.run(debug=True)
