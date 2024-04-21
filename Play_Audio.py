import os
import io
import wave
current_dir = os.path.dirname(os.path.abspath(__file__))
bin_dir = os.path.join(current_dir, "GUI_control_panel")
bin_dir = os.path.abspath(bin_dir)
os.environ["PATH"] += os.pathsep + bin_dir

import pyaudio
from pydub import AudioSegment
ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")
AudioSegment.converter = ffmpeg_path










play_audio_parameters = {
    "ai_voice_output_device_name": "",
    "chunk": 1024,
}



def PlayAudio(audio_path, output_device_name, command=None):
    global play_audio_parameters

    output_device_index = Get_available_output_devices_ID(output_device_name)

    _, file_extension = os.path.splitext(audio_path)
    if file_extension.lower() == '.wav':
        audio_data = open(audio_path, 'rb')
    else:
        audio = AudioSegment.from_file(audio_path)
        audio_data = io.BytesIO()
        audio.export(audio_data, format="wav")
        audio_data.seek(0)

    wf = wave.open(audio_data, 'rb')
    p = pyaudio.PyAudio()

    CHUNK = play_audio_parameters["chunk"]
    stream = p.open(
            output=True,
            output_device_index=output_device_index,
            channels=wf.getnchannels(),
            format=p.get_format_from_width(wf.getsampwidth()),
            rate=wf.getframerate(),
        )

    data = wf.readframes(CHUNK)

    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()





def Available_output_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            print(f"Output Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}")

    p.terminate()


def Get_available_output_devices_List():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    output_devices_list = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            output_devices_list.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

    p.terminate()
    return output_devices_list


def Get_available_output_devices_ID(devices_name):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    # find output device id by device name
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            if devices_name == p.get_device_info_by_host_api_device_index(0, i).get('name'):
                p.terminate()
                return i

    # if the name is not in output device list
    #return default system audio output device
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            p.terminate()
            return i

    p.terminate()
    return None










if __name__ == "__main__":
    Available_output_devices()


