import torch.multiprocessing as mp
from flask import Flask, jsonify, request
from flask_cors import CORS
from app_celery import make_celery, full_process_task
from worker import _full_process, _upload_files, _get_images
from werkzeug.utils import secure_filename
import os 

if mp.get_start_method(allow_none=True) != 'spawn':
    mp.set_start_method('spawn', force=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": 'http://localhost:5173'}})

app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['CELERY_BACKEND'] = 'rpc://localhost//'
# app.config['CELERY_IMPORTS'] = ['fstudio.tasks']

# celery = make_celery(app)


@app.route('/api/images/<user>', methods=['GET'])
def get_images(user):
    images = _get_images(user)
    return jsonify({
        "images": images,
        "msg": "Suceessfully Retrieved Images"
        }), 200


@app.route('/api/full', methods=['POST'])
def full_process():
    metadata = request.get_json()
    print(metadata)
    # process_info = full_process_task.delay(metadata)
    process_info = _full_process(metadata)

    return jsonify({
        'msg': 'Successfully Processed',
        'process_info': process_info
        }), 202


@app.route('/api/upload', methods=['POST'])
def upload_files():
    user = request.form.get('user')
    files = request.files.getlist('files')
    filenames, save_paths = _upload_files(user, files)
    return jsonify({
        'user': user,
        'filenames': filenames, 
        'save_paths': save_paths,
        'msg': f"Successfully Uploaded "
        }), 202


        # filename = secure_filename(file.filename)
        # file.save(filename)

        # # Define the S3 path based on the username
        # s3_path = f'{username}/{filename}'

        # # Upload the file to S3
        # s3.upload_file(
        #     Bucket='your-bucket-name',
        #     Filename=filename,
        #     Key=s3_path
        # )

        # # Delete the file from local after upload to S3
        # os.remove(filename)

    return jsonify({'info': f"Successfully Uploaded {filenames}"}), 202



# @app.route('/api/full/<task_id>')
# def task_status(task_id):
#     task = full_process_task.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {'state': task.state, 'status': 'Task is pending'}
#     elif task.state != 'FAILURE':
#         response = {'state': task.state, 'result': task.result}
#     else:
#         response = {'state': task.state, 'status': str(task.result)}
#     return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)


