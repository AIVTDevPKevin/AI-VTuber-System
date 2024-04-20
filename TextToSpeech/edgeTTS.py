import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio

import edge_tts










EdgeTTS_Voice_dict = {}

edgetts_parameters = {
    "output_path":"Audio/output_edgetts_01.mp3",
    "voice":"zh-TW-HsiaoChenNeural",
    "pitch":"+0Hz",
    "rate":"+0%",
    "volume":"+0%",
    "timeout":10,
}





async def async_edgetts(text, output_path, voice, pitch, rate, volume, timeout) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, pitch=pitch, rate=rate, volume=volume, receive_timeout=timeout)
    await communicate.save(output_path)


def edgetts(text="",
            output_path="Audio/output_edgetts_01.mp3",
            voice="zh-TW-HsiaoChenNeural",
            pitch="+0Hz", rate="+0%", volume="+0%", timeout=10,
            ):
    asyncio.run(async_edgetts(text, output_path, voice, pitch, rate, volume, timeout))





def create_voices_dict(file_path):
    voices_dict = {"Male": [], "Female": []}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if "Name" in line:
                name = line.split(":")[1].strip()

            elif "Gender" in line:
                gender = line.split(":")[1].strip()
                voices_dict[gender].append(name)

    return {gender: names for gender, names in voices_dict.items() if names}


def filter_voices_by_gender(voices_dict, gender):
    if gender == "All":
        return [name for names in voices_dict.values() for name in names]
    else:
        return voices_dict.get(gender, [])










if __name__ == "__main__":

    # Pitch  -100Hz ~ +100Hz
    # Rate   -100%  ~ +100%
    # Volume -100%  ~ +100%

    
    input_text = "Never gonna give you up never gonna let you down"
    edgetts(text=input_text,
            output_path="Audio/output_edgetts_01.mp3",
            voice="en-US-MichelleNeural",
            pitch="+30Hz",
            rate="-20%",
            volume="+0%",
            )
    

    '''
    input_text = "注意看，這個男人太狠了！"
    edgetts(text=input_text,
            output_path="Audio/output_edgetts_01.mp3",
            voice="zh-CN-YunxiNeural",
            pitch="+0Hz",
            rate="+0%",
            volume="+0%",
            )
    '''

    '''
    input_text = "廢話，車不改要怎麼騎？"
    edgetts(text=input_text,
            output_path="Audio/output_edgetts_01.mp3",
            voice="zh-TW-YunJheNeural",
            pitch="+0Hz",
            rate="+0%",
            volume="+0%",
            )
    '''
    
    '''
    input_text = "寶貝，你好大喔，做得好累"
    edgetts(text=input_text,
            output_path="Audio/output_edgetts_01.mp3",
            voice="zh-TW-HsiaoChenNeural",
            pitch="+15Hz",
            rate="-10%",
            volume="+0%",
            )
    '''

    '''
    input_text = "りしれ供さ小"
    edgetts(text=input_text,
            output_path="Audio/output_edgetts_01.mp3",
            voice="ja-JP-NanamiNeural",
            pitch="+15Hz",
            rate="-10%",
            volume="+0%",
            )
    '''




