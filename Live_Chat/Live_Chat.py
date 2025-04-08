import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import threading
import queue
import random

import pytchat
from twitchio.ext import commands as twitch_commands

import AIVT_Config
import AI_Vtuber_UI as aivtui
import My_Tools.Token_Calculator as tokenC










Live_Chat_Status = {
    "YouTube_live_chat": False,
    "YouTube_live_chat_alive": False,
    "YouTube_live_chat_retry": False,
    "YouTube_live_chat_connect_fail_count": 0,
    "Twitch_live_chat": False,
    "llm_request_checker": False,
}

live_chat_status = {"Twitch_live_chat": False,}

Live_chat_parameters = {
    "yt_channel_name": "AI VTuber Dev PKevin",
    "yt_live_id": "qTmJ4YkziEk",
    "yt_live_chat_vip_names": [],
    "yt_live_chat_ban_names": [],
    "yt_live_chat_log": True,
    "yt_live_chat_read_chat_now": False,
    "yt_response_chatroom": False,
    "yt_response_owner": False,
    "yt_response_vip": False,
    "yt_response_individual": False,
    "yt_wait_list_max": 10,
    "yt_chat_max_tokens": 128,
    "yt_chat_max_response": 5,

    "tw_channel_name": "pkevin_ai_vtuber_dev",
    "tw_live_chat_vip_names": [],
    "tw_live_chat_ban_names": [],
    "tw_live_chat_log": True,
    "tw_live_chat_read_chat_now": False,
    "tw_response_chatroom": False,
    "tw_response_owner": False,
    "tw_response_vip": False,
    "tw_response_individual": False,
    "tw_wait_list_max": 10,
    "tw_chat_max_tokens": 128,
    "tw_chat_max_response": 5,
}

YT_LC_wait_list = []
TW_LC_raw_list = []
TW_LC_wait_list = []
Live_Chat_LLM_wait_list = []





def YouTube_live_chat_connect():
    global Live_Chat_Status, Live_chat_parameters, YT_live_chat

    try:
        YT_live_chat = pytchat.create(video_id=Live_chat_parameters["yt_live_id"])
        print(f"!!! YouTube Live ID: {Live_chat_parameters['yt_live_id']} Connect Success !!!\n")
        Live_Chat_Status["YouTube_live_chat"] = True
        Live_Chat_Status["YouTube_live_chat_alive"] = True
        Live_Chat_Status["YouTube_live_chat_connect_fail_count"] = 0

    except Exception as e:
        Live_Chat_Status["YouTube_live_chat_connect_fail_count"] += 1

        if Live_Chat_Status["YouTube_live_chat_connect_fail_count"] >= 50:
            print(f"!!! YouTube Live ID: {Live_chat_parameters['yt_live_id']} Connect Failed !!!{e}\n")
            Live_Chat_Status["YouTube_live_chat"] = False
            Live_Chat_Status["YouTube_live_chat_alive"] = False
            Live_Chat_Status["YouTube_live_chat_connect_fail_count"] = 0


