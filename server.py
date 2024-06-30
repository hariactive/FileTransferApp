from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CHUNKS_FOLDER = 'chunks'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CHUNKS_FOLDER):
    os.makedirs(CHUNKS_FOLDER)

@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    chunk = request.files['chunk']
    chunk_index = int(request.form['chunkIndex'])
    total_chunks = int(request.form['totalChunks'])
    file_name = 'uploaded_file.tmp'

    chunk.save(os.path.join(CHUNKS_FOLDER, f'{file_name}_part_{chunk_index}'))

    if chunk_index == total_chunks - 1:
        with open(os.path.join(UPLOAD_FOLDER, file_name), 'wb') as f_out:
            for i in range(total_chunks):
                with open(os.path.join(CHUNKS_FOLDER, f'{file_name}_part_{i}'), 'rb') as f_in:
                    f_out.write(f_in.read())
        for i in range(total_chunks):
            os.remove(os.path.join(CHUNKS_FOLDER, f'{file_name}_part_{i}'))

    return 'Chunk uploaded successfully'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
