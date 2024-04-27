import os
import sys
import queue
import threading
import time
import random
import re
import copy 
import math
import datetime
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf8", buffering=1)

import Play_Audio
import Mic_Record
import My_Tools.Token_Calculator as tokenC
import TextToSpeech.edgeTTS as edgeTTS
import TextToSpeech.OpenAITTS as openaiTTS
import VTubeStudioPlugin.VTubeStudioPlugin as vtsp
import OBS_websocket.OBS_websocket as obsws
import OpenAI.whisper.OpenAI_Whisper as whisper
import OpenAI.whisper.OpenAI_Whisper_API as whisper_api
import OpenAI.gpt.OpenAI_GPT_API as gpt_api
import Google.gemini.GoogleAI_Gemini_API as gimini_api
import Sentiment_Analysis.NLP_API as sa_nlp_api
import Live_Chat.Live_Chat as live_chat
from My_Tools.AIVT_print import aprint










GUI_Running = False
GUI_User_Name = "PKevin"

AIVT_Character_path = "AIVT_Character"
AIVT_Character_prompt_filenames = [
    'character_prompt_01.txt', 'character_prompt_02.txt',
    'character_prompt_03.txt', 'character_prompt_04.txt',
    'character_prompt_05.txt'
    ]
AIVT_Character_Names = []
AIVT_Using_character = ""
AIVT_Using_character_previous = ""

conversation = []


def Load_AIVT_Character():
    global AIVT_Character_path, AIVT_Character_Names

    AIVT_Character_Names = []

    for subfolder in os.listdir(AIVT_Character_path):
        subfolder_path = os.path.join(AIVT_Character_path, subfolder)
        if os.path.isdir(subfolder_path):
            AIVT_Character_Names.append(subfolder)

    print(f"\n!!! Successfully Loaded {len(AIVT_Character_Names)} Characters !!!")

    for i, name in enumerate(AIVT_Character_Names):
        print(f"{i+1}. {name}")

    print("")

def Initialize_conversation(Using_character_name):
    global GUI_LLM_parameters, conversation
    global AIVT_Character_path, AIVT_Character_prompt_filenames, AIVT_Using_character_previous

    print(f"\n!!! Character *{Using_character_name}* Conversation Initializing !!!")

    for filename in AIVT_Character_prompt_filenames:
        path = os.path.join(AIVT_Character_path, Using_character_name, filename)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                character_prompt = file.read()
                conversation.append({"role": "system", "content": character_prompt})
        except FileNotFoundError:
            conversation.append({"role": "system", "content": ""})
            print(f"File not found: {path}")

    conversation.append({"role": "system", "content": GUI_LLM_parameters["wdn_prompt"]})

    AIVT_Using_character_previous = Using_character_name

    print(f"!!! Initialization Done !!!")

def conversation_character_prompt_change(Using_character_name, command=None):
    global conversation, AIVT_Character_path, AIVT_Character_prompt_filenames, AIVT_Using_character_previous

    if len(conversation) < len(AIVT_Character_prompt_filenames):
        print("The conversation does not have enough entries to replace.")
        return
    
    for i, filename in enumerate(AIVT_Character_prompt_filenames):
        path = os.path.join(AIVT_Character_path, Using_character_name, filename)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                character_prompt = file.read()
                if i < len(conversation):
                    conversation[i]["content"] = character_prompt
                else:
                    break
        except FileNotFoundError:
            conversation[i]["content"] = ""
            print(f"File not found: {path}")

    if command != "No merge":
        start_index = len(AIVT_Character_prompt_filenames) + 1
        if len(conversation) > start_index:
            merged_content = ""
            for entry in conversation[start_index:]:
                if entry["role"] == "assistant":
                    merged_content += f"{AIVT_Using_character_previous}: {entry['content']}\n"
                elif entry["role"] == "user":
                    merged_content += f"{entry['content']}\n"

            conversation = conversation[:len(AIVT_Character_prompt_filenames)+1]  # 保留前面的部分
            if merged_content:
                conversation.append({"role": "user", "content": merged_content.rstrip()})  # 添加合併後的內容

        #print(f"\n\n{conversation}\n\n")

    AIVT_Using_character_previous = Using_character_name



def get_instruction_enhance_prompt(Using_character_name):
    global AIVT_Character_path

    path = os.path.join(AIVT_Character_path, Using_character_name, "instruction_prompt.txt")

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        return ""

def write_instruction_enhance_prompt(Using_character_name, Instruction_enhance_prompt):
    global AIVT_Character_path

    path = os.path.join(AIVT_Character_path, Using_character_name, "instruction_prompt.txt")

    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(Instruction_enhance_prompt)
            #print(f"!!! *{Using_character_name}* Write Instruction Enhance Prompt Susses !!!")
    except:
        print(f"!!! *{Using_character_name}* Write Instruction Enhance Prompt Failed !!!")










