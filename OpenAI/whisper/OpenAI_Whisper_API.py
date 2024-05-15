import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import time
import queue

import openai

import AIVT_Config










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

whisper_parameters = {
    "model":"whisper-1",
    "user_mic_language":"zh",
    "prompt":"",
    "temperature":0.2,
    "timeout":10,
}





def run_with_timeout_OpenAI_Whisper_API(
        model = "whisper-1",
        audio_path = "audio/input_user_mic.wav",
        audio_language = "zh",
        prompt = "",
        temperature = 0.2,
        timeout=10,
        ):

    transcribe_ans = queue.Queue()

    start_time = time.time()

    OWAt = threading.Thread(
        target = OpenAI_Whisper_API_thread,
        args = (transcribe_ans, ),
        kwargs = {
            "model": model,
            "audio_path": audio_path,
            "audio_language": audio_language,
            "prompt": prompt,
            "temperature": temperature,
            },
        )

    OWAt.start()
    OWAt.join(timeout)

    if OWAt.is_alive():
        print("\n!!! OpenAI Whisper API time out !!!\n")
        return ""

    else:
        end_time = time.time()
        whisper_result = transcribe_ans.get()
        print("\nOpenAI Whisper API ----------\n")
        print(f"Duration: {end_time - start_time:.2f}s\n")
        print(f"Transcribe: {whisper_result}")
        print("\n----------\n")
        return whisper_result  


def OpenAI_Whisper_API_thread(
        ans,
        model = "whisper-1",
        audio_path = "audio/input_user_mic.wav",
        audio_language = "zh",
        prompt = "",
        temperature = 0.2,
        ):

    openai.api_key = AIVT_Config.openai_api_key

    try:
        audio_file = open(audio_path, "rb")
        transcript = openai.audio.transcriptions.create(
            model=model,
            file=audio_file,
            language=audio_language,
            prompt=prompt,
            temperature=temperature,
            )

        ans.put(transcript.text)
        return

    except Exception as e:
        print(f"Error transcribing audio\n{e}\n")
        ans.put("")
        return




