import base64
from dotenv import load_dotenv
import hashlib
import hmac
import mutagen
import os
import sys
import time
import requests
from pydub import AudioSegment

load_dotenv()

# ACRCloud data
access_key = os.getenv("ACCESS_KEY")
access_secret = os.getenv("SECRET")
requrl = "http://identify-us-west-2.acrcloud.com/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"
# default is "fingerprint", it's for recognizing fingerprint, 
# if you want to identify audio, please change data_type="audio"
data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
    timestamp)

sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),
                                 digestmod=hashlib.sha1).digest()).decode('ascii')

def splice_mp3(input_file, output_file, start_time_ms, end_time_ms):
    audio = AudioSegment.from_mp3(input_file)

    if len(audio) < 60000:
        end_time_ms = len(audio)

    spliced_audio = audio[start_time_ms:end_time_ms]
    spliced_audio.export(output_file, format="mp3")

def get_metadata(output_file):

    f = open(output_file, "rb")
    sample_bytes = os.path.getsize(output_file)

    files = [
        ("sample", ("output.mp3", open(output_file, "rb"), "audio/mpeg"))
    ]

    data = {'access_key': access_key,
    'sample_bytes': sample_bytes,
    'timestamp': str(timestamp),
    'signature': sign,
    'data_type': data_type,
    "signature_version": signature_version}

    r = requests.post(requrl, files=files, data=data)
    r.encoding = "utf-8"
    print(r.text)
    return r.json()

def tag_file(file, metadata):
    parsed_file = mutagen.File(file)
    #parsed_file.tags["@ART"] = metadata["metadata"]["music"][0]["artists"][0]["name"]
    parsed_file.pprint()
    parsed_file.save()
    pass

if __name__ == "__main__":
    input_files = [os.path.join("songs", "inputs", f) for f in os.listdir("songs/inputs")]
    output_file_path = os.path.join("songs", "outputs", "output.mp3")
    start_time_ms = 0
    end_time_ms = 60000

    for input_file in input_files:
        splice_mp3(input_file, output_file_path, start_time_ms, end_time_ms)
        response_json = get_metadata(output_file_path)
        tag_file(output_file_path, response_json)
