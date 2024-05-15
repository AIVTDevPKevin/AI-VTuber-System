import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import queue
import time
import glob
import gc

import whisper
import torch

from My_Tools.AIVT_print import aprint










Whisper_LANGUAGES = {
    "en": "english",
    "zh": "chinese",
    "ja": "japanese",
    "ko": "korean",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    "fr": "french",
    "pt": "portuguese",
    "tr": "turkish",
    "pl": "polish",
    "ca": "catalan",
    "nl": "dutch",
    "ar": "arabic",
    "sv": "swedish",
    "it": "italian",
    "id": "indonesian",
    "hi": "hindi",
    "fi": "finnish",
    "vi": "vietnamese",
    "he": "hebrew",
    "uk": "ukrainian",
    "el": "greek",
    "ms": "malay",
    "cs": "czech",
    "ro": "romanian",
    "da": "danish",
    "hu": "hungarian",
    "ta": "tamil",
    "no": "norwegian",
    "th": "thai",
    "ur": "urdu",
    "hr": "croatian",
    "bg": "bulgarian",
    "lt": "lithuanian",
    "la": "latin",
    "mi": "maori",
    "ml": "malayalam",
    "cy": "welsh",
    "sk": "slovak",
    "te": "telugu",
    "fa": "persian",
    "lv": "latvian",
    "bn": "bengali",
    "sr": "serbian",
    "az": "azerbaijani",
    "sl": "slovenian",
    "kn": "kannada",
    "et": "estonian",
    "mk": "macedonian",
    "br": "breton",
    "eu": "basque",
    "is": "icelandic",
    "hy": "armenian",
    "ne": "nepali",
    "mn": "mongolian",
    "bs": "bosnian",
    "kk": "kazakh",
    "sq": "albanian",
    "sw": "swahili",
    "gl": "galician",
    "mr": "marathi",
    "pa": "punjabi",
    "si": "sinhala",
    "km": "khmer",
    "sn": "shona",
    "yo": "yoruba",
    "so": "somali",
    "af": "afrikaans",
    "oc": "occitan",
    "ka": "georgian",
    "be": "belarusian",
    "tg": "tajik",
    "sd": "sindhi",
    "gu": "gujarati",
    "am": "amharic",
    "yi": "yiddish",
    "lo": "lao",
    "uz": "uzbek",
    "fo": "faroese",
    "ht": "haitian creole",
    "ps": "pashto",
    "tk": "turkmen",
    "nn": "nynorsk",
    "mt": "maltese",
    "sa": "sanskrit",
    "lb": "luxembourgish",
    "my": "myanmar",
    "bo": "tibetan",
    "tl": "tagalog",
    "mg": "malagasy",
    "as": "assamese",
    "tt": "tatar",
    "haw": "hawaiian",
    "ln": "lingala",
    "ha": "hausa",
    "ba": "bashkir",
    "jw": "javanese",
    "su": "sundanese",
    "yue": "cantonese",
}

whisper_status = {
    "loaded_model": "",
    "gui_selected_model": "base",
    "model_loding": False,
}

whisper_parameters = {
    "user_mic_language": "zh",
    "prompt": "",
    "max_tokens": 192,
    "temperature": 0.2,
    "timeout": 10,
}

model = None





def get_available_model_names_list():
    pattern = os.path.join("OpenAI/whisper/models/", "*.pt")
    pt_files = glob.glob(pattern)
    model_names_list = [os.path.splitext(os.path.basename(file))[0] for file in pt_files]
    return model_names_list



def load_model(model_name="base"):
    global model, whisper_status

    whisper_status["model_loding"] = True
    aprint(f"Whisper model loading: {model_name}")

    try:
        if whisper_status["loaded_model"]:
            del model
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        start_time = time.time()

        model = whisper.load_model(name=f"OpenAI/whisper/models/{model_name}.pt", )

        end_time = time.time()

        aprint(f"!!! Whisper Loaded Model Success: {model_name} !!!\nLoading time: {end_time - start_time:.2f}s\n")
        whisper_status["loaded_model"] = model_name

    except Exception as e:
        aprint(f"!!! Whisper Loaded Model Fail: {model_name} !!!\n{e}\n")
        whisper_status["loaded_model"] = ""

    whisper_status["model_loding"] = False


def unload_model():
    global model, whisper_status

    if whisper_status["loaded_model"]:
        try:
            del model
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            aprint(f"!!! Model Unloaded Success: {whisper_status['loaded_model']} !!!\n")
            whisper_status["loaded_model"] = ""
            model = None

        except Exception as e:
            aprint(f"!!! Model Unloaded fail: {whisper_status['loaded_model']} !!!\n{e}\n")





def run_with_timeout_OpenAI_Whisper(
        audio_path = "audio/input_user_mic.wav",
        audio_language = "zh",
        prompt = "",
        max_tokens = 192,
        temperature = 0.2,
        timeout=10,
        ):
    global whisper_status

    while whisper_status["model_loding"]:
        time.sleep(0.1)

    if whisper_status["loaded_model"] == "":
        load_model(model_name=whisper_status["gui_selected_model"])

    if whisper_status["loaded_model"] == "":
        print("\n!!! OpenAI Whisper Transcribe Fail !!!\n")
        return ""
    
    model_name = whisper_status["loaded_model"]

    transcribe_ans = queue.Queue()

    start_time = time.time()

    OWt = threading.Thread(
        target = OpenAI_Whisper_thread,
        args = (transcribe_ans, ),
        kwargs = {
            "audio_path": audio_path,
            "audio_language": audio_language,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            },
        )

    OWt.start()
    OWt.join(timeout)

    if OWt.is_alive():
        print("\n!!! OpenAI Whisper time out !!!\n")
        return ""

    else:
        end_time = time.time()
        whisper_result = transcribe_ans.get()
        print("\nOpenAI Whisper Local ----------\n")
        print(f"Model: {model_name}")
        print(f"Duration: {end_time - start_time:.2f}s\n")
        print(f"Transcribe: {whisper_result}")
        print("\n----------\n")
        return whisper_result 


def OpenAI_Whisper_thread(
        ans,
        audio_path="audio/input_user_mic.wav",
        audio_language="zh",
        prompt="",
        max_tokens=192,
        temperature=0.2,
        ):
    global model

    try:
        result = model.transcribe(
            audio = audio_path,
            language = audio_language,
            initial_prompt = prompt,
            temperature=temperature,
            sample_len=max_tokens,
            )

    except Exception as e:
        aprint(f"!!! Fail Transcribing !!!\n{e}\n")
        ans.put("")
        return

    ans.put(result["text"])
    return