OpenAI_Whisper_Inference = "Local"
OpenAI_Whisper_LLM_wait_list = []

lock_OpenAI_Whisper = threading.Lock()

def OpenAI_Whisper_thread(audio_frames, command=None):
    global GUI_User_Name, OpenAI_Whisper_LLM_wait_list, OpenAI_Whisper_Inference

    with lock_OpenAI_Whisper:
        user_mic_audio_path = Mic_Record.User_Mic_parameters["user_mic_audio_path"]

        Mic_Record.save_audio2wav(audio_frames, user_mic_audio_path, )

        aprint("* Whisper Transcribing... *")

        if OpenAI_Whisper_Inference == "Local":
            ans_OpenAI_Whisper_text = whisper.run_with_timeout_OpenAI_Whisper(
                audio_path = user_mic_audio_path,
                audio_language = whisper.whisper_parameters["user_mic_language"],
                prompt = whisper.whisper_parameters["prompt"],
                max_tokens = whisper.whisper_parameters["max_tokens"],
                temperature = whisper.whisper_parameters["temperature"],
                timeout = whisper.whisper_parameters["timeout"]
            )

        else:
            ans_OpenAI_Whisper_text = whisper_api.run_with_timeout_OpenAI_Whisper_API(
                model = whisper_api.whisper_parameters["model"],
                audio_path = user_mic_audio_path,
                audio_language = whisper_api.whisper_parameters["user_mic_language"],
                prompt = whisper_api.whisper_parameters["prompt"],
                temperature = whisper_api.whisper_parameters["temperature"],
                timeout = whisper_api.whisper_parameters["timeout"]
            )


        if ans_OpenAI_Whisper_text != "":
            role = "user_mic"
            ans_OpenAI_Whisper_text = GUI_User_Name + " : " + ans_OpenAI_Whisper_text
            ans_requst = {"role": role, "content": ans_OpenAI_Whisper_text}
            OpenAI_Whisper_LLM_wait_list.append(ans_requst)










GUI_LLM_parameters = {
    "model": "",
    "instruction_enhance": False,
    "instruction_enhance_i": 3,
    "instruction_enhance_prompt": "",
    "wdn_prompt": "",
}

lock_LLM_Request = threading.Lock()

def LLM_Request_thread(ans_request, llm_ans=None):
    global GUI_LLM_parameters, conversation

    with lock_LLM_Request:
        role = ans_request["role"]
        conversation_now = ans_request["content"]

        if role == "assistant":
            llm_ans.put("")
            return


        if GUI_LLM_parameters["instruction_enhance"]:
            conversation_instruction = GUI_LLM_parameters["instruction_enhance_prompt"]
        else:
            conversation_instruction = ""


        llm_model_name = ""
        token_max = 0
        
        if GUI_LLM_parameters["model"] == "Gemini":
            llm_model_name  = gimini_api.gemini_parameters["model"]
            token_max = gimini_api.gemini_parameters["max_input_tokens"] - 10
        elif GUI_LLM_parameters["model"] == "GPT":
            llm_model_name = gpt_api.gpt_parameters["model"]
            token_max = gpt_api.gpt_parameters["max_input_tokens"]
        else:
            llm_model_name  = gimini_api.gemini_parameters["model"]
            token_max = gimini_api.gemini_parameters["max_input_tokens"]


        conversation_for_llm = copy.deepcopy(conversation)

        iea = False
        iei = GUI_LLM_parameters["instruction_enhance_i"]*2
        if len(conversation) >= 6+iei:
            iea = True
            conversation_for_llm.insert(len(conversation)-iei, {'role': 'system', 'content': conversation_instruction})

        chat_role = ["user", "user_mic", "youtube_chat", "twitch_chat"]

        if role in chat_role:
            conversation.append({"role": "user", "content": conversation_now})
            conversation_for_llm.append({"role": "user", "content": conversation_now})


        token_now = tokenC.num_tokens_from_conversation(conversation_for_llm, llm_model_name)
        print(f"LLM Request input tokens {token_now}")

        cp = 7
        if iea:
            cp += 1

        while token_now > token_max:
            if len(conversation_for_llm) <= cp:
                print("!!! Plz Increse Max Input Tokens Or Reduce The Prompt !!!")
                llm_ans.put("")
                return
            
            conversation.pop(6)
            conversation_for_llm.pop(6)
            token_now = tokenC.num_tokens_from_conversation(conversation_for_llm, llm_model_name)
            print(f"LLM Request input tokens {token_now}")


        if GUI_LLM_parameters["model"] == "Gemini":
            llm_result = gimini_api.run_with_timeout_GoogleAI_Gemini_API(
                conversation_for_llm,
                conversation_now,
                model_name=gimini_api.gemini_parameters["model"],
                max_output_tokens=gimini_api.gemini_parameters["max_output_tokens"],
                temperature=gimini_api.gemini_parameters["temperature"],
                timeout=gimini_api.gemini_parameters["timeout"],
                retry=gimini_api.gemini_parameters["retry"],
                )

        elif GUI_LLM_parameters["model"] == "GPT":
            llm_result = gpt_api.run_with_timeout_OpenAI_GPT_API(
                conversation_for_llm,
                conversation_now,
                model_name=gpt_api.gpt_parameters["model"],
                max_output_tokens=gpt_api.gpt_parameters["max_output_tokens"],
                temperature=gpt_api.gpt_parameters["temperature"],
                timeout=gpt_api.gpt_parameters["timeout"],
                retry=gpt_api.gpt_parameters["retry"],
                )

        else:
            llm_ans.put("")
            return


        if llm_result == None or llm_result == "":
            if llm_result == None:
                print(f"LLM requset timeout!!!")
            else:
                print(f"LLM requset failed!!!")

            llm_ans.put("")
            return


        elif llm_result != "":
            conversation.append({"role": "assistant", "content": f"{llm_result}"})
            llm_ans.put(llm_result)
            return

        #print(f"\n{conversation}\n")