def YouTube_live_chat_get_comments():
    global Live_Chat_Status, Live_chat_parameters, YT_live_chat, YT_LC_wait_list

    YT_LC_wait_list = []

    while Live_Chat_Status["YouTube_live_chat"]:
        while YT_live_chat.is_alive() and  Live_Chat_Status["YouTube_live_chat"]:
            time.sleep(0.1)

            try:
                chat_data = YT_live_chat.get()
                chat_comments = list(chat_data.sync_items())

                if chat_data and chat_comments:
                    chat_list = []

                    for c in chat_comments:
                        chat_author = c.author.name
                        chat_raw = c.message

                        if chat_author in Live_chat_parameters["yt_live_chat_ban_names"]:
                            continue

                        elif (c.author.isChatOwner and Live_chat_parameters["yt_response_owner"]) or chat_author in Live_chat_parameters["yt_live_chat_vip_names"]:
                            chat_now = {chat_author: chat_raw}
                            chat_list.append(chat_now)

                        elif tokenC.num_tokens_from_conversation([{"role": "user", "content": chat_raw}], "gpt-3.5-turbo")-9 < Live_chat_parameters["yt_chat_max_tokens"]:
                            chat_now = {chat_author: chat_raw}
                            chat_list.append(chat_now)

                        else:
                            if Live_chat_parameters["yt_live_chat_log"]:
                                print(f"!!! *{chat_author}* comment beyond max tokens - YouTube Live Chat !!!")

                    if chat_list:
                        YT_LC_wait_list.extend(chat_list)
                        if Live_chat_parameters["yt_live_chat_log"]:
                            chat_c = "\n\n".join([f"{key} : {d[key]}" for d in chat_list for key in d])
                            print(f"\nYouTube Live Chat ----------\n\n{chat_c}\n\n----------\n")

            except Exception as e:
                print(f"YouTube get livechat fail:\n{e}\n")
                break


        print(f"YouTube Live Chat Reonnecting...")
        Live_Chat_Status["YouTube_live_chat_alive"] = False
        while not Live_Chat_Status["YouTube_live_chat_alive"]:
            time.sleep(0.01)

    Live_Chat_Status["YouTube_live_chat"] = False

def YouTube_live_chat_pick_comments():
    global Live_Chat_Status, Live_chat_parameters, YT_LC_wait_list, Live_Chat_LLM_wait_list

    while Live_Chat_Status["YouTube_live_chat"]:
        if Live_chat_parameters["yt_response_chatroom"] and YT_LC_wait_list:
            c = len(YT_LC_wait_list)
            chat_list = []
            while c > 0:
                c -= 1
                chat_list.append(YT_LC_wait_list.pop(0))

            chat_list.reverse()

            owner_name = Live_chat_parameters["yt_channel_name"]
            owner_chat_now = None

            if Live_chat_parameters["yt_response_owner"] and chat_list:
                if any(owner_name in d for d in chat_list):
                    for d in chat_list:
                        if owner_name in d:
                            owner_chat_now = d
                            break

                    chat_list = [d for d in chat_list if owner_name not in d]

                    name = list(owner_chat_now.keys())[0]
                    chat_now = owner_chat_now[name]
                    Live_Chat_LLM_wait_list.append({"role": "youtube_chat", "content": f"{name} : {chat_now}"})

            else:
                chat_list = [d for d in chat_list if owner_name not in d]


            vip_names = Live_chat_parameters["yt_live_chat_vip_names"]
            vip_chat_now = None

            if Live_chat_parameters["yt_response_vip"] and chat_list:
                for vip_name in vip_names:
                    if any(vip_name in d for d in chat_list):
                        for d in chat_list:
                            if vip_name in d:
                                vip_chat_now = d
                                break

                        chat_list = [d for d in chat_list if vip_name not in d]

                        name = list(vip_chat_now.keys())[0]
                        chat_now = vip_chat_now[name]
                        Live_Chat_LLM_wait_list.append({"role": "youtube_chat", "content": f"{name} : {chat_now}"})


            if chat_list:
                first_occurrences = {}
                for d in chat_list:
                    key = next(iter(d))
                    if key not in first_occurrences:
                        first_occurrences[key] = d

                keys_to_pick = list(first_occurrences.keys())
                random_keys = random.sample(keys_to_pick, min(Live_chat_parameters["yt_chat_max_response"], len(keys_to_pick)))
                selected_comments = [first_occurrences[key] for key in random_keys]

                if Live_chat_parameters["yt_response_individual"]:
                    for chat_content in selected_comments:
                        name = list(chat_content.keys())[0]
                        chat_now = chat_content[name]
                        Live_Chat_LLM_wait_list.append({"role": "youtube_chat", "content": f"{name} : {chat_now}"})

                else:
                    chat_s = "\n".join([f"{key} : {d[key]}" for d in selected_comments for key in d])
                    Live_Chat_LLM_wait_list.append({"role": "youtube_chat", "content": chat_s})

        time.sleep(0.1)





