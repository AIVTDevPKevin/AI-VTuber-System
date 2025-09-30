import sys
import os
import threading
import multiprocessing
import queue
import time
import configparser

from PySide6 import QtWidgets, QtCore, QtGui

import GUI_control_panel.GUI_py.AI_Vtuber_control_panel_ui_pysd6 as gui
import AI_Vtuber_UI as aivtui
import VTubeStudioPlugin.VTubeStudioPlugin as vtsp
import OBS_websocket.OBS_websocket as obsws
import OpenAI.whisper.OpenAI_Whisper as whisper
import OpenAI.whisper.OpenAI_Whisper_API as whisper_api
import OpenAI.gpt.OpenAI_GPT_API as gpt
import TextToSpeech.edgeTTS as edgetts
import TextToSpeech.OpenAITTS as openaitts
import Google.gemini.GoogleAI_Gemini_API as gemini
import Sentiment_Analysis.NLP_API as sa_nlp
import Live_Chat.Live_Chat as live_chat
import Play_Audio as plau
import Mic_Record as mcrc
from My_Tools.AIVT_print import aprint


print("\n" + "="*29 + "[ 開發者提示 ]" + "="*29)
print("您可能會在啟動時看到多則關於 'name shadows' 的 UserWarning。")
print("此警告源於第三方套件 (google-genai)，並非本應用程式的錯誤。")
print("請安心忽略此訊息，它不會影響程式的任何功能。")
print("="*72 + "\n")
print("="*29 + "[ DEVELOPER NOTICE ]" + "="*29)
print("You may see multiple UserWarnings regarding 'name shadows' on startup.")
print("This warning originates from a third-party library (google-genai) and is not an error in this application.")
print("Please feel free to ignore this message as it does not affect any functionality.")
print("="*78 + "\n")










GUI_config = configparser.ConfigParser()
GUI_config_path = "GUI_control_panel/GUI_config.ini"