GUI_TTS_Using = ""
GUI_Setting_read_chat_now = False
GUI_VTSP_wait_until_hotkeys_complete = False

GUI_AIVT_Speaking_wait_list = []
GUI_Conversation_History_list = []


def subtitles_speak_checker():
    global GUI_Running, GUI_AIVT_Speaking_wait_list, GUI_Conversation_History_list

    while GUI_Running:
        if len(GUI_AIVT_Speaking_wait_list) > 0:
            sst_arg = GUI_AIVT_Speaking_wait_list.pop(0)
            GUI_Conversation_History_list.append(sst_arg)

            try:
                threading.Thread(
                    target=subtitles_speak_thread,
                    args=(
                        sst_arg["chat_role"],
                        sst_arg["chat_now"],
                        sst_arg["ai_ans"],
                        sst_arg["ai_name"],
                        ),
                    ).start()
                
            except Exception as e:
                print(f"\n{e}\n")

        time.sleep(0.1)



lock_sa_requst = threading.Lock()
lock_tts_request = threading.Lock()
lock_subtitles_speak = threading.Lock()
lock_remove_file = threading.Lock()
speaking_continue_count = 0
speaking_continue_vtsp_hkns = []

def subtitles_speak_thread(chat_role, chat_now, ai_ans, ai_name):
    global GUI_Setting_read_chat_now, speaking_continue_count

    read_chat_role = ["user", "user_mic"]
    read_chat_now = (GUI_Setting_read_chat_now and chat_role in read_chat_role) or (live_chat.Live_chat_parameters["yt_live_chat_read_chat_now"] and chat_role == "youtube_chat") or (live_chat.Live_chat_parameters["tw_live_chat_read_chat_now"] and chat_role == "twitch_chat")

    AIVT_VTSP_Status_authenticated = vtsp.AIVT_VTSP_Status["authenticated"]

    sa_enble = vtsp.AIVT_hotkeys_parameters["sentiment_analysis"] and AIVT_VTSP_Status_authenticated
    if sa_enble:
        sa_ans = queue.Queue()
        sar = threading.Thread(target=sa_request_thread, args=(ai_ans, sa_ans, ))
        sar.start()
    else:
        emo_state = ""

    
    chat_now_tts_path = ""
    if read_chat_now:
        chat_now_tts_path = queue.Queue()
        tts_chat_now = chat_now.replace(";)", ")")
        tts_chat_now = tts_chat_now.replace("；)", ")")
        tr_cn = threading.Thread(target=tts_request_thread, args=(tts_chat_now, chat_now_tts_path, ))
        tr_cn.start()

    ai_ans_tts_path = queue.Queue()
    tr_aa = threading.Thread(target=tts_request_thread, args=(ai_ans.replace(";)", ")"), ai_ans_tts_path, ))
    tr_aa.start()

    if sa_enble:
        sar.join()
        emo_state = sa_ans.get()


    if read_chat_now:
        tr_cn.join()
        chat_now_tts_path = chat_now_tts_path.get()


    tr_aa.join()
    ai_ans_tts_path = ai_ans_tts_path.get()

    speaking_continue_count += 1

    with lock_subtitles_speak:
        subtitles_speak(
                chat_role,
                chat_now,
                ai_ans,
                ai_name,
                chat_now_tts_path,
                ai_ans_tts_path,
                emo_state,
                AIVT_VTSP_Status_authenticated=AIVT_VTSP_Status_authenticated
            )

    speaking_continue_count -= 1


    with lock_remove_file:
        def manage_files_by_count(file_path, file_max):
            try:
                file_max = int(file_max)
            except ValueError:
                file_max = 10
            if file_max < 0:
                file_max = 10

            files = [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]
            if len(files) <= file_max:
                return

            files.sort()
            while len(files) > file_max:
                os.remove(files[0])
                files.pop(0)

        file_path = "Audio/tts"
        file_max = 10
        manage_files_by_count(file_path, file_max)



