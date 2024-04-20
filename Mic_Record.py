import time
import threading
import pyaudio
import wave

import keyboard

import AI_Vtuber_UI as aivtui
from My_Tools.AIVT_print import aprint










user_mic_status = {
    "mic_on": False,
    "mic_record_running": False,
    "mic_checker_running": False,
    "mic_hotkeys_using": False,
    "mic_hotkey_1_detecting": False,
    "mic_hotkey_1_using": False,
    "mic_hotkey_1": "`",
    "mic_hotkey_2_detecting": False,
    "mic_hotkey_2_using": False,
    "mic_hotkey_2": "caps lock",
}

User_Mic_parameters = {
    "user_mic_audio_path": "Audio/user_mic_record/input_user_mic.wav",
    "input_device_name": "",
    "channels": 1,
    "format": pyaudio.paInt16,
    "rate": 24000,
    "chunk": 1024,
    "minimum_duration": 1,
}

Audio_frames_out = []
Mic_hotkey_pressed = False



def MC_Record():
    global user_mic_status, User_Mic_parameters, Mic_hotkey_pressed, Audio_frames_out

    input_device_index = Get_available_input_devices_ID(User_Mic_parameters["input_device_name"])
    CHUNK = User_Mic_parameters["chunk"]

    p = pyaudio.PyAudio()
    audio_stream = p.open(
            input=True,
            input_device_index=input_device_index,
            channels=User_Mic_parameters["channels"],
            format=User_Mic_parameters["format"],
            rate=User_Mic_parameters["rate"],
            frames_per_buffer=CHUNK,
        )

    Mic_hotkey_pressed = False
    dmhp = threading.Thread(target=Detect_Mic_hotkey_pressed)
    dmhp.start()

    while user_mic_status["mic_on"]:
        if Mic_hotkey_pressed:
            frames = []
            start_time = time.time()
            current_time = start_time

            while Mic_hotkey_pressed:
                data = audio_stream.read(CHUNK)
                frames.append(data)
                current_time = time.time()

            if current_time - start_time >= User_Mic_parameters["minimum_duration"]:
                Audio_frames_out.append(frames)
                aprint("* Record output *")

            else:
                aprint("*** Mic Record Cancel ***")

        time.sleep(0.1)

    user_mic_status["mic_record_running"] = False

    audio_stream.stop_stream()
    audio_stream.close()
    p.terminate()
    dmhp.join()
    print("* User Mic OFF *")


def Detect_Mic_hotkey_pressed():
    global user_mic_status, Mic_hotkey_pressed
    def on_key_event(e):
        global Mic_hotkey_pressed
        if e.event_type == keyboard.KEY_DOWN and user_mic_status["mic_hotkeys_using"]:
            if user_mic_status["mic_hotkey_1_using"] and user_mic_status["mic_hotkey_2_using"]:
                hotkeys = f"{user_mic_status['mic_hotkey_1']}+{user_mic_status['mic_hotkey_2']}"

            elif user_mic_status["mic_hotkey_1_using"]:
                hotkeys = user_mic_status['mic_hotkey_1']

            else:
                hotkeys = user_mic_status['mic_hotkey_2']
 
            if not Mic_hotkey_pressed and keyboard.is_pressed(hotkeys):
                aprint('** Start Mic Recording **')
                Mic_hotkey_pressed = True

        elif e.event_type == keyboard.KEY_UP and user_mic_status["mic_hotkeys_using"]:
            if Mic_hotkey_pressed and ((e.name == user_mic_status["mic_hotkey_1"] and user_mic_status["mic_hotkey_1_using"]) or (e.name == user_mic_status["mic_hotkey_2"] and user_mic_status["mic_hotkey_2_using"])):
                aprint('** End Mic Recording **')
                Mic_hotkey_pressed = False


    keyboard.hook(on_key_event)

    print("* User Mic ON *")
    user_mic_status["mic_record_running"] = True

    while user_mic_status["mic_on"]:
        time.sleep(0.1)

    Mic_hotkey_pressed = False

    keyboard.unhook_all()


def MC_Output_checker():
    global user_mic_status, Audio_frames_out

    user_mic_status["mic_checker_running"] = True

    while user_mic_status["mic_on"]:
        if Audio_frames_out:
            aprint("* output check *")
            mco = threading.Thread(target=aivtui.OpenAI_Whisper_thread, args=(Audio_frames_out.pop(0), ))
            mco.start()

        time.sleep(0.1)

    # Avoid mic off when MC_Record is still processing
    while user_mic_status["mic_record_running"]:
        time.sleep(0.1)

    if Audio_frames_out:
        aprint("* output check *")
        mco = threading.Thread(target=aivtui.OpenAI_Whisper_thread, args=(Audio_frames_out.pop(0), ))
        mco.start()
        mco.join()

    user_mic_status["mic_checker_running"] = False





def save_audio2wav(audio_frames, save_path):
    global User_Mic_parameters

    p = pyaudio.PyAudio()

    wf = wave.open(save_path, 'wb')
    wf.setnchannels(User_Mic_parameters["channels"])
    wf.setsampwidth(p.get_sample_size(User_Mic_parameters["format"]))
    wf.setframerate(User_Mic_parameters["rate"])
    wf.writeframes(b''.join(audio_frames))
    wf.close()





def Get_key_press():
    print("User Mic Hotkey Detecting(Press ESC to cancel)...")
    event = keyboard.read_event()

    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name
        if not key_name == "esc":
            print(f"Detected Key: {key_name}")

        else:
            print("User Mic Hotkey Cancel")

        return key_name





def Available_Input_Device():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"Input Device id {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}")

    p.terminate()


def Get_available_input_devices_List():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    input_devices_list = []
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            input_devices_list.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

    p.terminate()
    return input_devices_list


def Get_available_input_devices_ID(devices_name):
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    # find input device id by device name
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            if devices_name == p.get_device_info_by_host_api_device_index(0, i).get('name'):
                p.terminate()
                return i

    # if the name is not in input device list
    #return default system audio input device
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            p.terminate()
            return i

    p.terminate()
    return None










if __name__ == "__main__":
    Available_Input_Device()
    devices_id = Get_available_input_devices_ID("Never gonna make you cry never gonna say goodbye")
    print(f"Devices ID: {devices_id}")
    #Get_key_press()