class AI_Vtuber_GUI(gui.Ui_MainWindow, QtWidgets.QMainWindow, QtWidgets.QPushButton): #, QtWidgets.QAction
    # Initialize GUI
    def __init__(self):
        super().__init__()
        # Set up GUI
        self.setupUi(self)
        global GUI_config, GUI_config_path

        # Make the icon show correctly
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("GUI_control_panel\GUI_icon\AI_Vtuber_GUI_control_panel_01.ico"))
        self.setWindowIcon(icon)
        self.MW_Tab.setCurrentIndex(0)
        ### Make the icon show correctly





        # load gui config
        GUI_config.read(GUI_config_path, encoding="utf-8")
        ### load gui config





        # Show chat role
        enble = GUI_config["Main"]["show_chat_role"] == "True"
        self.CH_cB_Show_chat_role.setChecked(enble)
        GUI_config["Main"]["show_chat_role"] = str(enble)
        ### Show chat role





        # User name
        self.St_LE_User_Name.setText(str(GUI_config["Setting"]["user_name"]))
        aivtui.GUI_User_Name = str(GUI_config["Setting"]["user_name"])
        ### User name


        # character
        aivtui.Load_AIVT_Character()
        for name in aivtui.AIVT_Character_Names:
            self.St_CB_Character_select.addItem(name)

        GUI_Setting_Character = str(GUI_config["Setting"]["character"])
        if GUI_Setting_Character in aivtui.AIVT_Character_Names:
            self.St_CB_Character_select.setCurrentText(GUI_Setting_Character)
        else:
            GUI_Setting_Character = self.St_CB_Character_select.currentText()
            GUI_config["Setting"]["character"] = GUI_Setting_Character

        aivtui.AIVT_Using_character = GUI_Setting_Character
        ### character


        # tab position
        tabp = GUI_config["Setting"]["tab_position"]
        self.St_CB_Tab_position.setCurrentText(tabp)
        tab_position_map = {
            "North": QtWidgets.QTabWidget.North,
            "South": QtWidgets.QTabWidget.South,
            "West": QtWidgets.QTabWidget.West,
            "East": QtWidgets.QTabWidget.East
        }
        self.MW_Tab.setTabPosition(tab_position_map[tabp])
        ### tab position


        # ai voice output device name
        Available_output_device_list = plau.Get_available_output_devices_List()
        for name in Available_output_device_list:
            self.St_CB_AI_Voice_output_devices.addItem(name)

        AI_Voice_output_devices_name = str(GUI_config["Setting"]["ai_voice_output_device_name"])
        if AI_Voice_output_devices_name in Available_output_device_list:
            self.St_CB_AI_Voice_output_devices.setCurrentText(AI_Voice_output_devices_name)
        else:
            AI_Voice_output_devices_name = self.St_CB_AI_Voice_output_devices.currentText()
            GUI_config["Setting"]["ai_voice_output_device_name"] = AI_Voice_output_devices_name

        plau.play_audio_parameters["ai_voice_output_device_name"] = AI_Voice_output_devices_name
        ### ai voice output device name


        # user mic input device name
        Available_input_device_list = mcrc.Get_available_input_devices_List()
        for name in Available_input_device_list:
            self.St_CB_User_Mic_iutput_devices.addItem(name)

        User_Mic_input_devices_name = str(GUI_config["Setting"]["user_mic_input_device_name"])
        if User_Mic_input_devices_name in Available_input_device_list:
            self.St_CB_User_Mic_iutput_devices.setCurrentText(User_Mic_input_devices_name)
        else:
            User_Mic_input_devices_name = self.St_CB_User_Mic_iutput_devices.currentText()
            GUI_config["Setting"]["user_mic_input_device_name"] = User_Mic_input_devices_name

        mcrc.User_Mic_parameters["input_device_name"] = User_Mic_input_devices_name
        ### user mic input device name


        # read user chat
        enble = str(GUI_config["Setting"]["read_user_chat"]) == "True"
        aivtui.GUI_Setting_read_chat_now = enble
        self.St_cB_Read_user_chat.setChecked(enble)
        ### read user chat

        
        # user mic hotkey 1 using
        enble = str(GUI_config["Setting"]["user_mic_hotkey_1_using"]) == "True"
        mcrc.user_mic_status["mic_hotkey_1_using"] = enble
        self.St_cB_User_mic_hotkey1.setChecked(enble)
        mcrc.user_mic_status["mic_hotkeys_using"] = enble
        ### user mic hotkey 1 using


        # user mic hotkey 1
        hotkey = str(GUI_config["Setting"]["user_mic_hotkey_1"])
        mcrc.user_mic_status["mic_hotkey_1"] = hotkey
        self.St_cB_User_mic_hotkey1.setText(f"Mic Hotkey 1 : {hotkey}")
        ### user mic hotkey 1


        # user mic hotkey 2 using
        enble = str(GUI_config["Setting"]["user_mic_hotkey_2_using"]) == "True"
        mcrc.user_mic_status["mic_hotkey_2_using"] = enble
        self.St_cB_User_mic_hotkey2.setChecked(enble)
        if not mcrc.user_mic_status["mic_hotkey_1_using"]:
            mcrc.user_mic_status["mic_hotkeys_using"] = enble
        ### user mic hotkey 2 using


        # user mic hotkey 2
        hotkey = str(GUI_config["Setting"]["user_mic_hotkey_2"])
        mcrc.user_mic_status["mic_hotkey_2"] = hotkey
        self.St_cB_User_mic_hotkey2.setText(f"Mic Hotkey 2 : {hotkey}")
        ### user mic hotkey 2



        # doing now
        wdn = str(GUI_config["Setting"]["doing_now"])
        aivtui.GUI_LLM_parameters["wdn_prompt"] = wdn
        self.St_TE_Doing_now.setPlainText(wdn)
        ### doing now





        # YouTube channel name
        p = "yt"
        name = str(GUI_config["Live_Chat"][f"{p}_channel_name"]).strip()
        self.LC_LE_yt_channel_name.setText(name)
        live_chat.Live_chat_parameters[f"{p}_channel_name"] = name
        GUI_config["Live_Chat"][f"{p}_channel_name"] = name
        ### YouTube channel name


        # YouTube live id
        p = "yt"
        live_id = str(GUI_config["Live_Chat"][f"{p}_live_id"]).strip()
        self.LC_LE_yt_live_id.setText(live_id)
        live_chat.Live_chat_parameters[f"{p}_live_id"] = live_id
        GUI_config["Live_Chat"][f"{p}_live_id"] = live_id
        ### YouTube live id


        # YouTube response chatroom
        p = "yt"
        enble = GUI_config["Live_Chat"][f"{p}_response_chatroom"] == "True"
        self.LC_cB_yt_chatroom.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_chatroom"] = enble
        GUI_config["Live_Chat"][f"{p}_response_chatroom"] = str(enble)
        ### YouTube response chatroom


        # YouTube live chat read chat now
        p = "yt"
        enble = GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] == "True"
        self.LC_cB_yt_read_chat_now.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_live_chat_read_chat_now"] = enble
        GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] = str(enble)
        ### YouTube live chat read chat now


        # YouTube response owner
        p = "yt"
        enble = GUI_config["Live_Chat"][f"{p}_response_owner"] == "True"
        self.LC_cB_yt_owner.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_owner"] = enble
        GUI_config["Live_Chat"][f"{p}_response_owner"] = str(enble)
        ### YouTube response owner


        # YouTube response vip
        p = "yt"
        enble = GUI_config["Live_Chat"][f"{p}_response_vip"] == "True"
        self.LC_cB_yt_vip.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_vip"] = enble
        GUI_config["Live_Chat"][f"{p}_response_vip"] = str(enble)
        ### YouTube response vip


        # YouTube response individual
        p = "yt"
        enble = GUI_config["Live_Chat"][f"{p}_response_individual"] == "True"
        self.LC_cB_yt_response_individual.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_individual"] = enble
        GUI_config["Live_Chat"][f"{p}_response_individual"] = str(enble)
        ### YouTube response individual


        # YouTube wait list max
        p = "yt"
        num = int(GUI_config["Live_Chat"][f"{p}_wait_list_max"])
        self.LC_SB_yt_chat_max_wait_list.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_wait_list_max"] = num
        GUI_config["Live_Chat"][f"{p}_wait_list_max"] = str(num)
        ### YouTube wait list max


        # YouTube chat max tokens
        p = "yt"
        num = int(GUI_config["Live_Chat"][f"{p}_chat_max_tokens"])
        self.LC_SB_yt_chat_max_tokens.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_chat_max_tokens"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_tokens"] = str(num)
        ### YouTube chat max tokens


        # YouTube chat max response
        p = "yt"
        num = int(GUI_config["Live_Chat"][f"{p}_chat_max_response"])
        self.LC_SB_yt_chat_max_response.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_chat_max_response"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_response"] = str(num)
        ### YouTube chat max response


        # YouTube live chat vip names
        p = "yt"
        text = str(GUI_config["Live_Chat"][f"{p}_live_chat_vip_names"])
        self.LC_TE_yt_vip_names.setPlainText(text)
        live_chat.Live_chat_parameters[f"{p}_live_chat_vip_names"] = [name.strip() for name in text.split("/") if name.strip()]
        ### YouTube live chat vip names


        # YouTube yt live chat ban names
        p = "yt"
        text = str(GUI_config["Live_Chat"][f"{p}_live_chat_ban_names"])
        self.LC_TE_yt_ban_names.setPlainText(text)
        live_chat.Live_chat_parameters[f"{p}_live_chat_ban_names"] = [name.strip() for name in text.split("/") if name.strip()]
        ### YouTube live chat ban names



        # Twitch channel name
        p = "tw"
        name = str(GUI_config["Live_Chat"][f"{p}_channel_name"]).strip()
        self.LC_LE_tw_channel_name.setText(name)
        live_chat.Live_chat_parameters[f"{p}_channel_name"] = name
        GUI_config["Live_Chat"][f"{p}_channel_name"] = name
        ### Twitch channel name


        # Twitch response chatroom
        p = "tw"
        enble = GUI_config["Live_Chat"][f"{p}_response_chatroom"] == "True"
        self.LC_cB_tw_chatroom.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_chatroom"] = enble
        GUI_config["Live_Chat"][f"{p}_response_chatroom"] = str(enble)
        ### Twitch response chatroom


        # Twitch live chat read chat now
        p = "tw"
        enble = GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] == "True"
        self.LC_cB_tw_read_chat_now.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_live_chat_read_chat_now"] = enble
        GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] = str(enble)
        ### Twitch live chat read chat now


        # Twitch response owner
        p = "tw"
        enble = GUI_config["Live_Chat"][f"{p}_response_owner"] == "True"
        self.LC_cB_tw_owner.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_owner"] = enble
        GUI_config["Live_Chat"][f"{p}_response_owner"] = str(enble)
        ### Twitch response owner


        # Twitch response vip
        p = "tw"
        enble = GUI_config["Live_Chat"][f"{p}_response_vip"] == "True"
        self.LC_cB_tw_vip.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_vip"] = enble
        GUI_config["Live_Chat"][f"{p}_response_vip"] = str(enble)
        ### Twitch response vip


        # Twitch response individual
        p = "tw"
        enble = GUI_config["Live_Chat"][f"{p}_response_individual"] == "True"
        self.LC_cB_tw_response_individual.setChecked(enble)
        live_chat.Live_chat_parameters[f"{p}_response_individual"] = enble
        GUI_config["Live_Chat"][f"{p}_response_individual"] = str(enble)
        ### Twitch response individual


        # Twitch wait list max
        p = "tw"
        num = int(GUI_config["Live_Chat"][f"{p}_wait_list_max"])
        self.LC_SB_tw_chat_max_wait_list.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_wait_list_max"] = num
        GUI_config["Live_Chat"][f"{p}_wait_list_max"] = str(num)
        ### Twitch wait list max


        # Twitch chat max tokens
        p = "tw"
        num = int(GUI_config["Live_Chat"][f"{p}_chat_max_tokens"])
        self.LC_SB_tw_chat_max_tokens.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_chat_max_tokens"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_tokens"] = str(num)
        ### Twitch chat max tokens


        # Twitch chat max response
        p = "tw"
        num = int(GUI_config["Live_Chat"][f"{p}_chat_max_response"])
        self.LC_SB_tw_chat_max_response.setValue(num)
        live_chat.Live_chat_parameters[f"{p}_chat_max_response"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_response"] = str(num)
        ### Twitch chat max response


        # Twitch live chat vip names
        p = "tw"
        text = str(GUI_config["Live_Chat"][f"{p}_live_chat_vip_names"])
        self.LC_TE_tw_vip_names.setPlainText(text)
        live_chat.Live_chat_parameters[f"{p}_live_chat_vip_names"] = [name.strip() for name in text.split("/") if name.strip()]
        ### Twitch live chat vip names


        # Twitch yt live chat ban names
        p = "tw"
        text = str(GUI_config["Live_Chat"][f"{p}_live_chat_ban_names"])
        self.LC_TE_tw_ban_names.setPlainText(text)
        live_chat.Live_chat_parameters[f"{p}_live_chat_ban_names"] = [name.strip() for name in text.split("/") if name.strip()]
        ### Twitch live chat ban names





        # LLM using
        llm_using = GUI_config["LLM"]["using"]
        
        if llm_using == "Gemini":
            self.LLM_RB_Gemini.setChecked(True)
        elif llm_using == "GPT":
            self.LLM_RB_GPT.setChecked(True)
        else:
            llm_using = "Gemini"
            GUI_config["LLM"]["using"] = llm_using
            self.LLM_RB_Gemini.setChecked(True)
        
        aivtui.GUI_LLM_parameters["model"] = llm_using
        ### LLM using


        # LLM Instruction enhance
        instruction_enhance = GUI_config["LLM"]["instruction_enhance"] == "True"
        aivtui.GUI_LLM_parameters["instruction_enhance"] = instruction_enhance
        self.LLM_cB_Instruction_enhance.setChecked(instruction_enhance)

        prompt = aivtui.get_instruction_enhance_prompt(aivtui.AIVT_Using_character)
        self.LLM_TE_Instruction_enhance.setPlainText(prompt)
        aivtui.GUI_LLM_parameters["instruction_enhance_prompt"] = prompt
        ### LLM Instruction enhance


        # LLM Instruction enhance i
        instruction_enhance_i = int(GUI_config["LLM"]["instruction_enhance_i"])
        aivtui.GUI_LLM_parameters["instruction_enhance_i"] = instruction_enhance_i
        self.LLM_SB_Instruction_enhance.setValue(instruction_enhance_i)
        ### LLM Instruction enhance i



        # LLM Gemini model
        gemini_model_names_list = [name for name in gemini.gemini_models_max_input_tokens.keys()]
        for name in gemini_model_names_list:
            self.LLM_CB_Ge_Model.addItem(name)

        gemini_model = str(GUI_config["LLM_Gemini"]["model"])
        if gemini_model in gemini_model_names_list:
            self.LLM_CB_Ge_Model.setCurrentText(gemini_model)
        else:
            gemini_model = self.LLM_CB_Ge_Model.currentText()
            GUI_config["LLM_Gemini"]["model"] = gemini_model

        gemini.gemini_parameters["model"] = gemini_model
        ### LLM Gemini model


        # LLM Gemini max input tokens
        gemini_max_input_tokens = int(GUI_config["LLM_Gemini"]["max_input_tokens"])
        gemini_models_max_input_tokens = gemini.gemini_models_max_input_tokens[gemini.gemini_parameters["model"]]
        self.LLM_SB_Ge_Max_input_tokens.setMaximum(gemini_models_max_input_tokens)

        if gemini_max_input_tokens < 1024:
            gemini_max_input_tokens = 1024
        elif gemini_max_input_tokens > gemini_models_max_input_tokens:
            gemini_max_input_tokens = gemini_models_max_input_tokens

        GUI_config["LLM_Gemini"]["max_input_tokens"] = str(gemini_max_input_tokens)
        self.LLM_SB_Ge_Max_input_tokens.setValue(gemini_max_input_tokens)
        gemini.gemini_parameters["max_input_tokens"] = gemini_max_input_tokens
        ### LLM Gemini max input tokens


        # LLM Gemini max output tokens
        gemini_max_output_tokens = int(GUI_config["LLM_Gemini"]["max_output_tokens"])
        gemini_models_max_output_tokens = gemini.gemini_models_max_output_tokens[gemini.gemini_parameters["model"]]
        self.LLM_SB_Ge_Max_output_tokens.setMaximum(gemini_models_max_output_tokens)

        if gemini_max_output_tokens < 128:
            gemini_max_output_tokens = 128
        elif gemini_max_output_tokens > gemini_models_max_output_tokens:
            gemini_max_output_tokens = gemini_models_max_output_tokens

        GUI_config["LLM_Gemini"]["max_output_tokens"] = str(gemini_max_output_tokens)
        self.LLM_SB_Ge_Max_output_tokens.setValue(gemini_max_output_tokens)
        gemini.gemini_parameters["max_output_tokens"] = gemini_max_output_tokens
        ### LLM Gemini max output tokens


        # LLM Gemini temperature
        gemini_temperature = round(float(GUI_config["LLM_Gemini"]["temperature"]), 2)

        if gemini_temperature < 0:
            gemini_temperature = 0.00
        elif gemini_temperature > 1:
            gemini_temperature = 1.00

        GUI_config["LLM_Gemini"]["temperature"] = str(gemini_temperature)
        self.LLM_DSB_Ge_Temperature.setValue(gemini_temperature)
        gemini.gemini_parameters["temperature"] = gemini_temperature
        ### LLM Gemini temperature


        # LLM Gemini timeout
        gemini_timeout = int(GUI_config["LLM_Gemini"]["timeout"])

        if gemini_timeout < 5:
            gemini_timeout = 5
        elif gemini_timeout > 60:
            gemini_timeout = 60

        GUI_config["LLM_Gemini"]["timeout"] = str(gemini_timeout)
        self.LLM_SB_Ge_Timeout.setValue(gemini_timeout)
        gemini.gemini_parameters["timeout"] = gemini_timeout
        ### LLM Gemini timeout


        # LLM Gemini retry
        gemini_retry = int(GUI_config["LLM_Gemini"]["retry"])

        if gemini_retry < 1:
            gemini_retry = 1
        elif gemini_retry > 10:
            gemini_retry = 10

        GUI_config["LLM_Gemini"]["retry"] = str(gemini_retry)
        self.LLM_SB_Ge_Retry.setValue(gemini_retry)
        gemini.gemini_parameters["retry"] = gemini_retry
        ### LLM Gemini retry



        # LLM GPT model
        gpt_model_names_list = [name for name in gpt.gpt_models_max_input_tokens.keys()]
        for name in gpt_model_names_list:
            self.LLM_CB_GPT_Model.addItem(name)

        gpt_model = str(GUI_config["LLM_GPT"]["model"])
        if gpt_model in gpt_model_names_list:
            self.LLM_CB_GPT_Model.setCurrentText(gpt_model)
        else:
            gpt_model = self.LLM_CB_GPT_Model.currentText()
            GUI_config["LLM_GPT"]["model"] = gpt_model

        gpt.gpt_parameters["model"] = gpt_model
        ### LLM GPT model


        # LLM GPT max input tokens
        gpt_max_input_tokens = int(GUI_config["LLM_GPT"]["max_input_tokens"])
        gpt_models_max_input_tokens = gpt.gpt_models_max_input_tokens[gpt.gpt_parameters["model"]]
        self.LLM_SB_GPT_Max_input_tokens.setMaximum(gpt_models_max_input_tokens)

        if gpt_max_input_tokens < 1024:
            gpt_max_input_tokens = 1024
        elif gpt_max_input_tokens > gpt_models_max_input_tokens:
            gpt_max_input_tokens = gpt_models_max_input_tokens

        GUI_config["LLM_GPT"]["max_input_tokens"] = str(gpt_max_input_tokens)
        self.LLM_SB_GPT_Max_input_tokens.setValue(gpt_max_input_tokens)
        gpt.gpt_parameters["max_input_tokens"] = gpt_max_input_tokens
        ### LLM GPT max input tokens


        # LLM GPT max output tokens
        gpt_max_output_tokens = int(GUI_config["LLM_GPT"]["max_output_tokens"])
        gpt_models_max_output_tokens = gpt.gpt_models_max_output_tokens[gpt.gpt_parameters["model"]]
        self.LLM_SB_GPT_Max_output_tokens.setMaximum(gpt_models_max_output_tokens)

        if gpt_max_output_tokens < 128:
            gpt_max_output_tokens = 128
        elif gpt_max_output_tokens > gpt_models_max_output_tokens:
            gpt_max_output_tokens = gpt_models_max_output_tokens

        GUI_config["LLM_GPT"]["max_output_tokens"] = str(gpt_max_output_tokens)
        self.LLM_SB_GPT_Max_output_tokens.setValue(gpt_max_output_tokens)
        gpt.gpt_parameters["max_output_tokens"] = gpt_max_output_tokens
        ### LLM GPT max output tokens


        # LLM GPT temperature
        gpt_temperature = round(float(GUI_config["LLM_GPT"]["temperature"]), 2)

        if gpt_temperature < 0:
            gpt_temperature = 0.00
        elif gpt_temperature > 2:
            gpt_temperature = 2.00

        GUI_config["LLM_GPT"]["temperature"] = str(gpt_temperature)
        self.LLM_DSB_GPT_Temperature.setValue(gpt_temperature)
        gpt.gpt_parameters["temperature"] = gpt_temperature
        ### LLM GPT temperature


        # LLM GPT timeout
        gpt_timeout = int(GUI_config["LLM_GPT"]["timeout"])

        if gpt_timeout < 5:
            gpt_timeout = 5
        elif gpt_timeout > 60:
            gpt_timeout = 60

        GUI_config["LLM_GPT"]["timeout"] = str(gpt_timeout)
        self.LLM_SB_GPT_Timeout.setValue(gpt_timeout)
        gpt.gpt_parameters["timeout"] = gpt_timeout
        ### LLM GPT timeout


        # LLM GPT retry
        gpt_retry = int(GUI_config["LLM_GPT"]["retry"])

        if gpt_retry < 1:
            gpt_retry = 1
        elif gpt_retry > 10:
            gpt_retry = 10

        GUI_config["LLM_GPT"]["retry"] = str(gpt_retry)
        self.LLM_SB_GPT_Retry.setValue(gpt_retry)
        gpt.gpt_parameters["retry"] = gpt_retry
        ### LLM GPT retry





        # TextToSpeech using
        TextToSpeech_using = GUI_config["TextToSpeech"]["using"]
        
        if TextToSpeech_using == "EdgeTTS":
            self.TTS_RB_EdgeTTS.setChecked(True)
        elif TextToSpeech_using == "OpenAITTS":
            self.TTS_RB_OpenAITTS.setChecked(True)
        else:
            self.TTS_RB_EdgeTTS.setChecked(True)
            TextToSpeech_using = "EdgeTTS"
            GUI_config["TextToSpeech"]["using"] = TextToSpeech_using
        
        aivtui.GUI_TTS_Using = TextToSpeech_using
        ### TextToSpeech using



        # EdgeTTS voice
        edgetts.EdgeTTS_Voice_dict = edgetts.create_voices_dict("TextToSpeech/edgeTTS_speakers.txt")
        voice_list = edgetts.filter_voices_by_gender(edgetts.EdgeTTS_Voice_dict, "All")
        for name in voice_list:
            self.TTS_CB_ET_Voice.addItem(name)
        
        voice = GUI_config["EdgeTTS"]["voice"]
        if voice in voice_list:
            self.TTS_CB_ET_Voice.setCurrentText(voice)
        else:
            voice = self.TTS_CB_ET_Voice.currentText()
            GUI_config["EdgeTTS"]["voice"] = voice

        edgetts.edgetts_parameters["voice"] = voice
        ### EdgeTTS voice


        # EdgeTTS pitch
        EdgeTTS_pitch = int(GUI_config["EdgeTTS"]["pitch"])
        
        if EdgeTTS_pitch < -100:
            EdgeTTS_pitch = -100
        elif EdgeTTS_pitch > 100:
            EdgeTTS_pitch = 100

        GUI_config["EdgeTTS"]["pitch"] = str(EdgeTTS_pitch)
        self.TTS_SB_ET_Pitch.setValue(EdgeTTS_pitch)

        if EdgeTTS_pitch >= 0:
            EdgeTTS_pitch = f"+{EdgeTTS_pitch}Hz"
        else:
            EdgeTTS_pitch = f"{EdgeTTS_pitch}Hz"
        edgetts.edgetts_parameters["pitch"] = EdgeTTS_pitch
        ### EdgeTTS pitch


        # EdgeTTS rate
        EdgeTTS_rate = int(GUI_config["EdgeTTS"]["rate"])
        
        if EdgeTTS_rate < -100:
            EdgeTTS_rate = -100
        elif EdgeTTS_rate > 100:
            EdgeTTS_rate = 100

        GUI_config["EdgeTTS"]["rate"] = str(EdgeTTS_rate)
        self.TTS_SB_ET_Rate.setValue(EdgeTTS_rate)

        if EdgeTTS_rate >= 0:
            EdgeTTS_rate = f"+{EdgeTTS_rate}%"
        else:
            EdgeTTS_rate = f"{EdgeTTS_rate}%"
        edgetts.edgetts_parameters["rate"] = EdgeTTS_rate
        ### EdgeTTS rate


        # EdgeTTS volume
        EdgeTTS_volume = int(GUI_config["EdgeTTS"]["volume"])
        
        if EdgeTTS_volume < -100:
            EdgeTTS_volume = -100
        elif EdgeTTS_volume > 100:
            EdgeTTS_volume = 100

        GUI_config["EdgeTTS"]["volume"] = str(EdgeTTS_volume)
        self.TTS_SB_ET_Volume.setValue(EdgeTTS_volume)

        if EdgeTTS_volume >= 0:
            EdgeTTS_volume = f"+{EdgeTTS_volume}%"
        else:
            EdgeTTS_volume = f"{EdgeTTS_volume}%"
        edgetts.edgetts_parameters["volume"] = EdgeTTS_volume
        ### EdgeTTS volume


        # EdgeTTS timeout
        EdgeTTS_timeout = int(GUI_config["EdgeTTS"]["timeout"])
        
        if EdgeTTS_timeout < 5:
            EdgeTTS_timeout = 5
        elif EdgeTTS_timeout > 60:
            EdgeTTS_timeout = 60

        GUI_config["EdgeTTS"]["timeout"] = str(EdgeTTS_timeout)
        self.TTS_SB_ET_Timeout.setValue(EdgeTTS_timeout)
        edgetts.edgetts_parameters["timeout"] = EdgeTTS_timeout
        ### EdgeTTS timeout



        # OpenAITTS voice
        voice_list = openaitts.OpenAITTS_Voice_list
        for name in voice_list:
            self.TTS_CB_OT_Voice.addItem(name)
        
        voice = GUI_config["OpenAITTS"]["voice"]
        if voice in voice_list:
            self.TTS_CB_OT_Voice.setCurrentText(voice)
        else:
            voice = self.TTS_CB_OT_Voice.currentText()
            GUI_config["OpenAITTS"]["voice"] = voice

        openaitts.openaitts_parameters["voice"] = voice
        ### OpenAITTS voice


        # OpenAITTS model
        model_list = openaitts.OpenAITTS_Model_list
        for name in model_list:
            self.TTS_CB_OT_Model.addItem(name)
        
        model = GUI_config["OpenAITTS"]["model"]
        if model in model_list:
            self.TTS_CB_OT_Model.setCurrentText(model)
        else:
            model = self.TTS_CB_OT_Model.currentText()
            GUI_config["OpenAITTS"]["model"] = model

        openaitts.openaitts_parameters["model"] = model
        ### OpenAITTS model


        # OpenAITTS speed
        OpenAITTS_speed = round(float(GUI_config["OpenAITTS"]["speed"]), 2)

        if OpenAITTS_speed < 0.25:
            OpenAITTS_speed = 0.25
        elif OpenAITTS_speed > 4.00:
            OpenAITTS_speed = 4.00

        GUI_config["OpenAITTS"]["speed"] = str(OpenAITTS_speed)
        self.TTS_DSB_OT_Speed.setValue(OpenAITTS_speed)
        openaitts.openaitts_parameters["speed"] = OpenAITTS_speed
        ### OpenAITTS speed


        # OpenAITTS timeout
        OpenAITTS_timeout = int(GUI_config["OpenAITTS"]["timeout"])

        if OpenAITTS_timeout < 5:
            OpenAITTS_timeout = 5
        elif OpenAITTS_timeout > 60:
            OpenAITTS_timeout = 60

        GUI_config["OpenAITTS"]["timeout"] = str(OpenAITTS_timeout)
        self.TTS_SB_OT_Timeout.setValue(OpenAITTS_timeout)
        openaitts.openaitts_parameters["timeout"] = round(float(OpenAITTS_timeout), 1)
        ### OpenAITTS timeout





        # whisper inference
        aivtui.OpenAI_Whisper_Inference = str(GUI_config["Whisper"]["inference"])
        self.Wh_CB_Inference.setCurrentText(aivtui.OpenAI_Whisper_Inference)
        # whisper inference


        # whisper model name list
        Available_model_names_list = whisper.get_available_model_names_list()
        for name in Available_model_names_list:
            self.Wh_CB_Whisper_model_name.addItem(name)

        gui_selected_model = str(GUI_config["Whisper"]["model_name"])
        if gui_selected_model in Available_model_names_list:
            self.Wh_CB_Whisper_model_name.setCurrentText(gui_selected_model)
        else:
            gui_selected_model = self.Wh_CB_Whisper_model_name.currentText()
            GUI_config["Whisper"]["model_name"] = gui_selected_model

        whisper.whisper_status["gui_selected_model"] = gui_selected_model
        ### whisper model name list


        # whisper language
        language_names = [name for name in whisper.Whisper_LANGUAGES.keys()]
        for name in language_names:
            self.Wh_CB_Language.addItem(name)

        whisper_lang = str(GUI_config["Whisper"]["language"])
        if whisper_lang in language_names:
            self.Wh_CB_Language.setCurrentText(whisper_lang)
        else:
            whisper_lang = self.Wh_CB_Language.currentText()
            GUI_config["Whisper"]["language"] = whisper_lang

        whisper.whisper_parameters["user_mic_language"] = whisper_lang
        whisper_api.whisper_parameters["user_mic_language"] = whisper_lang
        ### whisper language


        # whisper max tokens
        tokens = int(GUI_config["Whisper"]["max_tokens"])
        
        if tokens < 0:
            tokens = 0
        elif tokens > 9999:
            tokens = 9999

        GUI_config["Whisper"]["max_tokens"] = str(tokens)
        self.Wh_SB_Max_tokens.setValue(tokens)
        whisper.whisper_parameters["max_tokens"] = tokens
        ### whisper max tokens


        # whisper temperature
        whisper_temp = float(GUI_config["Whisper"]["temperature"])
        
        if whisper_temp < 0:
            whisper_temp = 0.0
        elif whisper_temp > 1:
            whisper_temp = 1.0

        GUI_config["Whisper"]["temperature"] = str(whisper_temp)
        self.Wh_DSB_Temperature.setValue(whisper_temp)
        whisper.whisper_parameters["temperature"] = whisper_temp
        whisper_api.whisper_parameters["temperature"] = whisper_temp
        ### whisper temperature


        # whisper timeout
        whisper_timeout = int(GUI_config["Whisper"]["timeout"])
        
        if whisper_timeout < 5:
            whisper_timeout = 5
        elif whisper_timeout > 60:
            whisper_timeout = 60

        GUI_config["Whisper"]["timeout"] = str(whisper_timeout)
        self.Wh_SB_Timeout.setValue(whisper_timeout)
        whisper.whisper_parameters["timeout"] = whisper_timeout
        whisper_api.whisper_parameters["timeout"] = whisper_timeout
        ### whisper timeout


        # whisper prompt
        whisper_prompt = str(GUI_config["Whisper"]["prompt"])
        self.Wh_TE_Prompt.setPlainText(whisper_prompt)
        whisper.whisper_parameters["prompt"] = whisper_prompt
        whisper_api.whisper_parameters["prompt"] = whisper_prompt
        ### whisper prompt





        # OBS Subtitles formatter
        subtitles_formatter = GUI_config["OBS_Subtitles"]["subtitles_formatter"] == "True"
        obsws.OBS_subtitles_parameters["subtitles_formatter"] = subtitles_formatter
        self.OBS_cB_Subtitles_formatter.setChecked(subtitles_formatter)
        ### OBS Subtitles formatter


        # OBS Subtitles formatter version
        sub_ver_list = obsws.OBS_subtitles_formatter_versions
        for name in sub_ver_list:
            self.OBS_CB_Subtitles_formatter_version.addItem(name)

        sub_ver = str(GUI_config["OBS_Subtitles"]["subtitles_formatter_version"])
        if sub_ver in sub_ver_list:
            self.OBS_CB_Subtitles_formatter_version.setCurrentText(sub_ver)
        else:
            sub_ver = self.OBS_CB_Subtitles_formatter_version.currentText()
            GUI_config["OBS_Subtitles"]["subtitles_formatter_version"] = sub_ver

        obsws.OBS_subtitles_parameters["subtitles_formatter_version"] = sub_ver
        ### OBS Subtitles formatter version



        # OBS Chat now sub
        show_sub = GUI_config["OBS_Chat_now_sub"]["show"] == "True"
        obsws.OBS_chat_now_sub_parameters["show"] = show_sub
        self.OBS_cB_Chat_now.setChecked(show_sub)
        ### OBS Chat now sub


        # OBS Chat now sub clear
        clear_sub = GUI_config["OBS_Chat_now_sub"]["clear"] == "True"
        obsws.OBS_chat_now_sub_parameters["clear"] = clear_sub
        self.OBS_cB_cn_Clear.setChecked(clear_sub)
        ### OBS Chat now sub clear


        # OBS Chat now sub name
        sub_name = GUI_config["OBS_Chat_now_sub"]["sub_name"].strip()
        obsws.OBS_chat_now_sub_parameters["sub_name"] = sub_name
        self.OBS_LE_cn_Sub_name.setText(sub_name)
        GUI_config["OBS_Chat_now_sub"]["sub_name"] = sub_name
        ### OBS Chat now sub name


        # OBS Chat now sub time
        sub_time = round(float(GUI_config["OBS_Chat_now_sub"]["sub_time"]), 1)

        if sub_time < 0:
            sub_time = 0.0
        elif sub_time > 60:
            sub_time = 60.0

        GUI_config["OBS_Chat_now_sub"]["sub_time"] = str(sub_time)
        self.OBS_DSB_cn_Sub_time.setValue(sub_time)
        obsws.OBS_chat_now_sub_parameters["sub_time"] = sub_time
        ### OBS Chat now sub time


        # OBS Chat now sub max length
        sub_max_length = int(GUI_config["OBS_Chat_now_sub"]["sub_max_length"])

        if sub_max_length < 1:
            sub_max_length = 1
        elif sub_max_length > 999:
            sub_max_length = 999

        GUI_config["OBS_Chat_now_sub"]["sub_max_length"] = str(sub_max_length)
        self.OBS_SB_cn_Max_length.setValue(sub_max_length)
        obsws.OBS_chat_now_sub_parameters["sub_max_length"] = sub_max_length
        ### OBS Chat now sub max length


        # OBS Chat now sub english char length
        en_char_len = round(float(GUI_config["OBS_Chat_now_sub"]["sub_english_char_length"]), 2)

        if en_char_len < 0.01:
            en_char_len = 0.01
        elif en_char_len > 1.00:
            en_char_len = 1.00

        GUI_config["OBS_Chat_now_sub"]["sub_english_char_length"] = str(en_char_len)
        self.OBS_DSB_cn_English_char_length.setValue(en_char_len)
        obsws.OBS_chat_now_sub_parameters["sub_english_char_length"] = en_char_len
        ### OBS Chat now sub english char length
        

        # OBS Chat now sub base line count
        sub_blc = int(GUI_config["OBS_Chat_now_sub"]["sub_base_line_count"])

        if sub_blc < 1:
            sub_blc = 1
        elif sub_blc > 999:
            sub_blc = 999

        GUI_config["OBS_Chat_now_sub"]["sub_base_line_count"] = str(sub_blc)
        self.OBS_SB_cn_Base_line_count.setValue(sub_blc)
        obsws.OBS_chat_now_sub_parameters["sub_base_line_count"] = sub_blc
        ### OBS Chat now sub base line count


        # OBS Chat now sub end delay
        sub_end_delay = round(float(GUI_config["OBS_Chat_now_sub"]["sub_end_delay"]), 1)

        if sub_end_delay < 0:
            sub_end_delay = 0.0
        elif sub_end_delay > 60:
            sub_end_delay = 60.0

        GUI_config["OBS_Chat_now_sub"]["sub_end_delay"] = str(sub_end_delay)
        self.OBS_DSB_cn_End_delay.setValue(sub_end_delay)
        obsws.OBS_chat_now_sub_parameters["sub_end_delay"] = sub_end_delay
        ### OBS Chat now sub end delay


        # OBS Chat now show sub filter names
        filter_names = [name for name in GUI_config["OBS_Chat_now_sub"]["show_sub_filter_names"].split('/') if name.strip() != '']
        obsws.OBS_chat_now_sub_parameters["show_sub_filter_names"] = filter_names
        text = GUI_config["OBS_Chat_now_sub"]["show_sub_filter_names"].strip()
        self.OBS_TE_cn_Show_sub_filter_names.setPlainText(text)
        GUI_config["OBS_Chat_now_sub"]["show_sub_filter_names"] = text
        ### OBS Chat now show sub filter names


        # OBS Chat now show sub filter delay
        filter_delay = round(float(GUI_config["OBS_Chat_now_sub"]["show_sub_filter_start_delay"]), 2)

        if filter_delay < 0:
            filter_delay = 0.0
        elif filter_delay > 60:
            filter_delay = 60.0

        GUI_config["OBS_Chat_now_sub"]["show_sub_filter_start_delay"] = str(filter_delay)
        self.OBS_DSB_cn_Show_sub_filter_names_Delay.setValue(filter_delay)
        obsws.OBS_chat_now_sub_parameters["show_sub_filter_start_delay"] = filter_delay
        ### OBS Chat now show sub filter delay


        # OBS Chat now hide sub filter names
        filter_names = [name for name in GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_names"].split('/') if name.strip() != '']
        obsws.OBS_chat_now_sub_parameters["hide_sub_filter_names"] = filter_names
        text = GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_names"].strip()
        self.OBS_TE_cn_Hide_sub_filter_names.setPlainText(text)
        GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_names"] = text
        ### OBS Chat now hide sub filter names


        # OBS Chat now hide sub filter delay
        filter_delay = round(float(GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_start_delay"]), 2)

        if filter_delay < 0:
            filter_delay = 0.0
        elif filter_delay > 60:
            filter_delay = 60.0

        GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_start_delay"] = str(filter_delay)
        self.OBS_DSB_cn_Hide_sub_filter_names_Delay.setValue(filter_delay)
        obsws.OBS_chat_now_sub_parameters["hide_sub_filter_start_delay"] = filter_delay
        ### OBS Chat now hide sub filter delay



        # OBS AI ans sub
        show_sub = GUI_config["OBS_AI_ans_sub"]["show"] == "True"
        obsws.OBS_ai_ans_sub_parameters["show"] = show_sub
        self.OBS_cB_AI_ans.setChecked(show_sub)
        ### OBS AI ans sub


        # OBS AI ans sub clear
        clear_sub = GUI_config["OBS_AI_ans_sub"]["clear"] == "True"
        obsws.OBS_ai_ans_sub_parameters["clear"] = clear_sub
        self.OBS_cB_aa_Clear.setChecked(clear_sub)
        ### OBS AI ans sub clear


        # OBS AI ans sub name
        sub_name = GUI_config["OBS_AI_ans_sub"]["sub_name"].strip()
        obsws.OBS_ai_ans_sub_parameters["sub_name"] = sub_name
        self.OBS_LE_aa_Sub_name.setText(sub_name)
        GUI_config["OBS_AI_ans_sub"]["sub_name"] = sub_name
        ### OBS AI ans sub name


        # OBS AI ans sub remove original text wrap
        remove_original_text_wrap = GUI_config["OBS_AI_ans_sub"]["remove_original_text_wrap"] == "True"
        obsws.OBS_ai_ans_sub_parameters["remove_original_text_wrap"] = remove_original_text_wrap
        self.OBS_cB_aa_Remove_original_text_wrap.setChecked(remove_original_text_wrap)
        ### OBS AI ans sub remove original text wrap


        # OBS AI ans sub max length
        sub_max_length = int(GUI_config["OBS_AI_ans_sub"]["sub_max_length"])

        if sub_max_length < 1:
            sub_max_length = 1
        elif sub_max_length > 999:
            sub_max_length = 999

        GUI_config["OBS_AI_ans_sub"]["sub_max_length"] = str(sub_max_length)
        self.OBS_SB_aa_Max_length.setValue(sub_max_length)
        obsws.OBS_ai_ans_sub_parameters["sub_max_length"] = sub_max_length
        ### OBS AI ans sub max length


        # OBS AI ans sub english char length
        en_char_len = round(float(GUI_config["OBS_AI_ans_sub"]["sub_english_char_length"]), 2)

        if en_char_len < 0.01:
            en_char_len = 0.01
        elif en_char_len > 1.00:
            en_char_len = 1.00

        GUI_config["OBS_AI_ans_sub"]["sub_english_char_length"] = str(en_char_len)
        self.OBS_DSB_aa_English_char_length.setValue(en_char_len)
        obsws.OBS_ai_ans_sub_parameters["sub_english_char_length"] = en_char_len
        ### OBS AI ans sub english char length
        

        # OBS AI ans sub base line count
        sub_blc = int(GUI_config["OBS_AI_ans_sub"]["sub_base_line_count"])

        if sub_blc < 1:
            sub_blc = 1
        elif sub_blc > 999:
            sub_blc = 999

        GUI_config["OBS_AI_ans_sub"]["sub_base_line_count"] = str(sub_blc)
        self.OBS_SB_aa_Base_line_count.setValue(sub_blc)
        obsws.OBS_ai_ans_sub_parameters["sub_base_line_count"] = sub_blc
        ### OBS AI ans sub base line count


        # OBS AI ans sub end delay
        sub_end_delay = round(float(GUI_config["OBS_AI_ans_sub"]["sub_end_delay"]), 1)

        if sub_end_delay < 0:
            sub_end_delay = 0.0
        elif sub_end_delay > 60:
            sub_end_delay = 60.0

        GUI_config["OBS_AI_ans_sub"]["sub_end_delay"] = str(sub_end_delay)
        self.OBS_DSB_aa_End_delay.setValue(sub_end_delay)
        obsws.OBS_ai_ans_sub_parameters["sub_end_delay"] = sub_end_delay
        ### OBS AI ans sub end delay


        # OBS AI ans show sub filter names
        filter_names = [name for name in GUI_config["OBS_AI_ans_sub"]["show_sub_filter_names"].split('/') if name.strip() != '']
        obsws.OBS_ai_ans_sub_parameters["show_sub_filter_names"] = filter_names
        text = GUI_config["OBS_AI_ans_sub"]["show_sub_filter_names"].strip()
        self.OBS_TE_aa_Show_sub_filter_names.setPlainText(text)
        GUI_config["OBS_AI_ans_sub"]["show_sub_filter_names"] = text
        ### OBS AI ans show sub filter names


        # OBS AI ans show sub filter delay
        filter_delay = round(float(GUI_config["OBS_AI_ans_sub"]["show_sub_filter_start_delay"]), 2)

        if filter_delay < 0:
            filter_delay = 0.0
        elif filter_delay > 60:
            filter_delay = 60.0

        GUI_config["OBS_AI_ans_sub"]["show_sub_filter_start_delay"] = str(filter_delay)
        self.OBS_DSB_aa_Show_sub_filter_names_Delay.setValue(filter_delay)
        obsws.OBS_ai_ans_sub_parameters["show_sub_filter_start_delay"] = filter_delay
        ### OBS AI ans show sub filter delay


        # OBS AI ans hide sub filter names
        filter_names = [name for name in GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_names"].split('/') if name.strip() != '']
        obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_names"] = filter_names
        text = GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_names"].strip()
        self.OBS_TE_aa_Hide_sub_filter_names.setPlainText(text)
        GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_names"] = text
        ### OBS AI ans hide sub filter names


        # OBS AI ans hide sub filter delay
        filter_delay = round(float(GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_start_delay"]), 2)

        if filter_delay < 0:
            filter_delay = 0.0
        elif filter_delay > 60:
            filter_delay = 60.0

        GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_start_delay"] = str(filter_delay)
        self.OBS_DSB_aa_Hide_sub_filter_names_Delay.setValue(filter_delay)
        obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_start_delay"] = filter_delay
        ### OBS AI ans hide sub filter delay





        # VTSP trigger first
        enble = GUI_config["VTube_Studio_Plug"]["trigger_first"] == "True"
        self.VTSP_cB_Trigger_first.setChecked(enble)
        vtsp.AIVT_hotkeys_parameters["trigger_first"] = enble
        ### VTSP trigger first


        # VTSP wait until hotkeys complete
        enble = GUI_config["VTube_Studio_Plug"]["wait_until_hotkeys_complete"] == "True"
        self.VTSP_cB_Wait_until_hotkeys_complete.setChecked(enble)
        aivtui.GUI_VTSP_wait_until_hotkeys_complete = enble
        ### VTSP wait until hotkeys complete


        # VTSP sentiment analysis
        enble = GUI_config["VTube_Studio_Plug"]["sentiment_analysis"] == "True"
        
        self.VTSP_cB_Sentiment_analysis.setChecked(enble)
        vtsp.AIVT_hotkeys_parameters["sentiment_analysis"] = enble

        name_list = sa_nlp.model_names_list

        for name in name_list:
            self.VTSP_CB_Sentiment_analysis.addItem(name)

        model_name = str(GUI_config["VTube_Studio_Plug"]["sentiment_analysis_modle"])
        if model_name in name_list:
            self.VTSP_CB_Sentiment_analysis.setCurrentText(model_name)
        else:
            model_name = self.VTSP_CB_Sentiment_analysis.currentText()
            GUI_config["VTube_Studio_Plug"]["sentiment_analysis_modle"] = model_name

        vtsp.AIVT_hotkeys_parameters["sentiment_analysis_model"] = model_name
        ### VTSP sentiment analysis


        # VTSP idle animation
        text = str(GUI_config["VTube_Studio_Plug"]["idle_ani"])
        self.VTSP_TE_Idle_ani.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters["idle_ani"] = text
        # VTSP idle animation


        # VTSP normal
        emo = "normal"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Normal.setChecked(enble)
        self.VTSP_TE_Normal.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP normal


        # VTSP happy
        emo = "happy"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Happy.setChecked(enble)
        self.VTSP_TE_Happy.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP happy


        # VTSP shy
        emo = "shy"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Shy.setChecked(enble)
        self.VTSP_TE_Shy.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP shy


        # VTSP proud
        emo = "proud"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Proud.setChecked(enble)
        self.VTSP_TE_Proud.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP proud


        # VTSP shock
        emo = "shock"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Shock.setChecked(enble)
        self.VTSP_TE_Shock.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP shock


        # VTSP sad
        emo = "sad"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Sad.setChecked(enble)
        self.VTSP_TE_Sad.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP sad


        # VTSP angry
        emo = "angry"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Angry.setChecked(enble)
        self.VTSP_TE_Angry.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP angry


        # VTSP embarrass
        emo = "embarrass"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Embarrass.setChecked(enble)
        self.VTSP_TE_Embarrass.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP embarrass


        # VTSP afraid
        emo = "afraid"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Afraid.setChecked(enble)
        self.VTSP_TE_Afraid.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP afraid


        # VTSP confuse
        emo = "confuse"
        enble = str(GUI_config["VTube_Studio_Plug"][emo]) == "True"
        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        text = str(GUI_config["VTube_Studio_Plug"][f"{emo}_kn"])

        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

        self.VTSP_cB_Confuse.setChecked(enble)
        self.VTSP_TE_Confuse.setPlainText(text)
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        # VTSP confuse










        # Initialize AIVT System

        aivtui.Initialize_conversation(aivtui.AIVT_Using_character)
        # Conversation History appender
        GUI_cha = GUI_Conversation_History_appender(self)
        GUI_cha.signal_Conversation_History_append.connect(self.Conversation_History_append)
        GUI_cha.start()
        
        print("\n----------\n")










        # Connected functions

        self.mOBSws.changed.connect(self.mOBSWS)
        self.mLC_YouTube.changed.connect(self.menuLC_YouTube)
        self.mLC_Twitch.changed.connect(self.menuLC_Twitch)
        self.mVTSP_Hotkeys.changed.connect(self.menuVTSP_Hotkeys)



        self.CH_cB_Show_chat_role.clicked.connect(self.Conversation_History_Show_chat_role)
        self.CH_Bt_Reset.clicked.connect(self.UserChat_Rest)

        self.UC_CB_Role_select.currentTextChanged.connect(self.UserChat_Role_select)
        self.UC_Bt_Mic.clicked.connect(self.UserChat_Mic)
        self.UC_Bt_Clear.clicked.connect(self.UserChat_Clear)
        self.UC_Bt_Enter.clicked.connect(self.UserChat_Enter)



        self.St_LE_User_Name.textChanged.connect(self.Setting_User_Name)
        self.St_CB_Character_select.currentTextChanged.connect(self.Setting_Character_select)
        self.St_Bt_Refresh_available_character.clicked.connect(self.Setting_Refresh_available_character)

        self.St_CB_Tab_position.currentTextChanged.connect(self.Setting_Tab_Position)
        self.St_HS_Window_opacity.valueChanged.connect(self.Setting_Window_opacity)

        self.St_CB_AI_Voice_output_devices.currentTextChanged.connect(self.Setting_Select_AI_Voice_output_devices)
        self.St_CB_User_Mic_iutput_devices.currentTextChanged.connect(self.Setting_Select_User_Mic_input_devices)
        self.St_Bt_Refresh_available_Input_output_devices.clicked.connect(self.Setting_Refresh_available_input_output_devices)
        self.St_cB_Read_user_chat.clicked.connect(self.Setting_Read_user_chat)

        self.St_Bt_User_mic_hotkey1.clicked.connect(self.Setting_User_mic_hotkey1)
        self.St_cB_User_mic_hotkey1.clicked.connect(self.Setting_User_mic_hotkey_using)
        self.St_Bt_User_mic_hotkey2.clicked.connect(self.Setting_User_mic_hotkey2)
        self.St_cB_User_mic_hotkey2.clicked.connect(self.Setting_User_mic_hotkey_using)

        self.St_TE_Doing_now.textChanged.connect(self.Setting_Doing_now)


        self.LC_LE_yt_channel_name.textChanged.connect(self.YouTube_channel_name)
        self.LC_LE_yt_live_id.textChanged.connect(self.YouTube_live_id)
        self.LC_cB_yt_chatroom.clicked.connect(self.YouTube_chatroom)
        self.LC_cB_yt_read_chat_now.clicked.connect(self.YouTube_live_chat_read_chat_now)
        self.LC_cB_yt_owner.clicked.connect(self.YouTube_response_owner)
        self.LC_cB_yt_vip.clicked.connect(self.YouTube_response_vip)
        self.LC_cB_yt_response_individual.clicked.connect(self.YouTube_response_individual)
        self.LC_SB_yt_chat_max_wait_list.valueChanged.connect(self.YouTube_wait_list_max)
        self.LC_SB_yt_chat_max_tokens.valueChanged.connect(self.YouTube_chat_max_tokens)
        self.LC_SB_yt_chat_max_response.valueChanged.connect(self.YouTube_chat_max_response)
        self.LC_TE_yt_vip_names.textChanged.connect(self.YouTube_live_chat_vip_names)
        self.LC_TE_yt_ban_names.textChanged.connect(self.YouTube_live_chat_ban_names)

        self.LC_LE_tw_channel_name.textChanged.connect(self.Twitch_channel_name)
        self.LC_cB_tw_chatroom.clicked.connect(self.Twitch_chatroom)
        self.LC_cB_tw_read_chat_now.clicked.connect(self.Twitch_live_chat_read_chat_now)
        self.LC_cB_tw_owner.clicked.connect(self.Twitch_response_owner)
        self.LC_cB_tw_vip.clicked.connect(self.Twitch_response_vip)
        self.LC_cB_tw_response_individual.clicked.connect(self.Twitch_response_individual)
        self.LC_SB_tw_chat_max_wait_list.valueChanged.connect(self.Twitch_wait_list_max)
        self.LC_SB_tw_chat_max_tokens.valueChanged.connect(self.Twitch_chat_max_tokens)
        self.LC_SB_tw_chat_max_response.valueChanged.connect(self.Twitch_chat_max_response)
        self.LC_TE_tw_vip_names.textChanged.connect(self.Twitch_live_chat_vip_names)
        self.LC_TE_tw_ban_names.textChanged.connect(self.Twitch_live_chat_ban_names)



        self.Wh_CB_Inference.currentTextChanged.connect(self.Whisper_Select_Inference)

        self.Wh_CB_Whisper_model_name.currentTextChanged.connect(self.Whisper_Select_Whisper_model_name)
        self.Wh_Bt_Whisper_model_load.clicked.connect(self.Whisper_model_load)
        self.Wh_Bt_Whisper_model_unload.clicked.connect(self.Whisper_model_unload)
        self.Wh_Bt_Refresh_available_whisper_model.clicked.connect(self.Whisper_Refresh_available_whisper_model)

        self.Wh_CB_Language.currentTextChanged.connect(self.Whisper_Select_Language)
        self.Wh_SB_Max_tokens.valueChanged.connect(self.Whisper_max_tokens)
        self.Wh_DSB_Temperature.valueChanged.connect(self.Whisper_temperature)
        self.Wh_SB_Timeout.valueChanged.connect(self.Whisper_timeout)
        self.Wh_TE_Prompt.textChanged.connect(self.Whisper_prompt)



        self.TTS_RB_EdgeTTS.clicked.connect(self.TTS_EdgeTTS)
        self.TTS_RB_OpenAITTS.clicked.connect(self.TTS_OpenAITTS)

        self.TTS_CB_ET_Voice.currentTextChanged.connect(self.EdgeTTS_Select_voice)
        self.TTS_CB_ET_Gender.currentTextChanged.connect(self.EdgeTTS_Select_gender)
        self.TTS_SB_ET_Pitch.valueChanged.connect(self.EdgeTTS_pitch)
        self.TTS_SB_ET_Rate.valueChanged.connect(self.EdgeTTS_rate)
        self.TTS_SB_ET_Volume.valueChanged.connect(self.EdgeTTS_volume)
        self.TTS_SB_ET_Timeout.valueChanged.connect(self.EdgeTTS_timeout)

        self.TTS_CB_OT_Voice.currentTextChanged.connect(self.OpenAITTS_Select_voice)
        self.TTS_CB_OT_Model.currentTextChanged.connect(self.OpenAITTS_Select_model)
        self.TTS_DSB_OT_Speed.valueChanged.connect(self.OpenAITTS_speed)
        self.TTS_SB_OT_Timeout.valueChanged.connect(self.OpenAITTS_timeout)



        self.LLM_RB_Gemini.clicked.connect(self.LLM_Gemini)
        self.LLM_RB_GPT.clicked.connect(self.LLM_GPT)

        self.LLM_cB_Instruction_enhance.clicked.connect(self.LLM_instruction_enhance)
        self.LLM_SB_Instruction_enhance.valueChanged.connect(self.LLM_instruction_enhance_i)
        self.LLM_TE_Instruction_enhance.textChanged.connect(self.LLM_instruction_enhance_prompt_change)

        self.LLM_CB_Ge_Model.currentTextChanged.connect(self.Gemini_Select_model)
        self.LLM_SB_Ge_Max_input_tokens.valueChanged.connect(self.Gemini_max_input_tokens)
        self.LLM_SB_Ge_Max_output_tokens.valueChanged.connect(self.Gemini_max_output_tokens)
        self.LLM_DSB_Ge_Temperature.valueChanged.connect(self.Gemini_temperature)
        self.LLM_SB_Ge_Timeout.valueChanged.connect(self.Gemini_timeout)
        self.LLM_SB_Ge_Retry.valueChanged.connect(self.Gemini_retry)

        self.LLM_CB_GPT_Model.currentTextChanged.connect(self.GPT_Select_model)
        self.LLM_SB_GPT_Max_input_tokens.valueChanged.connect(self.GPT_max_input_tokens)
        self.LLM_SB_GPT_Max_output_tokens.valueChanged.connect(self.GPT_max_output_tokens)
        self.LLM_DSB_GPT_Temperature.valueChanged.connect(self.GPT_temperature)
        self.LLM_SB_GPT_Timeout.valueChanged.connect(self.GPT_timeout)
        self.LLM_SB_GPT_Retry.valueChanged.connect(self.GPT_retry)



        self.OBS_cB_Subtitles_formatter.clicked.connect(self.OBS_subtitles_formatter)
        self.OBS_CB_Subtitles_formatter_version.currentTextChanged.connect(self.OBS_Select_subtitles_formatter_version)

        self.OBS_cB_Chat_now.clicked.connect(self.OBS_chat_now_subtitles)
        self.OBS_cB_cn_Clear.clicked.connect(self.OBS_cn_clear)
        self.OBS_LE_cn_Sub_name.textChanged.connect(self.OBS_cn_sub_name)
        self.OBS_DSB_cn_Sub_time.valueChanged.connect(self.OBS_cn_sub_time)
        self.OBS_SB_cn_Max_length.valueChanged.connect(self.OBS_cn_sub_max_length)
        self.OBS_DSB_cn_English_char_length.valueChanged.connect(self.OBS_cn_sub_english_char_length)
        self.OBS_SB_cn_Base_line_count.valueChanged.connect(self.OBS_cn_sub_base_line_count)
        self.OBS_DSB_cn_End_delay.valueChanged.connect(self.OBS_cn_sub_end_delay)
        self.OBS_TE_cn_Show_sub_filter_names.textChanged.connect(self.OBS_cn_show_sub_filter_names)
        self.OBS_DSB_cn_Show_sub_filter_names_Delay.valueChanged.connect(self.OBS_cn_show_sub_filter_names_delay)
        self.OBS_TE_cn_Hide_sub_filter_names.textChanged.connect(self.OBS_cn_hide_sub_filter_names)
        self.OBS_DSB_cn_Hide_sub_filter_names_Delay.valueChanged.connect(self.OBS_cn_hide_sub_filter_names_delay)

        self.OBS_cB_AI_ans.clicked.connect(self.OBS_ai_ans_subtitles)
        self.OBS_cB_aa_Clear.clicked.connect(self.OBS_aa_clear)
        self.OBS_LE_aa_Sub_name.textChanged.connect(self.OBS_aa_sub_name)
        self.OBS_cB_aa_Remove_original_text_wrap.clicked.connect(self.OBS_aa_remove_original_text_wrap)
        self.OBS_SB_aa_Max_length.valueChanged.connect(self.OBS_aa_sub_max_length)
        self.OBS_DSB_aa_English_char_length.valueChanged.connect(self.OBS_aa_sub_english_char_length)
        self.OBS_SB_aa_Base_line_count.valueChanged.connect(self.OBS_aa_sub_base_line_count)
        self.OBS_DSB_aa_End_delay.valueChanged.connect(self.OBS_aa_sub_end_delay)
        self.OBS_TE_aa_Show_sub_filter_names.textChanged.connect(self.OBS_aa_show_sub_filter_names)
        self.OBS_DSB_aa_Show_sub_filter_names_Delay.valueChanged.connect(self.OBS_aa_show_sub_filter_names_delay)
        self.OBS_TE_aa_Hide_sub_filter_names.textChanged.connect(self.OBS_aa_hide_sub_filter_names)
        self.OBS_DSB_aa_Hide_sub_filter_names_Delay.valueChanged.connect(self.OBS_aa_hide_sub_filter_names_delay)



        self.VTSP_cB_Trigger_first.clicked.connect(self.VTSP_Trigger_first)
        self.VTSP_cB_Wait_until_hotkeys_complete.clicked.connect(self.VTSP_Wait_until_hotkeys_complete)
        self.VTSP_cB_Sentiment_analysis.clicked.connect(self.VTSP_Sentiment_analysis)
        self.VTSP_CB_Sentiment_analysis.currentIndexChanged.connect(self.VTSP_Select_Sentiment_analysis)

        self.VTSP_TE_Idle_ani.textChanged.connect(self.VTSP_Idle_animation)
        self.VTSP_cB_Normal.clicked.connect(self.VTSP_Normal)
        self.VTSP_TE_Normal.textChanged.connect(self.VTSP_Normal_kn)
        self.VTSP_cB_Happy.clicked.connect(self.VTSP_Happy)
        self.VTSP_TE_Happy.textChanged.connect(self.VTSP_Happy_kn)
        self.VTSP_cB_Shy.clicked.connect(self.VTSP_Shy)
        self.VTSP_TE_Shy.textChanged.connect(self.VTSP_Shy_kn)
        self.VTSP_cB_Proud.clicked.connect(self.VTSP_Proud)
        self.VTSP_TE_Proud.textChanged.connect(self.VTSP_Proud_kn)
        self.VTSP_cB_Shock.clicked.connect(self.VTSP_Shock)
        self.VTSP_TE_Shock.textChanged.connect(self.VTSP_Shock_kn)
        self.VTSP_cB_Sad.clicked.connect(self.VTSP_Sad)
        self.VTSP_TE_Sad.textChanged.connect(self.VTSP_Sad_kn)
        self.VTSP_cB_Angry.clicked.connect(self.VTSP_Angry)
        self.VTSP_TE_Angry.textChanged.connect(self.VTSP_Angry_kn)
        self.VTSP_cB_Embarrass.clicked.connect(self.VTSP_Embarrass)
        self.VTSP_TE_Embarrass.textChanged.connect(self.VTSP_Embarrass_kn)
        self.VTSP_cB_Afraid.clicked.connect(self.VTSP_Afraid)
        self.VTSP_TE_Afraid.textChanged.connect(self.VTSP_Afraid_kn)
        self.VTSP_cB_Confuse.clicked.connect(self.VTSP_Confuse)
        self.VTSP_TE_Confuse.textChanged.connect(self.VTSP_Confuse_kn)










        #aprint("GUI initialize success")










    # GUI Functions

    def menuLC_YouTube(self):
        if self.mLC_YouTube.isChecked():
            live_chat.Live_Chat_Status["YouTube_live_chat_connect_fail_count"] = 50
            self.YouTube_live_chat_connect()

            if live_chat.Live_Chat_Status["YouTube_live_chat"]:
                YT_lc = GUI_YT_LiveChat(self)
                YT_lc.signal_YouTube_live_chat_connect.connect(self.YouTube_live_chat_connect)
                YT_lc.signal_YouTube_live_chat_disconnect.connect(self.YouTube_live_chat_disconnect)
                YT_lc.start()

            else:
                self.mLC_YouTube.setChecked(False)

        else:
            print("!!! YouTube Live Chat Disconnect !!!\n")
            live_chat.Live_Chat_Status["YouTube_live_chat"] = False
            if not live_chat.Live_Chat_Status["Twitch_live_chat"]:
                live_chat.Live_Chat_Status["llm_request_checker"] = False

    def YouTube_live_chat_connect(self):
        live_chat.YouTube_live_chat_connect()
        live_chat.Live_Chat_Status["YouTube_live_chat_retry"] = False

    def YouTube_live_chat_disconnect(self):
        self.mLC_YouTube.setChecked(False)
        live_chat.Live_Chat_Status["YouTube_live_chat"] = False
        if not live_chat.Live_Chat_Status["Twitch_live_chat"]:
            live_chat.Live_Chat_Status["llm_request_checker"] = False


    def menuLC_Twitch(self):
        if self.mLC_Twitch.isChecked():
            TW_lc = GUI_TW_LiveChat(self)
            TW_lc.signal_Twitch_live_chat_disconnect.connect(self.Twitch_live_chat_disconnect)
            TW_lc.start()
            
        else:
            print("!!! Twitch Live Chat Disconnect !!!\n")
            live_chat.Live_Chat_Status["Twitch_live_chat"] = False
            live_chat.live_chat_status['Twitch_live_chat'] = False
            if not live_chat.Live_Chat_Status["YouTube_live_chat"]:
                live_chat.Live_Chat_Status["llm_request_checker"] = False

    def Twitch_live_chat_disconnect(self):
        self.mLC_Twitch.setChecked(False)
        live_chat.Live_Chat_Status["Twitch_live_chat"] = False
        live_chat.live_chat_status['Twitch_live_chat'] = False
        if not live_chat.Live_Chat_Status["YouTube_live_chat"]:
            live_chat.Live_Chat_Status["llm_request_checker"] = False



    def mOBSWS(self):
        if self.mOBSws.isChecked() and not obsws.OBS_Connected:
            oc = GUI_OBSWS_connect(self)
            oc.signal_OBSWS_connect_fail.connect(self.mOBSWS_unChecked)
            oc.start()
        
        elif not self.mOBSws.isChecked() and obsws.OBS_Connected:
            od = GUI_OBSWS_disconnect(self)
            od.start()

    def mOBSWS_unChecked(self, signal_bool):
        if not signal_bool:
            self.mOBSws.setChecked(False)



    def menuVTSP_Hotkeys(self):
        if self.mVTSP_Hotkeys.isChecked():
            vtsp_a = GUI_AIVT_VTSP_authenticated(self)
            vtsp_a.signal_vtsp_authenticated_fail.connect(self.menuVTSP_Hotkeys_unChecked)
            vtsp_a.start()
        else:
            print("!!! VTSP API Disconnect !!!")
            vtsp.AIVT_VTSP_Status["authenticated"] = False

    def menuVTSP_Hotkeys_unChecked(self):
        self.mVTSP_Hotkeys.setChecked(False)





    def Conversation_History_append(self, chat_role, chat_now, ai_name, ai_ans):
        try:
            name, text = chat_now.split(" : ", 1)
            text = text.split("*", 2)[-1]
            if self.CH_cB_Show_chat_role.isChecked():
                chat_now = f"{name} ({chat_role}) :\n{text}"

            else:
                chat_now = f"{name} :\n{text}"

        except:
            chat_now = chat_now

        if chat_role == "assistant":
            self.CH_TE_Conversation_history.append(f"{ai_name} :\n{ai_ans}\n\n----------\n")

        else:
            self.CH_TE_Conversation_history.append(f"{chat_now}\n\n{ai_name} :\n{ai_ans}\n\n----------\n")

    def Conversation_History_Show_chat_role(self):
        global GUI_config
        GUI_config["Main"]["show_chat_role"] = str(self.CH_cB_Show_chat_role.isChecked())



    def UserChat_Rest(self):
        aivtui.conversation = aivtui.conversation[:len(aivtui.AIVT_Character_prompt_filenames)+1]
        aprint("!!! Conversation Initialized !!!")


    def UserChat_Role_select(self):
        aprint(f"User chat role selected: {self.UC_CB_Role_select.currentText()}")


    def UserChat_Mic(self):
        mcrc.user_mic_status["mic_on"] = not mcrc.user_mic_status["mic_on"]
        if mcrc.user_mic_status["mic_on"]:
            aprint("User Mic ON")
            palette = self.UC_Bt_Mic.palette()
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 124, 67)) #orange
            self.UC_Bt_Mic.setPalette(palette)

            um = GUI_User_Mic(self)
            um.start()

            umi = GUI_User_Mic_indicator(self)
            umi.signal_mic_waiting.connect(self.UserChat_Mic_indicator_waiting)
            umi.signal_mic_recording.connect(self.UserChat_Mic_indicator_recording)
            umi.signal_mic_off.connect(self.UserChat_Mic_indicator_off)
            umi.start()

        else:
            aprint("User Mic OFF")
            palette = self.UC_Bt_Mic.palette()
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(225, 0, 0)) #red
            self.UC_Bt_Mic.setPalette(palette)

    def UserChat_Mic_indicator_waiting(self):
        palette = self.UC_Bt_Mic.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(0, 128, 0)) #green
        self.UC_Bt_Mic.setPalette(palette)
    
    def UserChat_Mic_indicator_recording(self):
        palette = self.UC_Bt_Mic.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 208, 67)) #yellow
        self.UC_Bt_Mic.setPalette(palette)
    
    def UserChat_Mic_indicator_off(self):
        palette = self.UC_Bt_Mic.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(225, 0, 0)) #red
        self.UC_Bt_Mic.setPalette(palette)

    def UserChat_Clear(self):
        aprint("User chat clear")
        self.UC_TE_Input.clear()


    def UserChat_Enter(self):
        user_chat_text = self.UC_TE_Input.toPlainText()
        
        if user_chat_text != "":
            uc_role = self.UC_CB_Role_select.currentText()

            if uc_role == "user":
                if self.UC_LE_username.text() == "":
                    user_chat_text_llm = f"{aivtui.GUI_User_Name} : {user_chat_text}"
                    user_chat_text_p = f"{aivtui.GUI_User_Name} :\n{user_chat_text}"

                else:
                    user_chat_text_llm = f"{self.UC_LE_username.text()} : {user_chat_text}"
                    user_chat_text_p = f"{self.UC_LE_username.text()} :\n{user_chat_text}"
                
                UC = GUI_User_Chat(self)
                UC.GUI_UserChat_Role = uc_role
                UC.GUI_UserChat_Input = user_chat_text_llm
                UC.start()

            elif uc_role == "system":
                aivtui.conversation.append({"role": "system", "content": user_chat_text})
                user_chat_text_p = f"System :\n{user_chat_text}"
                self.CH_TE_Conversation_history.append(f"{user_chat_text_p}\n\n----------\n")

            elif uc_role == "assistant":
                aivtui.conversation.append({"role": "assistant", "content": user_chat_text})
                user_chat_text_p = f"{aivtui.AIVT_Using_character} :\n{user_chat_text}"
                UC = GUI_User_Chat(self)
                UC.GUI_UserChat_Role = uc_role
                UC.GUI_UserChat_Input = user_chat_text
                UC.start()

            self.UC_TE_Input.clear()

            aprint(f"\nUser Chat Input ----------\n\n{user_chat_text_p}\n\n----------\n")


        else:
            aprint(f"Enter not thing")





    def Setting_User_Name(self):
        aivtui.GUI_User_Name = self.St_LE_User_Name.text()
        GUI_config["Setting"]["user_name"] = str(aivtui.GUI_User_Name)


    def Setting_Character_select(self):
        global GUI_config

        Character_name = self.St_CB_Character_select.currentText()

        path = os.path.join(aivtui.AIVT_Character_path, Character_name)
        if os.path.exists(path) and Character_name in aivtui.AIVT_Character_Names:
            if Character_name != aivtui.AIVT_Using_character:
                aprint(f"Character Name: {Character_name}")
                aivtui.AIVT_Using_character = Character_name
                GUI_config["Setting"]["character"] = Character_name

                previous_instruction_enhance_prompt = self.LLM_TE_Instruction_enhance.toPlainText()

                prompt = aivtui.get_instruction_enhance_prompt(aivtui.AIVT_Using_character)
                self.LLM_TE_Instruction_enhance.setPlainText(prompt)
                aivtui.GUI_LLM_parameters["instruction_enhance_prompt"] = prompt

                SCS = GUI_Setting_Character_select(self)
                SCS.Instruction_enhance_prompt = previous_instruction_enhance_prompt
                SCS.start()

        elif Character_name == "":
            return

        else:
            aprint(f"Character *{Character_name}* Not Found!\n!!! Plz Reload Character !!!")
            Character_name = aivtui.AIVT_Using_character
            GUI_config["Setting"]["character"] = Character_name
            self.St_CB_Character_select.setCurrentText(Character_name)

    def Setting_Refresh_available_character(self):
        global GUI_config

        aprint("Refresh available character")
        character_name = self.St_CB_Character_select.currentText()

        aivtui.Load_AIVT_Character()
        character_list = aivtui.AIVT_Character_Names

        self.St_CB_Character_select.clear()
        for name in character_list:
            self.St_CB_Character_select.addItem(name)

        if character_name in character_list:
            self.St_CB_Character_select.setCurrentText(character_name)
        else:
            character_name = self.St_CB_Character_select.currentText()

        aivtui.AIVT_Character_Names = character_list
        GUI_config["Setting"]["character"] = character_name



    def Setting_Tab_Position(self):
        aprint("Tab Position: " + self.St_CB_Tab_position.currentText())
        global GUI_config
        tabp = self.St_CB_Tab_position.currentText()
        tab_position_map = {
            "North": QtWidgets.QTabWidget.North,
            "South": QtWidgets.QTabWidget.South,
            "West": QtWidgets.QTabWidget.West,
            "East": QtWidgets.QTabWidget.East
        }
        self.MW_Tab.setTabPosition(tab_position_map[tabp])

        GUI_config["Setting"]["tab_position"] = tabp

    def Setting_Window_opacity(self):
        
        opacity= float(self.St_HS_Window_opacity.value()/100)
        self.setWindowOpacity(opacity)
        aprint("GUI window opacity = " + str(self.St_HS_Window_opacity.value()) + "%")


    def Setting_Select_AI_Voice_output_devices(self):
        global GUI_config

        devices_name = self.St_CB_AI_Voice_output_devices.currentText()

        if devices_name != "":
            aprint(f"AI Voice output device: {devices_name}")
            plau.play_audio_parameters["ai_voice_output_device_name"] = devices_name
            GUI_config["Setting"]["ai_voice_output_device_name"] = devices_name

    def Setting_Select_User_Mic_input_devices(self):
        global GUI_config

        devices_name = self.St_CB_User_Mic_iutput_devices.currentText()

        if devices_name != "":
            aprint(f"User Mic input device: {devices_name}")
            mcrc.User_Mic_parameters["input_device_name"] = devices_name
            GUI_config["Setting"]["user_mic_input_device_name"] = devices_name

    def Setting_Refresh_available_input_output_devices(self):
        global GUI_config
        aprint("Refresh available in&output devices")
        Available_output_device_list = plau.Get_available_output_devices_List()
        Available_input_device_list = mcrc.Get_available_input_devices_List()

        output_devices_name = plau.play_audio_parameters["ai_voice_output_device_name"]
        input_devices_name = mcrc.User_Mic_parameters["input_device_name"]

        self.St_CB_AI_Voice_output_devices.clear()
        self.St_CB_User_Mic_iutput_devices.clear()

        for name in Available_output_device_list:
            self.St_CB_AI_Voice_output_devices.addItem(name)
        for name in Available_input_device_list:
            self.St_CB_User_Mic_iutput_devices.addItem(name)

        if output_devices_name in Available_output_device_list:
            self.St_CB_AI_Voice_output_devices.setCurrentText(output_devices_name)
        else:
            output_devices_name = self.St_CB_AI_Voice_output_devices.currentText()
            plau.play_audio_parameters["ai_voice_output_device_name"] = output_devices_name

        if input_devices_name in Available_input_device_list:
            self.St_CB_User_Mic_iutput_devices.setCurrentText(input_devices_name)
        else:
            input_devices_name = self.St_CB_User_Mic_iutput_devices.currentText()
            mcrc.User_Mic_parameters["input_device_name"] = input_devices_name

        GUI_config["Setting"]["ai_voice_output_device_name"] = output_devices_name
        GUI_config["Setting"]["user_mic_input_device_name"] = input_devices_name


    def Setting_Read_user_chat(self):
        global GUI_config
        enble = self.St_cB_Read_user_chat.isChecked()
        aivtui.GUI_Setting_read_chat_now = enble
        GUI_config["Setting"]["read_user_chat"] = str(enble)
        aprint(f"Read user chat: {enble}")


    def Setting_User_mic_hotkey_using(self):
        enble = self.St_cB_User_mic_hotkey1.isChecked() or self.St_cB_User_mic_hotkey2.isChecked()
        mcrc.user_mic_status["mic_hotkeys_using"] = enble
        mcrc.user_mic_status["mic_hotkey_1_using"] = self.St_cB_User_mic_hotkey1.isChecked()
        mcrc.user_mic_status["mic_hotkey_2_using"] = self.St_cB_User_mic_hotkey2.isChecked()
        GUI_config["Setting"]["user_mic_hotkey_1_using"] = str(self.St_cB_User_mic_hotkey1.isChecked())
        GUI_config["Setting"]["user_mic_hotkey_2_using"] = str(self.St_cB_User_mic_hotkey2.isChecked())

    def Setting_User_mic_hotkey1(self):
        if not mcrc.user_mic_status["mic_hotkey_1_detecting"]:
            palette = self.UC_Bt_Mic.palette()
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 0, 0)) #red
            self.St_Bt_User_mic_hotkey1.setPalette(palette)

            mcrc.user_mic_status["mic_hotkey_1_detecting"] = True
            such = GUI_Setting_User_mic_hotkey1(self)
            such.signal_key.connect(self.Setting_User_mic_hotkey1_set_key)
            such.signal_finish.connect(self.Setting_User_mic_hotkey1_finish_detect)
            such.start()

    def Setting_User_mic_hotkey1_set_key(self, key):
        global GUI_config
        mcrc.user_mic_status["mic_hotkey_1"] = key
        self.St_cB_User_mic_hotkey1.setText(f"Mic Hotkey 1 : {key}")
        GUI_config["Setting"]["user_mic_hotkey_1"] = key

    def Setting_User_mic_hotkey1_finish_detect(self):
        palette = self.UC_Bt_Mic.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(79, 79, 79)) #gary
        self.St_Bt_User_mic_hotkey1.setPalette(palette)


    def Setting_User_mic_hotkey2(self):
        if not mcrc.user_mic_status["mic_hotkey_2_detecting"]:
            palette = self.UC_Bt_Mic.palette()
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 0, 0)) #red
            self.St_Bt_User_mic_hotkey2.setPalette(palette)

            mcrc.user_mic_status["mic_hotkey_2_detecting"] = True
            such = GUI_Setting_User_mic_hotkey2(self)
            such.signal_key.connect(self.Setting_User_mic_hotkey2_set_key)
            such.signal_finish.connect(self.Setting_User_mic_hotkey2_finish_detect)
            such.start()

    def Setting_User_mic_hotkey2_set_key(self, key):
        global GUI_config
        mcrc.user_mic_status["mic_hotkey_2"] = key
        self.St_cB_User_mic_hotkey2.setText(f"Mic Hotkey 2 : {key}")
        GUI_config["Setting"]["user_mic_hotkey_2"] = key

    def Setting_User_mic_hotkey2_finish_detect(self):
        palette = self.UC_Bt_Mic.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(79, 79, 79)) #gary
        self.St_Bt_User_mic_hotkey2.setPalette(palette)



    def Setting_Doing_now(self):
        global GUI_config
        wdn = self.St_TE_Doing_now.toPlainText()
        GUI_config["Setting"]["doing_now"] = wdn
        aivtui.GUI_LLM_parameters["wdn_prompt"] = wdn
        aivtui.conversation[5] = {"role": "system", "content": wdn}





    def YouTube_channel_name(self):
        global GUI_config
        p = "yt"
        text = self.LC_LE_yt_channel_name.text().strip()
        live_chat.Live_chat_parameters[f"{p}_channel_name"] = text
        GUI_config["Live_Chat"][f"{p}_channel_name"] = text

    def YouTube_live_id(self):
        global GUI_config
        p = "yt"
        text = self.LC_LE_yt_live_id.text().strip()
        live_chat.Live_chat_parameters[f"{p}_live_id"] = text
        GUI_config["Live_Chat"][f"{p}_live_id"] = text


    def YouTube_chatroom(self):
        global GUI_config
        p = "yt"
        enble = self.LC_cB_yt_chatroom.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_chatroom"] = enble
        GUI_config["Live_Chat"][f"{p}_response_chatroom"] = str(enble)

    def YouTube_live_chat_read_chat_now(self):
        global GUI_config
        p = "yt"
        enble = self.LC_cB_yt_read_chat_now.isChecked()
        live_chat.Live_chat_parameters[f"{p}_live_chat_read_chat_now"] = enble
        GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] = str(enble)

    def YouTube_response_owner(self):
        global GUI_config
        p = "yt"
        enble = self.LC_cB_yt_owner.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_owner"] = enble
        GUI_config["Live_Chat"][f"{p}_response_owner"] = str(enble)

    def YouTube_response_vip(self):
        global GUI_config
        p = "yt"
        enble = self.LC_cB_yt_vip.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_vip"] = enble
        GUI_config["Live_Chat"][f"{p}_response_vip"] = str(enble)
    
    def YouTube_response_individual(self):
        global GUI_config
        p = "yt"
        enble = self.LC_cB_yt_response_individual.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_individual"] = enble
        GUI_config["Live_Chat"][f"{p}_response_individual"] = str(enble)

    
    def YouTube_wait_list_max(self):
        global GUI_config
        p = "yt"
        num = self.LC_SB_yt_chat_max_wait_list.value()
        live_chat.Live_chat_parameters[f"{p}_wait_list_max"] = num
        GUI_config["Live_Chat"][f"{p}_wait_list_max"] = str(num)

    def YouTube_chat_max_tokens(self):
        global GUI_config
        p = "yt"
        num = self.LC_SB_yt_chat_max_tokens.value()
        live_chat.Live_chat_parameters[f"{p}_chat_max_tokens"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_tokens"] = str(num)

    def YouTube_chat_max_response(self):
        global GUI_config
        p = "yt"
        num = self.LC_SB_yt_chat_max_response.value()
        live_chat.Live_chat_parameters[f"{p}_chat_max_response"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_response"] = str(num)


    def YouTube_live_chat_vip_names(self):
        global GUI_config
        p = "yt"
        text = self.LC_TE_yt_vip_names.toPlainText()
        GUI_config["Live_Chat"][f"{p}_live_chat_vip_names"] = text
        live_chat.Live_chat_parameters[f"{p}_live_chat_vip_names"] = [name.strip() for name in text.split("/") if name.strip()]

    def YouTube_live_chat_ban_names(self):
        global GUI_config
        p = "yt"
        text = self.LC_TE_yt_ban_names.toPlainText()
        GUI_config["Live_Chat"][f"{p}_live_chat_ban_names"] = text
        live_chat.Live_chat_parameters[f"{p}_live_chat_ban_names"] = [name.strip() for name in text.split("/") if name.strip()]



    def Twitch_channel_name(self):
        global GUI_config
        p = "tw"
        text = self.LC_LE_tw_channel_name.text().strip()
        live_chat.Live_chat_parameters[f"{p}_channel_name"] = text
        GUI_config["Live_Chat"][f"{p}_channel_name"] = text


    def Twitch_chatroom(self):
        global GUI_config
        p = "tw"
        enble = self.LC_cB_tw_chatroom.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_chatroom"] = enble
        GUI_config["Live_Chat"][f"{p}_response_chatroom"] = str(enble)

    def Twitch_live_chat_read_chat_now(self):
        global GUI_config
        p = "tw"
        enble = self.LC_cB_tw_read_chat_now.isChecked()
        live_chat.Live_chat_parameters[f"{p}_live_chat_read_chat_now"] = enble
        GUI_config["Live_Chat"][f"{p}_live_chat_read_chat_now"] = str(enble)

    def Twitch_response_owner(self):
        global GUI_config
        p = "tw"
        enble = self.LC_cB_tw_owner.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_owner"] = enble
        GUI_config["Live_Chat"][f"{p}_response_owner"] = str(enble)

    def Twitch_response_vip(self):
        global GUI_config
        p = "tw"
        enble = self.LC_cB_tw_vip.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_vip"] = enble
        GUI_config["Live_Chat"][f"{p}_response_vip"] = str(enble)
    
    def Twitch_response_individual(self):
        global GUI_config
        p = "tw"
        enble = self.LC_cB_tw_response_individual.isChecked()
        live_chat.Live_chat_parameters[f"{p}_response_individual"] = enble
        GUI_config["Live_Chat"][f"{p}_response_individual"] = str(enble)

    
    def Twitch_wait_list_max(self):
        global GUI_config
        p = "tw"
        num = self.LC_SB_tw_chat_max_wait_list.value()
        live_chat.Live_chat_parameters[f"{p}_wait_list_max"] = num
        GUI_config["Live_Chat"][f"{p}_wait_list_max"] = str(num)

    def Twitch_chat_max_tokens(self):
        global GUI_config
        p = "tw"
        num = self.LC_SB_tw_chat_max_tokens.value()
        live_chat.Live_chat_parameters[f"{p}_chat_max_tokens"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_tokens"] = str(num)

    def Twitch_chat_max_response(self):
        global GUI_config
        p = "tw"
        num = self.LC_SB_tw_chat_max_response.value()
        live_chat.Live_chat_parameters[f"{p}_chat_max_response"] = num
        GUI_config["Live_Chat"][f"{p}_chat_max_response"] = str(num)


    def Twitch_live_chat_vip_names(self):
        global GUI_config
        p = "tw"
        text = self.LC_TE_tw_vip_names.toPlainText()
        GUI_config["Live_Chat"][f"{p}_live_chat_vip_names"] = text
        live_chat.Live_chat_parameters[f"{p}_live_chat_vip_names"] = [name.strip() for name in text.split("/") if name.strip()]

    def Twitch_live_chat_ban_names(self):
        global GUI_config
        p = "tw"
        text = self.LC_TE_tw_ban_names.toPlainText()
        GUI_config["Live_Chat"][f"{p}_live_chat_ban_names"] = text
        live_chat.Live_chat_parameters[f"{p}_live_chat_ban_names"] = [name.strip() for name in text.split("/") if name.strip()]





    def LLM_Gemini(self):
        global GUI_config
        using = "Gemini"
        GUI_config["LLM"]["using"] = using
        aivtui.GUI_LLM_parameters["model"] = using
        aprint("LLM selected: Gemini")

    def LLM_GPT(self):
        global GUI_config
        using = "GPT"
        GUI_config["LLM"]["using"] = using
        aivtui.GUI_LLM_parameters["model"] = using
        aprint("LLM selected: GPT")


    def LLM_instruction_enhance(self):
        global GUI_config
        enble = self.LLM_cB_Instruction_enhance.isChecked()
        aivtui.GUI_LLM_parameters["instruction_enhance"] = enble
        GUI_config["LLM"]["instruction_enhance"] = str(enble)
        aprint(f"Instruction enhance: {enble}")

    def LLM_instruction_enhance_i(self):
        global GUI_config
        i = self.LLM_SB_Instruction_enhance.value()
        aivtui.GUI_LLM_parameters["instruction_enhance_i"] = i
        GUI_config["LLM"]["instruction_enhance_i"] = str(i)
        aprint(f"Instruction enhance: {i}")

    def LLM_instruction_enhance_prompt_change(self):
        aivtui.GUI_LLM_parameters["instruction_enhance_prompt"] = self.LLM_TE_Instruction_enhance.toPlainText()



    def Gemini_Select_model(self):
        global GUI_config
        model = self.LLM_CB_Ge_Model.currentText()
        gemini.gemini_parameters["model"] = model
        GUI_config["LLM_Gemini"]["model"] = model
        aprint(f"Gemini model selected: {model}")

        model_max_input_tokens = gemini.gemini_models_max_input_tokens[gemini.gemini_parameters["model"]]
        self.LLM_SB_Ge_Max_input_tokens.setMaximum(model_max_input_tokens)
        model_max_output_tokens = gemini.gemini_models_max_output_tokens[gemini.gemini_parameters["model"]]
        self.LLM_SB_Ge_Max_output_tokens.setMaximum(model_max_output_tokens)


    def Gemini_max_input_tokens(self):
        global GUI_config
        tokens = self.LLM_SB_Ge_Max_input_tokens.value()
        gemini.gemini_parameters["max_input_tokens"] = tokens
        GUI_config["LLM_Gemini"]["max_input_tokens"] = str(tokens)
        aprint(f"Gemini max input tokens: {tokens}")

    def Gemini_max_output_tokens(self):
        global GUI_config
        tokens = self.LLM_SB_Ge_Max_output_tokens.value()
        gemini.gemini_parameters["max_output_tokens"] = tokens
        GUI_config["LLM_Gemini"]["max_output_tokens"] = str(tokens)
        aprint(f"Gemini max output tokens: {tokens}")

    def Gemini_temperature(self):
        global GUI_config
        temp = round(self.LLM_DSB_Ge_Temperature.value(), 2)

        if temp < 0:
            temp = 0.00
        elif temp > 1:
            temp = 1.00

        gemini.gemini_parameters["temperature"] = temp
        GUI_config["LLM_Gemini"]["temperature"] = str(temp)
        aprint(f"Gemini temperature: {temp}")

    def Gemini_timeout(self):
        global GUI_config
        timeout = self.LLM_SB_Ge_Timeout.value()
        gemini.gemini_parameters["timeout"] = timeout
        GUI_config["LLM_Gemini"]["timeout"] = str(timeout)
        aprint(f"Gemini timeout: {timeout}s")

    def Gemini_retry(self):
        global GUI_config
        retry = self.LLM_SB_Ge_Retry.value()
        gemini.gemini_parameters["retry"] = retry
        GUI_config["LLM_Gemini"]["retry"] = str(retry)
        aprint(f"Gemini retry: {retry}")



    def GPT_Select_model(self):
        global GUI_config
        model = self.LLM_CB_GPT_Model.currentText()
        gpt.gpt_parameters["model"] = model
        GUI_config["LLM_GPT"]["model"] = model
        aprint(f"GPT model selected: {model}")

        model_max_input_tokens = gpt.gpt_models_max_input_tokens[gpt.gpt_parameters["model"]]
        self.LLM_SB_GPT_Max_input_tokens.setMaximum(model_max_input_tokens)
        model_max_output_tokens = gpt.gpt_models_max_output_tokens[gpt.gpt_parameters["model"]]
        self.LLM_SB_GPT_Max_output_tokens.setMaximum(model_max_output_tokens)


    def GPT_max_input_tokens(self):
        global GUI_config
        tokens = self.LLM_SB_GPT_Max_input_tokens.value()
        gpt.gpt_parameters["max_input_tokens"] = tokens
        GUI_config["LLM_GPT"]["max_input_tokens"] = str(tokens)
        aprint(f"GPT max input tokens: {tokens}")

    def GPT_max_output_tokens(self):
        global GUI_config
        tokens = self.LLM_SB_GPT_Max_output_tokens.value()
        gpt.gpt_parameters["max_output_tokens"] = tokens
        GUI_config["LLM_GPT"]["max_output_tokens"] = str(tokens)
        aprint(f"GPT max output tokens: {tokens}")

    def GPT_temperature(self):
        global GUI_config
        temp = round(self.LLM_DSB_GPT_Temperature.value(), 2)

        if temp < 0:
            temp = 0.00
        elif temp > 2:
            temp = 2.00

        GUI_config["LLM_GPT"]["temperature"] = str(temp)
        gpt.gpt_parameters["temperature"] = temp
        aprint(f"GPT temperature: {temp}")

    def GPT_timeout(self):
        global GUI_config
        timeout = self.LLM_SB_GPT_Timeout.value()
        gpt.gpt_parameters["timeout"] = timeout
        GUI_config["LLM_GPT"]["timeout"] = str(timeout)
        aprint(f"GPT timeout: {timeout}s")

    def GPT_retry(self):
        global GUI_config
        retry = self.LLM_SB_GPT_Retry.value()
        gpt.gpt_parameters["retry"] = retry
        GUI_config["LLM_GPT"]["retry"] = str(retry)
        aprint(f"GPT retry: {retry}")





    def TTS_EdgeTTS(self):
        global GUI_config
        using = "EdgeTTS"
        aivtui.GUI_TTS_Using = using
        GUI_config["TextToSpeech"]["using"] = using
        aprint("TTS selected: EdgeTTS")

    def TTS_OpenAITTS(self):
        global GUI_config
        using = "OpenAITTS"
        aivtui.GUI_TTS_Using = using
        GUI_config["TextToSpeech"]["using"] = using
        aprint("TTS selected: OpenAITTS")


    def EdgeTTS_Select_voice(self):
        global GUI_config
        voice = self.TTS_CB_ET_Voice.currentText()
        if voice:
            edgetts.edgetts_parameters["voice"] = voice
            GUI_config["EdgeTTS"]["voice"] = voice
            aprint(f"EdgeTTS voice selected: {voice}")

            if self.TTS_CB_ET_Gender.currentText() == "Male":
                GUI_config["EdgeTTS"]["voice_male"] = voice
            elif self.TTS_CB_ET_Gender.currentText() == "Female":
                GUI_config["EdgeTTS"]["voice_female"] = voice

    def EdgeTTS_Select_gender(self):
        global GUI_config
        gender = self.TTS_CB_ET_Gender.currentText()
        voice = edgetts.edgetts_parameters["voice"]
        aprint("EdgeTTS gender selected: " + gender)

        if self.TTS_CB_ET_Gender.currentText() == "Male":
            voice_list = edgetts.filter_voices_by_gender(edgetts.EdgeTTS_Voice_dict, "Male")
            if voice in voice_list:
                GUI_config["EdgeTTS"]["voice_male"] = voice
            else:
                GUI_config["EdgeTTS"]["voice_Female"] = voice
                voice = GUI_config["EdgeTTS"]["voice_male"] 

        elif self.TTS_CB_ET_Gender.currentText() == "Female":
            voice_list = edgetts.filter_voices_by_gender(edgetts.EdgeTTS_Voice_dict, "Female")
            if voice in voice_list:
                GUI_config["EdgeTTS"]["voice_female"] = voice
            else:
                GUI_config["EdgeTTS"]["voice_male"] = voice
                voice = GUI_config["EdgeTTS"]["voice_Female"]
        
        else:
            voice_list = edgetts.filter_voices_by_gender(edgetts.EdgeTTS_Voice_dict, "All")

        self.TTS_CB_ET_Voice.clear()
        for name in voice_list:
            self.TTS_CB_ET_Voice.addItem(name)

        self.TTS_CB_ET_Voice.setCurrentText(voice)
        edgetts.edgetts_parameters["voice"] = voice
        GUI_config["EdgeTTS"]["voice"] = voice

    def EdgeTTS_pitch(self):
        global GUI_config
        edgetts_pitch = self.TTS_SB_ET_Pitch.value()
        GUI_config["EdgeTTS"]["pitch"] = str(edgetts_pitch)
        aprint(f"EdgeTTS pitch: {edgetts_pitch}Hz")

        if edgetts_pitch >= 0:
            edgetts_pitch = f"+{edgetts_pitch}Hz"
        else:
            edgetts_pitch = f"{edgetts_pitch}Hz"
        edgetts.edgetts_parameters["pitch"] = edgetts_pitch

    def EdgeTTS_rate(self):
        global GUI_config
        edgetts_rate = self.TTS_SB_ET_Rate.value()
        GUI_config["EdgeTTS"]["rate"] = str(edgetts_rate)
        aprint(f"EdgeTTS rate: {edgetts_rate}%")

        if edgetts_rate >= 0:
            edgetts_rate = f"+{edgetts_rate}%"
        else:
            edgetts_rate = f"{edgetts_rate}%"
        edgetts.edgetts_parameters["rate"] = edgetts_rate

    def EdgeTTS_volume(self):
        global GUI_config
        edgetts_volume = self.TTS_SB_ET_Volume.value()
        GUI_config["EdgeTTS"]["volume"] = str(edgetts_volume)
        aprint(f"EdgeTTS volume: {edgetts_volume}%")

        if edgetts_volume >= 0:
            edgetts_volume = f"+{edgetts_volume}%"
        else:
            edgetts_volume = f"{edgetts_volume}%"
        edgetts.edgetts_parameters["volume"] = edgetts_volume

    def EdgeTTS_timeout(self):
        global GUI_config
        edgetts_timeout = self.TTS_SB_ET_Timeout.value()
        aprint(f"EdgeTTS timeout: {edgetts_timeout}s")
        GUI_config["EdgeTTS"]["timeout"] = str(edgetts_timeout)
        edgetts.edgetts_parameters["timeout"] = edgetts_timeout



    def OpenAITTS_Select_voice(self):
        global GUI_config
        voice = self.TTS_CB_OT_Voice.currentText()
        openaitts.openaitts_parameters["voice"] = voice
        GUI_config["OpenAITTS"]["voice"] = voice
        aprint("OpenAITTS voice selected: " + voice)

    def OpenAITTS_Select_model(self):
        global GUI_config
        model = self.TTS_CB_OT_Model.currentText()
        openaitts.openaitts_parameters["model"] = model
        GUI_config["OpenAITTS"]["model"] = model
        aprint("OpenAITTS model selected: " + model)

    def OpenAITTS_speed(self):
        global GUI_config
        openaitts_speed = round(self.TTS_DSB_OT_Speed.value(), 2) 
        GUI_config["OpenAITTS"]["speed"] = str(openaitts_speed)
        openaitts.openaitts_parameters["speed"] = openaitts_speed
        aprint(f"OpenAITTS speed: {openaitts_speed}")

    def OpenAITTS_timeout(self):
        global GUI_config
        openaitts_timeout = self.TTS_SB_OT_Timeout.value()
        GUI_config["OpenAITTS"]["timeout"] = str(openaitts_timeout)
        openaitts.openaitts_parameters["timeout"] = round(float(openaitts_timeout), 1)
        aprint(f"OpenAITTS timeout: {openaitts_timeout}s")





    def Whisper_Select_Inference(self):
        global GUI_config
        Whisper_Inference = self.Wh_CB_Inference.currentText()
        aivtui.OpenAI_Whisper_Inference = Whisper_Inference
        GUI_config["Whisper"]["inference"] = Whisper_Inference
        aprint("Whisper inference selected: " + Whisper_Inference)

        if Whisper_Inference == "Local" and whisper.whisper_status["loaded_model"] == "" and mcrc.user_mic_status["mic_on"]:
            WML = Whisper_model_load(self)
            WML.start()


    def Whisper_Select_Whisper_model_name(self):
        global GUI_config
        name = self.Wh_CB_Whisper_model_name.currentText()
        whisper.whisper_status["gui_selected_model"] = name
        GUI_config["Whisper"]["model_name"] = name
        aprint(f"Whisper model selected: {name}")


    def Whisper_Refresh_available_whisper_model(self):
        global GUI_config
        aprint("Refresh available whisper model list")
        Available_whisper_model_list = whisper.get_available_model_names_list()

        whisper_status_gui_selected_model = whisper.whisper_status["gui_selected_model"]

        self.Wh_CB_Whisper_model_name.clear()

        for name in Available_whisper_model_list:
            self.Wh_CB_Whisper_model_name.addItem(name)

        if whisper_status_gui_selected_model in Available_whisper_model_list:
            self.Wh_CB_Whisper_model_name.setCurrentText(whisper_status_gui_selected_model)
        else:
            whisper_status_gui_selected_model = self.Wh_CB_Whisper_model_name.currentText()
            whisper.whisper_status["gui_selected_model"] = whisper_status_gui_selected_model

        GUI_config["Whisper"]["model_name"] = whisper_status_gui_selected_model

    def Whisper_model_load(self):
        wml = Whisper_model_load(self)
        wml.start()

    def Whisper_model_unload(self):
        wmu = Whisper_model_unload(self)
        wmu.start()


    def Whisper_Select_Language(self):
        global GUI_config
        text = self.Wh_CB_Language.currentText()
        whisper.whisper_parameters["user_mic_language"] = text
        whisper_api.whisper_parameters["user_mic_language"] = text
        GUI_config["Whisper"]["language"] = text
        aprint(f"Whisper language selected: {text}")

    def Whisper_max_tokens(self):
        global GUI_config
        value = self.Wh_SB_Max_tokens.value()
        whisper.whisper_parameters["max_tokens"] = value
        GUI_config["Whisper"]["max_tokens"] = str(value)
        aprint(f"Whisper max tokens: {value}")

    def Whisper_temperature(self):
        global GUI_config
        value = round(self.Wh_DSB_Temperature.value(), 1)

        if value < 0:
            value = 0.0
        elif value > 1:
            value = 1.0
        
        whisper.whisper_parameters["temperature"] = value
        whisper_api.whisper_parameters["temperature"] = value
        GUI_config["Whisper"]["temperature"] = str(value)
        aprint(f"Whisper temperature: {value}")

    def Whisper_timeout(self):
        global GUI_config
        value = self.Wh_SB_Timeout.value()
        whisper.whisper_parameters["timeout"] = value
        whisper_api.whisper_parameters["timeout"] = value
        GUI_config["Whisper"]["timeout"] = str(value)
        aprint(f"Whisper timeout: {value}s")

    def Whisper_prompt(self):
        global GUI_config
        text = self.Wh_TE_Prompt.toPlainText()
        whisper.whisper_parameters["prompt"] = text
        whisper_api.whisper_parameters["prompt"] = text
        GUI_config["Whisper"]["prompt"] = str(text)





    def OBS_subtitles_formatter(self):
        global GUI_config
        enble = self.OBS_cB_Subtitles_formatter.isChecked()
        obsws.OBS_subtitles_parameters["subtitles_formatter"] = enble
        GUI_config["OBS_Subtitles"]["subtitles_formatter"] = str(enble)
        aprint(f"OBS Subtitles formatter: {enble}")

    def OBS_Select_subtitles_formatter_version(self):
        global GUI_config
        ver = self.OBS_CB_Subtitles_formatter_version.currentText()
        obsws.OBS_subtitles_parameters["subtitles_formatter_version"] = ver
        GUI_config["OBS_Subtitles"]["subtitles_formatter_version"] = ver
        aprint(f"OBS Subtitles formatter selected: {ver}")



    def OBS_chat_now_subtitles(self):
        global GUI_config
        enble = self.OBS_cB_Chat_now.isChecked()
        obsws.OBS_chat_now_sub_parameters["show"] = enble
        GUI_config["OBS_Chat_now_sub"]["show"] = str(enble)
        aprint(f"OBS Chat now subtitles: {enble}")

    def OBS_cn_clear(self):
        global GUI_config
        enble = self.OBS_cB_cn_Clear.isChecked()
        obsws.OBS_chat_now_sub_parameters["clear"] = enble
        GUI_config["OBS_Chat_now_sub"]["clear"] = str(enble)
        aprint(f"OBS Chat now clear: {enble}")

    def OBS_cn_sub_name(self):
        global GUI_config
        text = self.OBS_LE_cn_Sub_name.text()
        obsws.OBS_chat_now_sub_parameters["sub_name"] = text
        GUI_config["OBS_Chat_now_sub"]["sub_name"] = text

    def OBS_cn_sub_time(self):
        global GUI_config
        value = round(self.OBS_DSB_cn_Sub_time.value(), 1)
        obsws.OBS_chat_now_sub_parameters["sub_time"] = value
        GUI_config["OBS_Chat_now_sub"]["sub_time"] = str(value)
        aprint(f"OBS Chat now sub time: {value}s")

    def OBS_cn_sub_max_length(self):
        global GUI_config
        value = self.OBS_SB_cn_Max_length.value()
        obsws.OBS_chat_now_sub_parameters["sub_max_length"] = value
        GUI_config["OBS_Chat_now_sub"]["sub_max_length"] = str(value)
        aprint(f"OBS Chat now sub max length: {value}")

    def OBS_cn_sub_english_char_length(self):
        global GUI_config
        value = round(self.OBS_DSB_cn_English_char_length.value(), 2)
        obsws.OBS_chat_now_sub_parameters["sub_english_char_length"] = value
        GUI_config["OBS_Chat_now_sub"]["sub_english_char_length"] = str(value)
        aprint(f"OBS Chat now sub english char length: {value}")

    def OBS_cn_sub_base_line_count(self):
        global GUI_config
        value = self.OBS_SB_cn_Base_line_count.value()
        obsws.OBS_chat_now_sub_parameters["sub_base_line_count"] = value
        GUI_config["OBS_Chat_now_sub"]["sub_base_line_count"] = str(value)
        aprint(f"OBS Chat now sub base line count: {value}")

    def OBS_cn_sub_end_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_cn_End_delay.value(), 1)
        obsws.OBS_chat_now_sub_parameters["sub_end_delay"] = value
        GUI_config["OBS_Chat_now_sub"]["sub_end_delay"] = str(value)
        aprint(f"OBS Chat now sub end delay: {value}s")

    def OBS_cn_show_sub_filter_names(self):
        global GUI_config
        text = self.OBS_TE_cn_Show_sub_filter_names.toPlainText()
        list = [name.strip() for name in text.split('/') if name.strip() != '']
        obsws.OBS_chat_now_sub_parameters["show_sub_filter_names"] = list
        GUI_config["OBS_Chat_now_sub"]["show_sub_filter_names"] = text

    def OBS_cn_show_sub_filter_names_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_cn_Show_sub_filter_names_Delay.value(), 2)
        obsws.OBS_chat_now_sub_parameters["show_sub_filter_start_delay"] = value
        GUI_config["OBS_Chat_now_sub"]["show_sub_filter_start_delay"] = str(value)
        aprint(f"OBS Chat now show sub filter names delay: {value}s")

    def OBS_cn_hide_sub_filter_names(self):
        global GUI_config
        text = self.OBS_TE_cn_Hide_sub_filter_names.toPlainText()
        list = [name.strip() for name in text.split('/') if name.strip() != '']
        obsws.OBS_chat_now_sub_parameters["hide_sub_filter_names"] = list
        GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_names"] = text

    def OBS_cn_hide_sub_filter_names_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_cn_Hide_sub_filter_names_Delay.value(), 2)
        obsws.OBS_chat_now_sub_parameters["hide_sub_filter_start_delay"] = value
        GUI_config["OBS_Chat_now_sub"]["hide_sub_filter_start_delay"] = str(value)
        aprint(f"OBS Chat now hide sub filter names delay: {value}s")


    def OBS_ai_ans_subtitles(self):
        global GUI_config
        enble = self.OBS_cB_AI_ans.isChecked()
        obsws.OBS_ai_ans_sub_parameters["show"] = enble
        GUI_config["OBS_AI_ans_sub"]["show"] = str(enble)
        aprint(f"OBS AI ans subtitles: {enble}")

    def OBS_aa_clear(self):
        global GUI_config
        enble = self.OBS_cB_aa_Clear.isChecked()
        obsws.OBS_ai_ans_sub_parameters["clear"] = enble
        GUI_config["OBS_AI_ans_sub"]["clear"] = str(enble)
        aprint(f"OBS AI ans clear: {enble}")

    def OBS_aa_sub_name(self):
        global GUI_config
        text = self.OBS_LE_aa_Sub_name.text()
        obsws.OBS_ai_ans_sub_parameters["sub_name"] = text
        GUI_config["OBS_AI_ans_sub"]["sub_name"] = text

    def OBS_aa_remove_original_text_wrap(self):
        global GUI_config
        enble = self.OBS_cB_aa_Remove_original_text_wrap.isChecked()
        obsws.OBS_ai_ans_sub_parameters["remove_original_text_wrap"] = enble
        GUI_config["OBS_AI_ans_sub"]["remove_original_text_wrap"] = str(enble)
        aprint(f"OBS AI ans remove original text wrap: {enble}")

    def OBS_aa_sub_max_length(self):
        global GUI_config
        value = self.OBS_SB_aa_Max_length.value()
        obsws.OBS_ai_ans_sub_parameters["sub_max_length"] = value
        GUI_config["OBS_AI_ans_sub"]["sub_max_length"] = str(value)
        aprint(f"OBS AI ans sub max length: {value}")

    def OBS_aa_sub_english_char_length(self):
        global GUI_config
        value = round(self.OBS_DSB_aa_English_char_length.value(), 2)
        obsws.OBS_ai_ans_sub_parameters["sub_english_char_length"] = value
        GUI_config["OBS_AI_ans_sub"]["sub_english_char_length"] = str(value)
        aprint(f"OBS AI ans sub english char length: {value}")

    def OBS_aa_sub_base_line_count(self):
        global GUI_config
        value = self.OBS_SB_aa_Base_line_count.value()
        obsws.OBS_ai_ans_sub_parameters["sub_base_line_count"] = value
        GUI_config["OBS_AI_ans_sub"]["sub_base_line_count"] = str(value)
        aprint(f"OBS AI ans sub base line count: {value}")

    def OBS_aa_sub_end_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_aa_End_delay.value(), 1)
        obsws.OBS_ai_ans_sub_parameters["sub_end_delay"] = value
        GUI_config["OBS_AI_ans_sub"]["sub_end_delay"] = str(value)
        aprint(f"OBS AI ans sub end delay: {value}s")

    def OBS_aa_show_sub_filter_names(self):
        global GUI_config
        text = self.OBS_TE_aa_Show_sub_filter_names.toPlainText()
        list = [name.strip() for name in text.split('/') if name.strip() != '']
        obsws.OBS_ai_ans_sub_parameters["show_sub_filter_names"] = list
        GUI_config["OBS_AI_ans_sub"]["show_sub_filter_names"] = text

    def OBS_aa_show_sub_filter_names_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_aa_Show_sub_filter_names_Delay.value(), 2)
        obsws.OBS_ai_ans_sub_parameters["show_sub_filter_start_delay"] = value
        GUI_config["OBS_AI_ans_sub"]["show_sub_filter_start_delay"] = str(value)
        aprint(f"OBS AI ans show sub filter names delay: {value}s")

    def OBS_aa_hide_sub_filter_names(self):
        global GUI_config
        text = self.OBS_TE_aa_Hide_sub_filter_names.toPlainText()
        list = [name.strip() for name in text.split('/') if name.strip() != '']
        obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_names"] = list
        GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_names"] = text

    def OBS_aa_hide_sub_filter_names_delay(self):
        global GUI_config
        value = round(self.OBS_DSB_aa_Hide_sub_filter_names_Delay.value(), 2)
        obsws.OBS_ai_ans_sub_parameters["hide_sub_filter_start_delay"] = value
        GUI_config["OBS_AI_ans_sub"]["hide_sub_filter_start_delay"] = str(value)
        aprint(f"OBS AI ans hide sub filter names delay: {value}s")





    def VTSP_Trigger_first(self):
        global GUI_config
        enble = self.VTSP_cB_Trigger_first.isChecked()
        vtsp.AIVT_hotkeys_parameters["trigger_first"] = enble
        GUI_config["VTube_Studio_Plug"]["trigger_first"] = str(enble)
        aprint(f"VTSP Trigger first: {enble}")

    def VTSP_Wait_until_hotkeys_complete(self):
        global GUI_config
        enble = self.VTSP_cB_Wait_until_hotkeys_complete.isChecked()
        aivtui.GUI_VTSP_wait_until_hotkeys_complete = enble
        GUI_config["VTube_Studio_Plug"]["wait_until_hotkeys_complete"] = str(enble)
        aprint(f"VTSP wait until hotkeys complete: {enble}")

    def VTSP_Sentiment_analysis(self):
        global GUI_config
        enble = self.VTSP_cB_Sentiment_analysis.isChecked()
        vtsp.AIVT_hotkeys_parameters["sentiment_analysis"] = enble
        GUI_config["VTube_Studio_Plug"]["sentiment_analysis"] = str(enble)
        aprint(f"VTSP Sentiment analysis: {enble}")

    def VTSP_Select_Sentiment_analysis(self):
        global GUI_config
        text = self.VTSP_CB_Sentiment_analysis.currentText()
        vtsp.AIVT_hotkeys_parameters["sentiment_analysis_model"] = text
        GUI_config["VTube_Studio_Plug"]["sentiment_analysis_modle"] = text
        aprint(f"VTSP Select Sentiment analysis model: {text}")


    def VTSP_Idle_animation(self):
        text = self.VTSP_TE_Idle_ani.toPlainText()
        vtsp.AIVT_hotkeys_parameters["idle_ani"] = text
        GUI_config["VTube_Studio_Plug"]["idle_ani"] = text


    def VTSP_Normal(self):
        emo = "normal"
        enble = self.VTSP_cB_Normal.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Normal_kn(self):
        emo = "normal"
        text = self.VTSP_TE_Normal.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Happy(self):
        emo = "happy"
        enble = self.VTSP_cB_Happy.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Happy_kn(self):
        emo = "happy"
        text = self.VTSP_TE_Happy.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Shy(self):
        emo = "shy"
        enble = self.VTSP_cB_Shy.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Shy_kn(self):
        emo = "shy"
        text = self.VTSP_TE_Shy.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Proud(self):
        emo = "proud"
        enble = self.VTSP_cB_Proud.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Proud_kn(self):
        emo = "proud"
        text = self.VTSP_TE_Proud.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Shock(self):
        emo = "shock"
        enble = self.VTSP_cB_Shock.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Shock_kn(self):
        emo = "shock"
        text = self.VTSP_TE_Shock.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Sad(self):
        emo = "sad"
        enble = self.VTSP_cB_Sad.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Sad_kn(self):
        emo = "sad"
        text = self.VTSP_TE_Sad.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Angry(self):
        emo = "angry"
        enble = self.VTSP_cB_Angry.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Angry_kn(self):
        emo = "angry"
        text = self.VTSP_TE_Angry.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Embarrass(self):
        emo = "embarrass"
        enble = self.VTSP_cB_Embarrass.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Embarrass_kn(self):
        emo = "embarrass"
        text = self.VTSP_TE_Embarrass.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Afraid(self):
        emo = "afraid"
        enble = self.VTSP_cB_Afraid.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Afraid_kn(self):
        emo = "afraid"
        text = self.VTSP_TE_Afraid.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text


    def VTSP_Confuse(self):
        emo = "confuse"
        enble = self.VTSP_cB_Confuse.isChecked()
        vtsp.AIVT_hotkeys_parameters[emo] = enble
        GUI_config["VTube_Studio_Plug"][emo] = str(enble)

        in_list = emo in vtsp.AIVT_hotkeys_parameters["Emo_state_categories"]
        if enble and not in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].append(emo)
        elif not enble and in_list:
            vtsp.AIVT_hotkeys_parameters["Emo_state_categories"].remove(emo)

    def VTSP_Confuse_kn(self):
        emo = "confuse"
        text = self.VTSP_TE_Confuse.toPlainText()
        vtsp.AIVT_hotkeys_parameters[f"{emo}_kn"] = text
        GUI_config["VTube_Studio_Plug"][f"{emo}_kn"] = text