def sa_request_thread(text, sa_ans):
    with lock_sa_requst:
        sa_ans.put(sa_nlp_api.Sentiment_Analysis_NLP(text, Emo_state_categories=vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]))


def tts_request_thread(tts_text, tts_path):
    global GUI_TTS_Using

    with lock_tts_request:
        def generate_unique_filename(file_path, file_name, file_extension):
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            base_filename = f"{timestamp}_{file_name}"
            full_filename = f"{base_filename}{file_extension}"
            full_path = os.path.join(file_path, full_filename)
            counter = 1

            while os.path.exists(full_path):
                full_filename = f"{base_filename}_{counter}{file_extension}"
                full_path = os.path.join(file_path, full_filename)
                counter += 1
            
            return full_path

        file_path = "Audio/tts"
        file_name = f"{GUI_TTS_Using}"
        if GUI_TTS_Using == "EdgeTTS":
            file_extension = ".mp3"
        elif GUI_TTS_Using == "OpenAITTS":
            file_extension = ".wav"
        else:
            file_extension = ".mp3"

        unique_filename = generate_unique_filename(file_path, file_name, file_extension)

        if GUI_TTS_Using == "EdgeTTS":
            output_path = unique_filename
            voice = edgeTTS.edgetts_parameters["voice"]
            pitch = edgeTTS.edgetts_parameters["pitch"]
            rate = edgeTTS.edgetts_parameters["rate"]
            volume = edgeTTS.edgetts_parameters["volume"]
            timeout = edgeTTS.edgetts_parameters["timeout"]

            ttsr = threading.Thread(
                target=edgeTTS.edgetts,
                kwargs={
                    "text":tts_text,
                    "output_path":output_path,
                    "voice":voice,
                    "pitch":pitch,
                    "rate":rate,
                    "volume":volume,
                    "timeout":timeout,
                    }
                )
            ttsr.start()

        elif GUI_TTS_Using == "OpenAITTS":
            output_path = unique_filename
            model = openaiTTS.openaitts_parameters["model"]
            voice = openaiTTS.openaitts_parameters["voice"]
            speed = openaiTTS.openaitts_parameters["speed"]
            format = openaiTTS.openaitts_parameters["format"]
            timeout = openaiTTS.openaitts_parameters["timeout"]

            ttsr = threading.Thread(
                target=openaiTTS.openaitts,
                kwargs={
                    "text":tts_text,
                    "output_path":output_path,
                    "model":model,
                    "voice":voice,
                    "speed":speed,
                    "format":format,
                    "timeout":timeout,
                    }
                )
            ttsr.start()

        else:
            output_path = unique_filename
            voice = edgeTTS.edgetts_parameters["voice"]
            pitch = edgeTTS.edgetts_parameters["pitch"]
            rate = edgeTTS.edgetts_parameters["rate"]
            volume = edgeTTS.edgetts_parameters["volume"]
            timeout = edgeTTS.edgetts_parameters["timeout"]

            ttsr = threading.Thread(
                target=edgeTTS.edgetts,
                kwargs={
                    "text":tts_text,
                    "output_path":output_path,
                    "voice":voice,
                    "pitch":pitch,
                    "rate":rate,
                    "volume":volume,
                    "timeout":timeout,
                    }
                )
            ttsr.start()

        ttsr.join()

        tts_path.put(unique_filename)
        return


