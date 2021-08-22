# Copyright 2019 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import base64
import json
import logging
import os
from datetime import datetime , timezone , timedelta
import jwt
#Add End

from flask import current_app, Flask, render_template, request
from google.auth.transport import requests
import google.auth.transport.requests
import requests
from google.oauth2 import id_token
from google.cloud import storage


app = Flask(__name__)

# Configure the following environment variables via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
SCAN_URL = os.environ['SCAN_URL']
EXPECTED_AUDIENCE = os.environ['EXPECTED_AUDIENCE']

#CSV Check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])

#IAP_JWT Infomations Get 
def validate_iap_jwt(iap_jwt, expected_audience):
    """Validate an IAP JWT.
    Args:
      iap_jwt: The contents of the X-Goog-IAP-JWT-Assertion header.
      expected_audience: The Signed Header JWT audience. See
      https://cloud.google.com/iap/docs/signed-headers-howto
      for details on how to get this value.

    Returns:
      (user_id, user_email, error_str).
              """
    request = google.auth.transport.requests.Request()
    try:
        decoded_jwt = id_token.verify_token(
            iap_jwt, request=request, audience=expected_audience,
            certs_url='https://www.gstatic.com/iap/verify/public_key')
        return (decoded_jwt['sub'], decoded_jwt['email'], '')
    except Exception as e:
        return (None, None, '**ERROR: JWT validation error {}**'.format(e))
#Add End

# [START index]
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
# [END index]


# [START 戻るボタン押下]
@app.route('/testback', methods=["GET"])
def testback():
        return render_template('index.html')
# [END]

# [START アップロード時]
@app.route('/upload', methods=['POST'])
def upload():

    #JWT Infomations and EmailAddress Get 
    token = request.headers["x-goog-iap-jwt-assertion"] 
    publicKey = validate_iap_jwt(token,EXPECTED_AUDIENCE) 
    s = publicKey[1]
    target = '@'
    idx = s.find(target)
    email_add = s[:idx]

    # TimeZone Setting
    JST = timezone(timedelta(hours=+9), 'JST')
    now_timestamp = datetime.now(JST).strftime('%Y%m%d%H%M%S')   

    #upload file name Setting
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('file')
    fname = email_add + "_" + now_timestamp + "_" + uploaded_file.filename

    #File Exist Check
    if not uploaded_file:
        return 'No file uploaded.', 400

    #CSV Check
    if not allowed_file(uploaded_file.filename):
        return 'No allowed file-type', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(fname)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    #Call Virus Web-API CALL
    url = SCAN_URL
    obj = {
         "location": "gs://" + CLOUD_STORAGE_BUCKET + "/" + fname,
         "filename": fname,
         "bucketname": CLOUD_STORAGE_BUCKET
    }

    response = requests.post(
            url,
            json = obj
            )
    jsonResponse = response.json()

    if jsonResponse["virus_status"] == 1:
        logging.warning('WARNING! virus_detected. filename ={},message={}'.format(uploaded_file.filename,jsonResponse["message"]))
        return render_template('comp_alert.html')
    elif jsonResponse["virus_status"] == 9:
        logging.error('unexpected Error occured. filename ={},message={}'.format(uploaded_file.filename,jsonResponse["message"]))
        return 'unexpected Error occured', 500
    else:
        return render_template('comp.html')
# [END]

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
