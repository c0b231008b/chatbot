import requests, json
import io
import wave
import pyaudio
import time
import xmlrpc.client
import os

class Voicevox:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port

    def speak(self, text=None, speaker=3, save_file=False, filename="output.wav"):
        params = (
            ("text", text),
            ("speaker", speaker)  # 音声の種類をInt型で指定
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

        # メモリ上で展開
        audio = io.BytesIO(res.content)

        if save_file:
            # 音声ファイルを保存
            with open(filename, "wb") as f:
                f.write(audio.getvalue())  
            print(f"音声ファイルを保存しました: {filename}")

 

        with wave.open(audio, 'rb') as f:
            # 以下再生用処理
            p = pyaudio.PyAudio()

            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)

            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            stream_callback=_callback)

            # Voice再生
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()


proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8000')
while True:
    # ユーザーからの入力を取得
    user_input = input("マスター: ")
    
    # 終了コマンド
    if user_input.lower() in ["終了", "exit", "quit"]:
        print("チャットを終了します。")
        break
    
    # サーバーにリクエストを送信してレスポンスを取得
    response = proxy.respond_to_user_input(user_input)

    print(f"ずんだもん: {response}")

    vv = Voicevox()
    vv.speak(text=response, save_file=True, filename=f"response_{int(time.time())}.wav")