def Subtitles_formatter_v3(text, max_length, english_char_length, base_line_count):
    def format_text(text, max_length, english_char_length, base_line_count):
        lines = [line for line in text.split('\n') if line.strip() != '']
        Predicted_lines = []
        for line in lines:
            while len(line) > max_length:
                Predicted_lines.append(line[:max_length])
                line = line[max_length:]
            Predicted_lines.append(line)
        
        Predicted_line_count = len(Predicted_lines)
        #print(f'\nPredicted line count: {Predicted_line_count}\n')

        if Predicted_line_count < base_line_count:
            line_count = base_line_count
        else:
            line_count = Predicted_line_count
        new_max_length = max_length * line_count / base_line_count
        #print(f'Iteration BASE: line_count={line_count}, new_max_length={new_max_length}')
        result = split_line_text(lines, math.ceil(new_max_length), english_char_length, line_count)
    
        iteration = 1
        prev_line_count = None
        #print(str(len(result) != line_count) + " -> len(result) != line_count")
        #print(str(prev_line_count is None or prev_line_count != line_count) + " -> (prev_line_count is None or prev_line_count != line_count)")
        #print(str(iteration < 10) + " -> iteration < 10")
        #print(str(lines_fit_check != -1) + " -> lines_fit_check != -1")
        #print("\n----------\n")
        while len(result) != line_count and (prev_line_count is None or prev_line_count != line_count) and iteration < 10:
            #print(f'Iteration {iteration}: line_count={line_count}, new_max_length={new_max_length}')
            prev_line_count = line_count
            lr = len(result)
            #print(f'len(result) {lr}\n')
            line_count = (len(result) + line_count) // 2
            new_max_length = max_length * line_count / base_line_count
            #print(f'Iteration {iteration}: line_count={line_count}, new_max_length={new_max_length}')
            result = split_line_text(lines, math.ceil(new_max_length), english_char_length, line_count)
            iteration += 1

        fix_iteration_line_count = (len(result) + line_count) // 2
        #print(f'fix_iteration_line_count {fix_iteration_line_count}')
        if fix_iteration_line_count < base_line_count:
            line_count = base_line_count
        else:
            line_count = len(result) + 1

        lr = len(result)
        #print(f'len(result) {lr}')
        #print(f'line_count {line_count}')
        #if len(result) == line_count:
            #line_count = lr + 1
        #line_count = lr + 1

        new_max_length = max_length * line_count / base_line_count
        #print(f'fix iteration parameters: line_count={line_count}, new_max_length={new_max_length}')
        result = split_line_text(lines, math.ceil(new_max_length), english_char_length, line_count)
    
        final_iteration_line_count = len(result)
        #print(f'\nFinal result: line_count={final_iteration_line_count}, max_length={new_max_length}')
        #print(f'{result}')
        #print("\n----------\n")
        return '\n'.join(result)
    
    def split_line_text(lines: str, max_length: int, english_char_length: float, line_count: int):
        global lines_fit_check
        result = []
        lines_fit_check = 0
        for line in lines:
        
            while len(line) > 0:
                #print(line)
                actual_length = 0
                split_index = 0
            
                for i, char in enumerate(line):
                    if re.match(r' [a-zA-Z]\(\)\[\]{}<>:;=，。！？；～,!?~;【】「」『』〔〕()┐┌ლ✧⁄／╧ﾉﾒ彡o｡丿•̥̥̥`´ﾟゞو', char):
                        actual_length += english_char_length
                    else:
                        actual_length += 1
                    if actual_length > max_length:
                        #print("----------")
                        #print(f'max_length {max_length}')
                        #print(f'actual_length {actual_length}')
                        break
                    split_index = i + 1

                if actual_length > max_length:
                    punctuation_index = [i for i in range(split_index) if line[i] in ' ，。！？；～,!?~;【】「」『』〔〕()┐┌ლ✧⁄＼／╧ﾉﾒ彡o｡つ丿ㄟㄏ︴Ψ']
                    if punctuation_index:
                        if line[punctuation_index[-1]] in '【「『〔((┐┌ㄟ＼': #:：】」』〕)┌ლ✧⁄╧╧ﾉﾒ彡o｡丿
                            split_index = punctuation_index[-1]
                        else:
                            split_index = punctuation_index[-1] + 1             
                    
                    #print(f'split_index {split_index}')
                    result.append(line[:split_index])
                    line = line[split_index:].lstrip()
                else:
                    result.append(line)
                    line = ""
                    lines_fit_check += 1
                    #print(f'lines_fit_check {lines_fit_check}')

        if lines_fit_check == line_count:
            lines_fit_check = -1
            #print(f'lines_fit_check {lines_fit_check}')
        #print("\n----------\n")
        return result

    return format_text(text, max_length, english_char_length, base_line_count)

def Subtitles_formatter_v2(text, max_length, english_char_length, base_line_count):
    def find_natural_break(line, max_length):
        total_length = 0
        last_good_break = 0
        for i, char in enumerate(line):
            char_length = english_char_length if char.isalpha() else 1
            total_length += char_length

            if char in ' ,.!?;:':
                last_good_break = i + 1

            if total_length > max_length:
                if last_good_break > 0:
                    return last_good_break
                break

        return last_good_break if last_good_break > 0 else i
    
    def process_line_splits(lines, max_length):
        new_lines = []
        for line in lines:
            while len(line) > max_length:
                break_index = find_natural_break(line, max_length)
                if break_index == 0:
                    break_index = len(line)
                new_lines.append(line[:break_index].strip())
                line = line[break_index:].lstrip()
            new_lines.append(line.strip())
        return new_lines
    
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if line.strip() == '':
            continue
        processed_lines.append(line.strip())
    
    iteration = 0
    while iteration < 10:
        new_lines = process_line_splits(processed_lines, max_length)
        if len(new_lines) <= base_line_count or len(new_lines) == len(processed_lines):
            break
        max_length = int(max_length * (len(new_lines) / base_line_count))
        processed_lines = new_lines
        iteration += 1

    return '\n'.join(new_lines)