# GUI QThreads

class GUI_Conversation_History_appender(QtCore.QThread):
    signal_Conversation_History_append = QtCore.Signal(str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        while aivtui.GUI_Running:
            if aivtui.GUI_Conversation_History_list:
                ch = aivtui.GUI_Conversation_History_list.pop(0)

                self.signal_Conversation_History_append.emit(
                        ch["chat_role"],
                        ch["chat_now"],
                        ch["ai_name"],
                        ch["ai_ans"],
                    )

            time.sleep(0.1)





class GUI_User_Mic(QtCore.QThread):
    signal_mic_waiting = QtCore.Signal()
    signal_mic_recording = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        if aivtui.OpenAI_Whisper_Inference == "Local" and whisper.whisper_status["loaded_model"] == "":
            whisper.load_model(model_name=whisper.whisper_status["gui_selected_model"])

        mcrc.Audio_frames_out = []
        mcrc.Mic_hotkey_pressed = False

        mcr = threading.Thread(target=mcrc.MC_Record)
        mcr.start()
        moc = threading.Thread(target=mcrc.MC_Output_checker)
        moc.start()

        while mcrc.user_mic_status["mic_on"]:
            if aivtui.OpenAI_Whisper_LLM_wait_list:
                ans_requst = aivtui.OpenAI_Whisper_LLM_wait_list.pop(0)
                chat_role = ans_requst["role"]
                chat_now = ans_requst["content"]
                ai_name = aivtui.AIVT_Using_character

                llm_ans = queue.Queue()

                llm_rt = threading.Thread(target=aivtui.LLM_Request_thread, args=(ans_requst, llm_ans, ))
                llm_rt.start()
                llm_rt.join()

                ai_ans = llm_ans.get()

                if ai_ans != "":
                    aivtui.GUI_AIVT_Speaking_wait_list.append(
                        {
                            "chat_role": chat_role,
                            "chat_now": chat_now,
                            "ai_ans": ai_ans,
                            "ai_name": ai_name,
                        }
                    )

            time.sleep(0.1)

        # Avoid mic off when MC_Output_checker is still running
        while mcrc.user_mic_status["mic_checker_running"]:
            time.sleep(0.1)

        if aivtui.OpenAI_Whisper_LLM_wait_list:
            ans_requst = aivtui.OpenAI_Whisper_LLM_wait_list.pop(0)
            chat_role = ans_requst["role"]
            chat_now = ans_requst["content"]
            ai_name = aivtui.AIVT_Using_character

            llm_ans = queue.Queue()

            llm_rt = threading.Thread(target=aivtui.LLM_Request_thread, args=(ans_requst, llm_ans, ))
            llm_rt.start()
            llm_rt.join()

            ai_ans = llm_ans.get()

            if ai_ans != "":
                aivtui.GUI_AIVT_Speaking_wait_list.append(
                        {
                            "chat_role": chat_role,
                            "chat_now": chat_now,
                            "ai_ans": ai_ans,
                            "ai_name": ai_name,
                        }
                    )

        mcr.join()
        moc.join()


class GUI_User_Mic_indicator(QtCore.QThread):
    signal_mic_waiting = QtCore.Signal()
    signal_mic_recording = QtCore.Signal()
    signal_mic_off = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        while not mcrc.user_mic_status["mic_record_running"]:
            time.sleep(0.1)
        self.signal_mic_waiting.emit()

        mic_hotkey_pressed_r = True

        while mcrc.user_mic_status["mic_on"]:
            if mcrc.Mic_hotkey_pressed and mic_hotkey_pressed_r:
                mic_hotkey_pressed_r = False
                self.signal_mic_recording.emit()

            if not mcrc.Mic_hotkey_pressed and not mic_hotkey_pressed_r:
                mic_hotkey_pressed_r = True
                self.signal_mic_waiting.emit()

            time.sleep(0.1)

        self.signal_mic_off.emit()



class GUI_User_Chat(QtCore.QThread):
    GUI_UserChat_Role = ""
    GUI_UserChat_Input = ""

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        ans_requst = {"role": self.GUI_UserChat_Role, "content": self.GUI_UserChat_Input}
        character_name = aivtui.AIVT_Using_character

        if self.GUI_UserChat_Role == "user":
            llm_ans = queue.Queue()
            
            llm_rt = threading.Thread(target=aivtui.LLM_Request_thread, args=(ans_requst, llm_ans, ))
            llm_rt.start()
            llm_rt.join()

            AI_Ans = llm_ans.get()

        elif self.GUI_UserChat_Role == "assistant":
            AI_Ans = self.GUI_UserChat_Input

        else:
            AI_Ans = ""


        if AI_Ans != "":
            aivtui.GUI_AIVT_Speaking_wait_list.append(
                    {
                        "chat_role": self.GUI_UserChat_Role,
                        "chat_now": self.GUI_UserChat_Input,
                        "ai_ans": AI_Ans,
                        "ai_name": character_name,
                    }
                )





class GUI_YT_LiveChat(QtCore.QThread):
    signal_YouTube_live_chat_connect = QtCore.Signal()
    signal_YouTube_live_chat_disconnect = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        live_chat.YouTube_LiveChat_boot_on()

        while live_chat.Live_Chat_Status["YouTube_live_chat"]:
            if not live_chat.Live_Chat_Status["YouTube_live_chat_alive"]:
                live_chat.Live_Chat_Status["YouTube_live_chat_retry"] = True
                self.signal_YouTube_live_chat_connect.emit()
            
            while live_chat.Live_Chat_Status["YouTube_live_chat_retry"]:
                time.sleep(0.01)

            time.sleep(0.02)

        self.signal_YouTube_live_chat_disconnect.emit()



class GUI_TW_LiveChat(QtCore.QThread):
    signal_Twitch_live_chat_disconnect = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        live_chat.Live_Chat_Status["Twitch_live_chat"] = True

        manager = multiprocessing.Manager()
        live_chat.live_chat_status = manager.dict()
        live_chat.live_chat_status['Twitch_live_chat'] = True
        live_chat.TW_LC_raw_list = manager.list()

        tlcc = multiprocessing.Process(target=live_chat.Twitch_live_chat_connect, args=(live_chat.live_chat_status, live_chat.TW_LC_raw_list))
        tlcc.start()

        tlcbo = threading.Thread(target=live_chat.Twitch_LiveChat_boot_on)
        tlcbo.start()

        while live_chat.Live_Chat_Status["Twitch_live_chat"]:
            time.sleep(0.1)

        tlcc.terminate()
        self.signal_Twitch_live_chat_disconnect.emit()





class GUI_AIVT_VTSP_authenticated(QtCore.QThread):
    signal_vtsp_authenticated_fail = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        vtsp.AIVT_VTSP_authenticated()

        if vtsp.AIVT_VTSP_Status["authenticated"]:
            via = threading.Thread(target=aivtui.AIVT_VTSP_Idle_Animation)
            via.start()
        else:
            self.signal_vtsp_authenticated_fail.emit()





class GUI_OBSWS_connect(QtCore.QThread):
    signal_OBSWS_connect_fail = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        obsws.OBSws_connect()
        if not obsws.OBS_Connected:
            self.signal_OBSWS_connect_fail.emit(False)

class GUI_OBSWS_disconnect(QtCore.QThread):

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        obsws.OBSws_disconnect()





class GUI_Setting_Character_select(QtCore.QThread):
    Instruction_enhance_prompt = ""

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global GUI_config
        aivtui.write_instruction_enhance_prompt(aivtui.AIVT_Using_character_previous, self.Instruction_enhance_prompt)
        aivtui.conversation_character_prompt_change(aivtui.AIVT_Using_character)



class GUI_Setting_User_mic_hotkey1(QtCore.QThread):
    signal_key = QtCore.Signal(str)
    signal_finish = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global GUI_config
        key = mcrc.Get_key_press()
        if not key == "esc":
            self.signal_key.emit(key, )

        self.signal_finish.emit()
        mcrc.user_mic_status["mic_hotkey_1_detecting"] = False


class GUI_Setting_User_mic_hotkey2(QtCore.QThread):
    signal_key = QtCore.Signal(str)
    signal_finish = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global GUI_config
        key = mcrc.Get_key_press()
        if not key == "esc":
            self.signal_key.emit(key, )

        self.signal_finish.emit()
        mcrc.user_mic_status["mic_hotkey_2_detecting"] = False





class Whisper_model_load(QtCore.QThread):

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global GUI_config
        whisper.load_model(model_name=whisper.whisper_status["gui_selected_model"])


class Whisper_model_unload(QtCore.QThread):

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global GUI_config
        whisper.unload_model()










if __name__ == '__main__':
    print("\n----------")
    aivtui.GUI_Running = True
    ssc = threading.Thread(target=aivtui.subtitles_speak_checker)
    ssc.start()

    try:
        app = QtWidgets.QApplication(sys.argv)
        window = AI_Vtuber_GUI()
        window.show()

        sys.exit(app.exec())

    finally:
        aivtui.GUI_Running = False
        mcrc.user_mic_status["mic_on"] = False
        live_chat.Live_Chat_Status["YouTube_live_chat"] = False
        live_chat.Live_Chat_Status["Twitch_live_chat"] = False
        live_chat.live_chat_status["Twitch_live_chat"] = False

        if obsws.OBS_Connected:
            obsws.OBSws_disconnect()

        GUI_config["Live_Chat"]["yt_response_chatroom"] = "False"
        GUI_config["Live_Chat"]["tw_response_chatroom"] = "False"

        aivtui.write_instruction_enhance_prompt(aivtui.AIVT_Using_character, aivtui.GUI_LLM_parameters["instruction_enhance_prompt"])

        with open(GUI_config_path, 'w', encoding="utf-8") as configfile:
            GUI_config.write(configfile)

        print("GUI Exit!\n!!! GUI Config Saved !!!")




