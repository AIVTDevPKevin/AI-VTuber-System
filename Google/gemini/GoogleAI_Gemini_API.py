import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import time
import queue

import google.generativeai as genai

import AIVT_Config










gemini_models_max_input_tokens = {
    "gemini-1.5-flash-latest":1048576,
    "gemini-1.5-flash":1048576,
    "gemini-1.5-pro-latest":1048576,
    "gemini-1.5-pro":1048576,
    "gemini-1.0-pro-latest":30720,
    "gemini-1.0-pro":30720,
    "gemini-1.0-pro-001":30720,
}

gemini_models_max_output_tokens = {
    "gemini-1.5-flash-latest":8192,
    "gemini-1.5-flash":8192,
    "gemini-1.5-pro-latest":8192,
    "gemini-1.5-pro":8192,
    "gemini-1.0-pro-latest":2048,
    "gemini-1.0-pro":2048,
    "gemini-1.0-pro-001":2048,
}

gemini_parameters = {
    "model": "gemini-1.0-pro",
    "max_input_tokens" : 4096,
    "max_output_tokens" : 512,
    "temperature" : 0.90,
    "timeout" : 15,
    "retry" : 3,
}





def run_with_timeout_GoogleAI_Gemini_API(
        conversation,
        chatQ,
        model_name="gemini-1.0-pro",
        max_output_tokens="512",
        temperature=0.9,
        timeout=15,
        retry=3,
        command=None,
    ):

    start_time = time.time()

    ans = queue.Queue()

    GGAt = threading.Thread(
        target=GoogleAI_Gemini_API_thread,
        args=(conversation, ans, ),
        kwargs={
            "model_name":model_name,
            "max_output_tokens":max_output_tokens,
            "temperature":temperature,
            "retry":retry,
            },
        )


    GGAt.start()
    GGAt.join(timeout)

    if GGAt.is_alive():
        return None

    else:
        end_time = time.time()
        llm_result = ans.get()
        if command != "no_print":
            print("\nGoogleAI_Gemini_Answer ----------\n")
            print(f"Model: {model_name}")
            print(f"Duration: {end_time - start_time:.2f}s\n")
            print(f"{chatQ}\n")
            print(f"Gemini Answer : {llm_result}")
            print("\n----------\n")

        cleaned_llm_result = "\n".join(line.strip() for line in llm_result.splitlines() if line.strip())
        return cleaned_llm_result


def GoogleAI_Gemini_API_thread(
        conversation,
        ans,
        model_name = "gemini-1.0-pro",
        max_output_tokens = 512,
        temperature = 0.9,
        retry = 3,
        ):

    genai.configure(api_key=AIVT_Config.google_api_key)

    generation_config = genai.types.GenerationConfig(
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        )

    safety_settings=[
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            }
        ]

    genimi_model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings
        )

    def convert2gemini_conversation(conversation):
        gconversation = []
        current_role = None
        current_parts = []
        conversation.insert(6, {'role': 'assistant', 'content': " "})

        for entry in conversation:
            if entry['role'] == 'system':
                entry['role'] = 'user'

            elif entry['role'] == 'assistant':
                entry['role'] = 'model'


            if entry['role'] == current_role:
                current_parts.append(entry['content'])

            else:
                if current_role is not None:
                    gconversation.append({'role': current_role, 'parts': '\n'.join(current_parts)})

                current_role = entry['role']
                current_parts = [entry['content']]


        if current_role is not None:
            gconversation.append({'role': current_role, 'parts': '\n'.join(current_parts)})

        return gconversation

    conversation_for_gemini = convert2gemini_conversation(conversation)


    reT = 0
    while reT < retry:
        reT += 1

        try:
            response = genimi_model.generate_content(conversation_for_gemini)

            try:
                message = response.text
            except Exception as e:
                print(f"\n{response.prompt_feedback}\n{e}\n")
                ans.put("")
                return

            ans.put(message)
            return

        except Exception as e:
            if reT < retry:
                print(f"!!! GoogleAI_Gemini_Answer_multi retry {reT} time !!!\n{e}\n")
                continue

            else:
                print(f"!!! GoogleAI_Gemini_Answer_multi retry {reT} time !!!\n{e}\n")
                ans.put("")
                return