def subtitles_speak_sleep(stime):
    time.sleep(stime)

def subtitles_speak(
        chat_role,
        chat_now,
        ai_ans,
        ai_name,
        chat_now_tts_path,
        ai_ans_tts_path,
        emo_state,
        AIVT_VTSP_Status_authenticated=False,
        command=None
    ):
    global GUI_Setting_read_chat_now, GUI_VTSP_wait_until_hotkeys_complete
    global speaking_continue_count, speaking_continue_vtsp_hkns


    show_chat_now = (chat_role in ["user", "user_mic", "youtube_chat", "twitch_chat"])
    read_chat_now = show_chat_now and ((GUI_Setting_read_chat_now and chat_role in ["user", "user_mic"]) or (live_chat.Live_chat_parameters["yt_live_chat_read_chat_now"] and chat_role == "youtube_chat")) or (live_chat.Live_chat_parameters["tw_live_chat_read_chat_now"] and chat_role == "twitch_chat")


    obs_show_chat_now = show_chat_now and obsws.OBS_Connected and obsws.OBS_chat_now_sub_parameters["show"]
    obs_show_ai_ans = obsws.OBS_Connected and obsws.OBS_ai_ans_sub_parameters["show"]

    obs_sub_formatter = obsws.OBS_subtitles_parameters["subtitles_formatter"]
    obs_sub_formatter_ver = obsws.OBS_subtitles_parameters["subtitles_formatter_version"]

    obs_chat_now_sub_name = obsws.OBS_chat_now_sub_parameters["sub_name"]
    obs_chat_now_show_sub_filter_names = obsws.OBS_chat_now_sub_parameters["show_sub_filter_names"]
    obs_chat_now_hide_sub_filter_names = obsws.OBS_chat_now_sub_parameters["hide_sub_filter_names"]

    obs_ai_ans_sub_name = obsws.OBS_ai_ans_sub_parameters["sub_name"]
    obs_ai_ans_show_sub_filter_names = obsws.OBS_ai_ans_sub_parameters["show_sub_filter_names"]
    obs_ai_ans_hide_sub_filter_names = obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_names"]

    vtsp_hk_enble = AIVT_VTSP_Status_authenticated
    vtsp_trigger_first = vtsp.AIVT_hotkeys_parameters["trigger_first"]



    if vtsp_hk_enble and emo_state != "":
        emo_kn = vtsp.AIVT_hotkeys_parameters[f"{emo_state}_kn"]
        vtsp_hotkey_names = vtsp.get_hotkey_names(emo_kn)

    elif vtsp_hk_enble:
        emo = random.choice(vtsp.AIVT_hotkeys_parameters["Emo_state_categories"])
        print(f"VTSP Random Emotion State: {emo}")
        emo_kn = vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"]
        vtsp_hotkey_names = vtsp.get_hotkey_names(emo_kn)


    if vtsp_hk_enble and vtsp_trigger_first:
        if speaking_continue_vtsp_hkns:
            o_vtsp_hkns = set(vtsp_hotkey_names["all"])
            p_vtsp_hkns = set(speaking_continue_vtsp_hkns)
            d_vtsp_hkns = o_vtsp_hkns & p_vtsp_hkns

            no_vtsp_hkns = [item for item in vtsp_hotkey_names["all"] if item not in d_vtsp_hkns]
            np_vtsp_hkns = [item for item in speaking_continue_vtsp_hkns if item not in d_vtsp_hkns]

            n_vtsp_hkns = np_vtsp_hkns + no_vtsp_hkns

        else:
            n_vtsp_hkns = vtsp_hotkey_names["all"]

        vtsp_ht = threading.Thread(
                target=vtsp.VTSP_Hotkey_Names_Trigger,
                kwargs={"hotkey_names_list": n_vtsp_hkns},
            )
        vtsp_ht.start()
        if GUI_VTSP_wait_until_hotkeys_complete:
            vtsp_ht.join()

    speaking_continue_vtsp_hkns = []



    if obs_show_chat_now:
        if obs_sub_formatter:
            lines = chat_now.splitlines()
            lines = [line for line in lines if line.strip() != '']
            obs_chat_now = '\n'.join(lines)

            if obs_sub_formatter_ver == "v3":
                obs_chat_now = Subtitles_formatter_v3(
                    obs_chat_now,
                    obsws.OBS_chat_now_sub_parameters["sub_max_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_english_char_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_base_line_count"]
                    )

            elif obs_sub_formatter_ver == "v2":
                obs_chat_now = Subtitles_formatter_v2(
                    obs_chat_now,
                    obsws.OBS_chat_now_sub_parameters["sub_max_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_english_char_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_base_line_count"]
                    )

            else:
                obs_chat_now = Subtitles_formatter_v3(
                    obs_chat_now,
                    obsws.OBS_chat_now_sub_parameters["sub_max_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_english_char_length"],
                    obsws.OBS_chat_now_sub_parameters["sub_base_line_count"]
                    )

        obst_cn_st = threading.Thread(
            target=obsws.Set_Source_Text,
            args=(obs_chat_now_sub_name, obs_chat_now)
            )
        obst_cn_st.start()
        obst_cn_st.join()

        if len(obs_chat_now_show_sub_filter_names) > 0:
            obst_cn_s = threading.Thread(
                target=obsws.Set_Source_Filter_Enabled,
                args=(
                    obs_chat_now_sub_name,
                    obs_chat_now_show_sub_filter_names,
                    True,
                    ),
                kwargs={
                    "start_delay":obsws.OBS_chat_now_sub_parameters["show_sub_filter_start_delay"],
                    "end_delay":obsws.OBS_chat_now_sub_parameters["show_sub_filter_end_delay"],
                    },
                )
            obst_cn_s.start()

        sub_time = obsws.OBS_chat_now_sub_parameters["sub_time"]
        if sub_time > 0:
            sss = threading.Thread(target=subtitles_speak_sleep, args=(sub_time, ))
            sss.start()



    if read_chat_now:
        chat_now_read = threading.Thread(target=speaking, args=(chat_now_tts_path, ))  
        chat_now_read.start()
        chat_now_read.join()



    if obs_show_chat_now:
        if sub_time > 0:
            sss.join()

    if obs_show_chat_now:
        time.sleep(obsws.OBS_chat_now_sub_parameters["sub_end_delay"])

    if vtsp_hk_enble and not vtsp_trigger_first:
        vtsp_ht = threading.Thread(
                target=vtsp.VTSP_Hotkey_Names_Trigger,
                kwargs={"hotkey_names_list": vtsp_hotkey_names["all"]}
            )
        vtsp_ht.start()
        if GUI_VTSP_wait_until_hotkeys_complete:
            vtsp_ht.join()



    if obs_show_chat_now:
        if obsws.OBS_chat_now_sub_parameters["clear"]:
            obst_cn_st = threading.Thread(
                target=obsws.Set_Source_Text,
                args=(obs_chat_now_sub_name, "")
                )
            obst_cn_st.start()
            obst_cn_st.join()
        
        if len(obs_chat_now_hide_sub_filter_names) > 0:
            obst_cn_fe_sd = threading.Thread(
                target=obsws.Set_Source_Filter_Enabled,
                args=(
                    obs_chat_now_sub_name,
                    obs_chat_now_hide_sub_filter_names,
                    True,
                    ),
                kwargs={
                    "start_delay":obsws.OBS_chat_now_sub_parameters["hide_sub_filter_start_delay"],
                    "end_delay":obsws.OBS_chat_now_sub_parameters["hide_sub_filter_end_delay"],
                    },
                )
            obst_cn_fe_sd.start()



    if obs_show_ai_ans:
        
        if obsws.OBS_ai_ans_sub_parameters["remove_original_text_wrap"]:
            obs_ai_ans = ai_ans.replace('\n', ' ')
        else:
            obs_ai_ans = ai_ans

        if obs_sub_formatter_ver == "v3":
            ai_ans_formatted = Subtitles_formatter_v3(
                obs_ai_ans,
                obsws.OBS_ai_ans_sub_parameters["sub_max_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_english_char_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_base_line_count"]
                )

        elif obs_sub_formatter_ver == "v2":
            ai_ans_formatted = Subtitles_formatter_v2(
                obs_ai_ans,
                obsws.OBS_ai_ans_sub_parameters["sub_max_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_english_char_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_base_line_count"]
                )

        else:
            ai_ans_formatted = Subtitles_formatter_v3(
                obs_ai_ans,
                obsws.OBS_ai_ans_sub_parameters["sub_max_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_english_char_length"],
                obsws.OBS_ai_ans_sub_parameters["sub_base_line_count"]
                )

        obst_aa_st = threading.Thread(
            target=obsws.Set_Source_Text,
            args=(obs_ai_ans_sub_name, ai_ans_formatted)
            )
        obst_aa_st.start()
        obst_aa_st.join()



    ai_ans_read = threading.Thread(target=speaking, args=(ai_ans_tts_path, ))



    if obs_show_ai_ans:
        if len(obs_ai_ans_show_sub_filter_names) > 0:
            obst_aa_fe_s = threading.Thread(
                target=obsws.Set_Source_Filter_Enabled,
                args=(
                    obs_ai_ans_sub_name,
                    obs_ai_ans_show_sub_filter_names,
                    True,
                    ),
                kwargs={
                    "start_delay":obsws.OBS_ai_ans_sub_parameters["show_sub_filter_start_delay"],
                    "end_delay":obsws.OBS_ai_ans_sub_parameters["show_sub_filter_end_delay"],
                    },
                )
            obst_aa_fe_s.start()



    ai_ans_read.start()
    ai_ans_read.join()



    if obs_show_ai_ans:
        time.sleep(obsws.OBS_ai_ans_sub_parameters["sub_end_delay"])



    if vtsp_hk_enble and (speaking_continue_count <= 1 or not vtsp_trigger_first):
        idle_kn = vtsp.get_hotkey_names(vtsp.AIVT_hotkeys_parameters["idle_ani"], command="idle_ani")
        vtsp_hkns = idle_kn["r_ani"] + vtsp_hotkey_names["all_exp"]

        vtsp_ht = threading.Thread(
            target=vtsp.VTSP_Hotkey_Names_Trigger,
            kwargs={"hotkey_names_list": vtsp_hkns}
        )
        vtsp_ht.start()

    elif vtsp_hk_enble:
        speaking_continue_vtsp_hkns = vtsp_hotkey_names["all_exp"]


    if vtsp_hk_enble and GUI_VTSP_wait_until_hotkeys_complete:
        vtsp_ht.join()


    if obs_show_ai_ans:
        if obsws.OBS_ai_ans_sub_parameters["clear"]:
            obst_aa_st = threading.Thread(
                target=obsws.Set_Source_Text,
                args=(obs_ai_ans_sub_name, "")
                )
            obst_aa_st.start()
            obst_aa_st.join()

        if len(obs_ai_ans_hide_sub_filter_names) > 0:
            obst_aa_fe_h = threading.Thread(
                target=obsws.Set_Source_Filter_Enabled,
                args=(
                    obs_ai_ans_sub_name,
                    obs_ai_ans_hide_sub_filter_names,
                    True,
                    ),
                kwargs={
                    "start_delay":obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_start_delay"],
                    "end_delay":obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_end_delay"],
                    },
                )
            obst_aa_fe_h.start()
    


    try:
        w_name, w_text = chat_now.split(" : ", 1)
        w_chat_now = f"{w_name} :\n{w_text}"
    except:
        w_chat_now = chat_now
    w_ai_ans = f"{ai_name} :\n{ai_ans}"
    wch = threading.Thread(target=write_conversation_history, args=(w_chat_now, w_ai_ans))
    wch.start()



