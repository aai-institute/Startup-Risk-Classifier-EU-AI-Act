from flask import Flask, render_template, request, Response, send_file
import os
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

def generate_output(process):
    """Generator function to stream output from main.py in real time."""
    # Read each line from the subprocess (which must be unbuffered)
    for line in iter(process.stdout.readline, ''):
        if line:
            # Each printed line is sent immediately (with a <br> tag for HTML)
            yield line.strip() + "<br>\n"
    process.stdout.close()
    process.wait()
    # Signal to the client that processing is complete
    yield "DONE"

@app.route('/upload', methods=['POST'])
def upload_file():
    # Validate file inputs
    if 'excel_file' not in request.files or 'word_file' not in request.files:
        return Response("Both files must be uploaded!", status=400)
    excel_file = request.files['excel_file']
    word_file = request.files['word_file']
    if excel_file.filename == '' or word_file.filename == '':
        return Response("Both files must be selected!", status=400)

    # Save uploaded files
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_file.filename)
    word_path = os.path.join(app.config['UPLOAD_FOLDER'], word_file.filename)
    excel_file.save(excel_path)
    word_file.save(word_path)

    # Run main.py using the "-u" flag to force unbuffered output
    def stream():
        process = subprocess.Popen(
            ["custom-env\Scripts\python.exe", "-u", "main.py", excel_path, word_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        yield from generate_output(process)

    # Create a streaming response with extra headers to disable buffering
    response = Response(stream(), mimetype='text/html')
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

@app.route('/download')
def download_file():
    output_file_path = os.path.join(os.getcwd(), "ai_use_cases.xlsx")
    if os.path.exists(output_file_path):
        return send_file(output_file_path, as_attachment=True)
    else:
        return Response("File not found!", status=404)

if __name__ == '__main__':
    app.run(debug=True)