def Twitch_live_chat_connect(live_chat_status, tw_lc_raw_list):
    try:
        tlc = Twitch_live_chat(
            channel=AIVT_Config.Twitch_user_name,
            token=AIVT_Config.Twitch_token,
            tw_lc_raw_list=tw_lc_raw_list
            )
        tlc.run()

        while live_chat_status['Twitch_live_chat']:
            time.sleep(0.1)

        tlc.close()

    except Exception as e:
        print(f"!!! Twitch {AIVT_Config.Twitch_user_name} Disconnected !!!\n\n{e}\n\n")
        live_chat_status['Twitch_live_chat'] = False

class Twitch_live_chat(twitch_commands.Bot):
    def __init__(self, channel, token, tw_lc_raw_list):
        super().__init__(token=token, prefix='!', initial_channels=[channel])
        self.tw_lc_raw_list = tw_lc_raw_list

    async def event_ready(self):
        print(f"!!! Twitch {self.nick} Connected !!!\n")

    async def event_message(self, message):
        if message.echo:
            return

        formatted_message = f"{message.author.name} : {message.content}"
        self.tw_lc_raw_list.append(formatted_message)

        await self.handle_commands(message)


def Twitch_live_chat_get_comments():
    global Live_Chat_Status, Live_chat_parameters, TW_LC_raw_list, TW_LC_wait_list

    TW_LC_wait_list = []

    while Live_Chat_Status["Twitch_live_chat"]:
        time.sleep(0.1)

        try:
            if TW_LC_raw_list:
                chat_list = []

                TW_LC_raw_list_l = len(TW_LC_raw_list)
                while TW_LC_raw_list_l > 0:
                    TW_LC_raw_list_l -= 1

                    chat_author, chat_raw = TW_LC_raw_list.pop(0).split(" : ", 1)

                    if chat_author in Live_chat_parameters["tw_live_chat_ban_names"]:
                        continue

                    elif (chat_author == Live_chat_parameters["tw_channel_name"] and Live_chat_parameters["tw_response_owner"]) or chat_author in Live_chat_parameters["tw_live_chat_vip_names"]:
                        chat_now = {chat_author: chat_raw}
                        chat_list.append(chat_now)

                    elif tokenC.num_tokens_from_conversation([{"role": "user", "content": chat_raw}], "gpt-3.5-turbo")-9 < Live_chat_parameters["tw_chat_max_tokens"]:
                        chat_now = {chat_author: chat_raw}
                        chat_list.append(chat_now)

                    else:
                        if Live_chat_parameters["tw_live_chat_log"]:
                            print(f"!!! *{chat_author}* comment beyond max tokens - Twitch Live Chat !!!")
                    
                if chat_list:
                    TW_LC_wait_list.extend(chat_list)
                    if Live_chat_parameters["tw_live_chat_log"]:
                        chat_c = "\n\n".join([f"{key} : {d[key]}" for d in chat_list for key in d])
                        print(f"\nTwitch Live Chat ----------\n\n{chat_c}\n\n----------\n")
        
        except:
            '''
            Never gonna give you up
            Never gonna let you down
            Never gonna run around and desert you
            Never gonna make you cry
            Never gonna say goodbye
            Never gonna tell a lie and hurt you
            '''