def speaking(audio_path, start_delay=0, end_delay=0):
    ai_voice_output_device_name = Play_Audio.play_audio_parameters["ai_voice_output_device_name"]

    time.sleep(start_delay)

    try:
        Play_Audio.PlayAudio(audio_path, ai_voice_output_device_name)
    
    except Exception as e:
        print(f"!!! Play Audio Error !!!\n{e}")

    time.sleep(end_delay)



lock_write_conversation_history = threading.Lock()

def write_conversation_history(chat_now, subtitles):
    with lock_write_conversation_history:
        ConversationHistory_path = f"Text_files/ConversationHistory/{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"

        with open(ConversationHistory_path, "a", encoding="utf-8") as outfile:
            outfile.write(f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %p')}\n")
            outfile.write(f"\n{chat_now}\n")
            outfile.write(f"\n{subtitles}\n")
            outfile.write("\n------------------------------\n")










def AIVT_VTSP_Idle_Animation():
    global speaking_continue_count
    if vtsp.AIVT_VTSP_Status["authenticated"]:
        kn = vtsp.get_hotkey_names(vtsp.AIVT_hotkeys_parameters["idle_ani"], command="idle_ani")
        vtsp_ht = threading.Thread(
                target=vtsp.VTSP_Hotkey_Names_Trigger,
                kwargs={"hotkey_names_list": kn["r_ani"]}
            )
        vtsp_ht.start()

        t = 0

        while vtsp.AIVT_VTSP_Status["authenticated"]:
            while speaking_continue_count > 0:
                t = 0
                time.sleep(0.1)

            if t >= 59:
                t = 0

                kn = vtsp.get_hotkey_names(vtsp.AIVT_hotkeys_parameters["idle_ani"], command="idle_ani")
                vtsp_ht = threading.Thread(
                        target=vtsp.VTSP_Hotkey_Names_Trigger,
                        kwargs={"hotkey_names_list": kn["r_ani"]}
                    )
                vtsp_ht.start()

            time.sleep(1)
            t += 1




