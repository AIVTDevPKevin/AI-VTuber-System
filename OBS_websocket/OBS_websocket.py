import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time

import obswebsocket as obsWS

import AIVT_Config










obsws = obsWS.obsws(AIVT_Config.OBS_WebSockets_ip, AIVT_Config.OBS_WebSockets_port, AIVT_Config.OBS_WebSockets_password)

OBS_Connected = False
OBS_Requesting = False
OBS_subtitles_formatter_versions = ["v2", "v3"]

OBS_subtitles_parameters = {
    "subtitles_formatter": True,
    "subtitles_formatter_version": "v3",
}

OBS_chat_now_sub_parameters = {
    "sub_name": "AIVT_CSub",
    "show": True,
    "clear": False,
    "sub_time": 3.0,
    "sub_max_length": 20,
    "sub_english_char_length": 0.50,
    "sub_base_line_count": 5,
    "sub_end_delay": 0.0,

    "show_sub_filter_names": ["Sub Appear"],
    "show_sub_filter_start_delay": 0.00,
    "show_sub_filter_end_delay": 0.00,

    "hide_sub_filter_names": ["Sub Disappear"],
    "hide_sub_filter_start_delay": 0.00,
    "hide_sub_filter_end_delay": 0.00,
}

OBS_ai_ans_sub_parameters = {
    "sub_name": "AIVT_Sub",
    "show": True,
    "clear": False,
    "remove_original_text_wrap": False,
    "sub_max_length": 20,
    "sub_english_char_length": 0.50,
    "sub_base_line_count": 5,
    "sub_end_delay": 0.0,

    "show_sub_filter_names": ["T Sub Appear"],
    "show_sub_filter_start_delay": 0.00,
    "show_sub_filter_end_delay": 0.00,

    "hide_sub_filter_names": ["T Sub Disappear"],
    "hide_sub_filter_start_delay": 0.00,
    "hide_sub_filter_end_delay": 0.00,
}





def OBSws_connect():
    global obsws, OBS_Connected

    try:
        obsws.connect()
        OBS_Connected = True
        print("!!! OBS WebSockets Connect Success !!!")

    except Exception as e:
        OBS_Connected = False
        print("!!! OBS WebSockets Connect Fail !!!\n{e}\n")


def OBSws_disconnect():
    global obsws, OBS_Connected, OBS_Requesting

    while OBS_Requesting:
        time.sleep(0.1)

    try:
        obsws.disconnect()
        OBS_Connected = False
        print("!!! OBS WebSockets Disconnect !!!")

    except Exception as e:
        OBS_Connected = True
        print(f"!!! OBS WebSockets Disconnect Fail !!!\n{e}\n")





def Set_Source_Text(text_name, text, start_delay=0, end_delay=0):
    global obsws, OBS_Connected, OBS_Requesting

    if OBS_Connected:
        OBS_Requesting = True
        time.sleep(start_delay)

        obsws.call(obsWS.requests.SetInputSettings(inputName=text_name, inputSettings={"text": text}))

        time.sleep(end_delay)
        OBS_Requesting = False



def Set_Source_Filter_Enabled(source_name, filter_names, filter_enabled, start_delay=0, end_delay=0):
    global obsws, OBS_Connected, OBS_Requesting

    if OBS_Connected:
        OBS_Requesting = True

        filter_names_list = []
        if isinstance(filter_names, str):
            filter_names_list.append(filter_names)

        elif isinstance(filter_names, list):
            filter_names_list.extend(filter_names)


        time.sleep(start_delay)

        for filter_name in filter_names_list:
            obsws.call(obsWS.requests.SetSourceFilterEnabled(sourceName=source_name, filterName=filter_name, filterEnabled=filter_enabled))

        time.sleep(end_delay)
        OBS_Requesting = False