def Twitch_live_chat_pick_comments():
    global Live_Chat_Status, Live_chat_parameters, TW_LC_wait_list, Live_Chat_LLM_wait_list

    while Live_Chat_Status["Twitch_live_chat"]:
        if Live_chat_parameters["tw_response_chatroom"] and TW_LC_wait_list:
            c = len(TW_LC_wait_list)
            chat_list = []
            while c > 0:
                c -= 1
                chat_list.append(TW_LC_wait_list.pop(0))

            chat_list.reverse()
            
            owner_name = Live_chat_parameters["tw_channel_name"]
            owner_chat_now = None

            if Live_chat_parameters["tw_response_owner"] and chat_list:
                if any(owner_name in d for d in chat_list):
                    for d in chat_list:
                        if owner_name in d:
                            owner_chat_now = d
                            break
                    
                    chat_list = [d for d in chat_list if owner_name not in d]

                    name = list(owner_chat_now.keys())[0]
                    chat_now = owner_chat_now[name]
                    Live_Chat_LLM_wait_list.append({"role": "twitch_chat", "content": f"{name} : {chat_now}"})

            else:
                chat_list = [d for d in chat_list if owner_name not in d]

            vip_names = Live_chat_parameters["tw_live_chat_vip_names"]
            vip_chat_now = None

            if Live_chat_parameters["tw_response_vip"] and chat_list:
                for vip_name in vip_names:
                    if any(vip_name in d for d in chat_list):
                        for d in chat_list:
                            if vip_name in d:
                                vip_chat_now = d
                                break
                        
                        chat_list = [d for d in chat_list if vip_name not in d]

                        name = list(vip_chat_now.keys())[0]
                        chat_now = vip_chat_now[name]
                        Live_Chat_LLM_wait_list.append({"role": "twitch_chat", "content": f"{name} : {chat_now}"})

            if chat_list:
                first_occurrences = {}
                for d in chat_list:
                    key = next(iter(d))
                    if key not in first_occurrences:
                        first_occurrences[key] = d

                keys_to_pick = list(first_occurrences.keys())
                random_keys = random.sample(keys_to_pick, min(Live_chat_parameters["tw_chat_max_response"], len(keys_to_pick)))
                selected_comments = [first_occurrences[key] for key in random_keys]

                if Live_chat_parameters["tw_response_individual"]:
                    for chat_content in selected_comments:
                        name = list(chat_content.keys())[0]
                        chat_now = chat_content[name]
                        Live_Chat_LLM_wait_list.append({"role": "twitch_chat", "content": f"{name} : {chat_now}"})

                else:
                    chat_s = "\n".join([f"{key} : {d[key]}" for d in selected_comments for key in d])
                    Live_Chat_LLM_wait_list.append({"role": "twitch_chat", "content": chat_s})

        time.sleep(0.1)





def YouTube_LiveChat_boot_on():
    global Live_Chat_Status

    YT_lcgc = threading.Thread(target=YouTube_live_chat_get_comments)
    YT_lcgc.start()

    YT_lcpc = threading.Thread(target=YouTube_live_chat_pick_comments)
    YT_lcpc.start()

    if not Live_Chat_Status["llm_request_checker"]:
        Live_Chat_Status["llm_request_checker"] = True
        LC_llmc = threading.Thread(target=Live_Chat_LLM_checker)
        LC_llmc.start()


def Twitch_LiveChat_boot_on():
    global Live_Chat_Status

    TW_lcgc = threading.Thread(target=Twitch_live_chat_get_comments)
    TW_lcgc.start()

    TW_lcpc = threading.Thread(target=Twitch_live_chat_pick_comments)
    TW_lcpc.start()

    if not Live_Chat_Status["llm_request_checker"]:
        Live_Chat_Status["llm_request_checker"] = True
        LC_llmc = threading.Thread(target=Live_Chat_LLM_checker)
        LC_llmc.start()





def Live_Chat_LLM_checker():
    global Live_Chat_Status, Live_chat_parameters, Live_Chat_LLM_wait_list

    Live_Chat_LLM_wait_list = []

    while Live_Chat_Status["YouTube_live_chat"] or Live_Chat_Status["Twitch_live_chat"]:
        if Live_Chat_LLM_wait_list:
            ans_requst = Live_Chat_LLM_wait_list.pop(0)
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

    Live_Chat_Status["llm_request_checker"] = False










if __name__ == "__main__":
    Live_Chat_Status["YouTube_live_chat"] = True
    Live_chat_parameters["yt_live_id"] = "qTmJ4YkziEk"
    Live_chat_parameters["yt_response_chatroom"] = True
    Live_chat_parameters["yt_response_owner"] = True
    Live_chat_parameters["yt_response_vip"] = True
    YouTube_live_chat_connect()
    YouTube_LiveChat_boot_on()




