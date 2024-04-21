import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import threading
import random

import pyvts

from My_Tools.AIVT_print import aprint










AIVT_VTSP_Status = {
    "authenticated": False,
    "hotkey_trigger": False,
}

AIVT_hotkeys_parameters = {
    "trigger_first": False,
    "Emo_state_categories": ["normal", "happy", "shy", "proud", "shock", "sad", "angry", "embarrass", "afraid", "confuse"],
    "sentiment_analysis": False,
    "sentiment_analysis_model": "gemini-1.0-pro",
    "idle_ani": "",
    "idle_ani_previous": "",
    "normal": True,
    "normal_kn": "",
    "happy": True,
    "happy_kn": "",
    "shy": True,
    "shy_kn": "",
    "proud": True,
    "proud_kn": "",
    "shock": True,
    "shock_kn": "",
    "sad": True,
    "sad_kn": "",
    "angry": True,
    "angry_kn": "",
    "embarrass": True,
    "embarrass_kn": "",
    "afraid": True,
    "afraid_kn": "",
    "confuse": True,
    "confuse_kn": "",
}

AIVT_previous_ani_exp = {
    "idle_ani": "",
    "talking_ani": "",
    "talking_exp": "", 
}





def AIVT_VTSP_authenticated():
    global AIVT_VTSP_Status, aivt_vtsp

    authentication_token_path = "VtuberStudioPlug/VTSP_authentication_token.txt"

    AIVT_VTSP_info = {
    "plugin_name":"AIVT_VTSP",
    "developer":"PKevin",
    "authentication_token_path":authentication_token_path
    }

    aivt_vtsp = pyvts.vts(plugin_info=AIVT_VTSP_info)

    
    if os.path.exists(authentication_token_path):
        try:
            asyncio.run(async_AIVT_VTSP_authenticated())
            AIVT_VTSP_Status["authenticated"] = True
            print("!!! VTSP Authenticated Success !!!")

        except:
            try:
                asyncio.run(async_AIVT_VTSP_get_token_and_authenticated())
                AIVT_VTSP_Status["authenticated"] = True
                print("!!! VTSP Authenticated Success !!!")

            except:
                AIVT_VTSP_Status["authenticated"] = False
                print("!!! VTSP Authenticated Fail !!!")

    else:
        try:
            asyncio.run(async_AIVT_VTSP_get_token_and_authenticated())
            AIVT_VTSP_Status["authenticated"] = True
            print("!!! VTSP Authenticated Success !!!")

        except:
            AIVT_VTSP_Status["authenticated"] = False
            print("!!! VTSP Authenticated Fail !!!")


async def async_AIVT_VTSP_get_token_and_authenticated():
    global aivt_vtsp

    await aivt_vtsp.connect()
    await aivt_vtsp.request_authenticate_token()
    await aivt_vtsp.write_token()
    await aivt_vtsp.request_authenticate()
    await aivt_vtsp.close()

async def async_AIVT_VTSP_authenticated():
    global aivt_vtsp

    await aivt_vtsp.connect()
    await aivt_vtsp.read_token()
    await aivt_vtsp.request_authenticate()
    await aivt_vtsp.close()





lock_hnt = threading.Lock()

def VTSP_Hotkey_Names_Trigger(hotkey_names_list=[], command=None):
    global aivt_vtsp

    with lock_hnt:
        if AIVT_VTSP_Status["authenticated"] and len(hotkey_names_list) > 0:
            aprint(f"VTSP trigger hotkey names: {hotkey_names_list}")
            asyncio.run(async_VTSP_Hotkey_Names_Trigger(hotkey_names_list, command=command))


async def async_VTSP_Hotkey_Names_Trigger(hotkey_names, command=None):
    global aivt_vtsp

    await aivt_vtsp.connect()
    await aivt_vtsp.request_authenticate()

    for hotkey_name in hotkey_names:
        try:
            send_hotkey_request = aivt_vtsp.vts_request.requestTriggerHotKey(hotkey_name)
            await aivt_vtsp.request(send_hotkey_request)

        except Exception as e:
            aprint(f"!!! Trigger Hotkey *{hotkey_name}* Fail !!!")

    await aivt_vtsp.close()





def get_hotkey_names(text_kn, command=None):
    global AIVT_hotkeys_parameters

    items = [item.strip() for item in text_kn.split("/") if item.strip()]
    list1, list2, list3, list4 = [], [], [], []

    for item in items:
        if item.startswith("!"):
            list1.append(item[1:].strip())

        elif item.startswith("*"):
            list2.append(item[1:].strip())

        elif item.startswith("@"):
            list3.append(item[1:].strip())

        else:
            list4.append(item)


    all = []
    r_ani = []
    f_exp = []
    r_iexp = []
    r_exp = []

    if list1:
        if command == "idle_ani" and len(list1) > 1:
            i = 0

            while True:
                i += 10
                kn = random.choice(list1)
                if kn != AIVT_hotkeys_parameters["idle_ani_previous"]:
                    break

                if i > 10:
                    break

        else:
            kn = random.choice(list1)

        AIVT_hotkeys_parameters["idle_ani_previous"] = kn

        all.append(kn)
        r_ani.append(kn)

    if list2:
        for name in list2:
            if not name in all:
                all.append(name)
                f_exp.append(name)

    if list3:
        list3_r = []
        for name in list3:
            if not name in all:
                list3_r.append(name)

        if list3_r:
            kn = random.choice(list3_r)
            all.append(kn)
            r_iexp.append(kn)

    if list4:
        list4_r = []
        for name in list4:
            if not name in all:
                list4_r.append(name)

        if list4_r:
            kn = random.choice(list4)
            all.append(kn)
            r_exp.append(kn)


    result_list = {
        "all": all,
        "all_exp": f_exp+r_iexp+r_exp,
        "r_ani": r_ani,
        "f_exp": f_exp,
        "r_iexp": r_iexp,
        "r_exp": r_exp,
    }

    return result_list










if __name__ == "__main__":
    AIVT_VTSP_authenticated()
    AIVT_VTSP_Status["authenticated"] = True

    while AIVT_VTSP_Status["authenticated"]:
        input_text = input("Enter the names of hotkey (split by /) :\n")
        hotkey_names = [name.strip() for name in input_text.split("/") if name.strip()]
        VTSP_Hotkey_Names_Trigger(hotkey_names_list=hotkey_names)




