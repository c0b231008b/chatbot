from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import time
import os

app = Flask(__name__)


class Voicevox:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port

    def speak(self, text=None, speaker=8, save_file=False, filename="output.wav"):
        params = (
            ("text", text),
            ("speaker", speaker)
        )

        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )

        if save_file:
            with open(filename, "wb") as f:
                f.write(res.content)
            print(f"音声ファイルを保存しました: {filename}")

        return filename


STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input. 'text' field is required."}), 400

    text = data['text']
    # STATIC_DIRのすべての音声ファイルを削除する
    for file in os.listdir(STATIC_DIR):
        file_path = os.path.join(STATIC_DIR, file)
        try:
            if os.path.isfile(file_path) and file_path.endswith('.wav'):
                os.unlink(file_path)
                print(f"削除しました: {file_path}")
        except Exception as e:
            print(f"エラーが発生しました: {e}")

    filename = f"response_{int(time.time())}.wav"
    full_path = os.path.join(STATIC_DIR, filename)

    vv = Voicevox()
    vv.speak(text=text, save_file=True, filename=full_path)

    return jsonify({"filename": filename})


if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)  
    app.run(host='0.0.0.0', port=8001, debug=True)
