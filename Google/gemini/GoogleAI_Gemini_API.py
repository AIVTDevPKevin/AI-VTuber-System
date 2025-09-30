import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import time
import queue

from google import genai
from google.genai import types

import AIVT_Config










gemini_models_max_input_tokens = {
    #"gemini-2.5-pro":1048576,
    "gemini-2.5-flash":1048576,
    "gemini-2.5-flash-lite":1048576,
    "gemini-2.0-flash":1048576,
    "gemini-2.0-flash-lite":1048576,
    "gemini-1.5-flash-latest":1048576,
    "gemini-1.5-flash":1048576,
    "gemini-1.5-pro-latest":1048576,
    "gemini-1.5-pro":1048576,
    "gemini-1.0-pro-latest":30720,
    "gemini-1.0-pro":30720,
    "gemini-1.0-pro-001":30720,
    "gemini-1.5-flash-002":30720,
    "gemini-1.5-pro-002":30720,
}

gemini_models_max_output_tokens = {
    #"gemini-2.5-pro":65536,
    "gemini-2.5-flash":65536,
    "gemini-2.5-flash-lite":65536,
    "gemini-2.0-flash":8192,
    "gemini-2.0-flash-lite":8192,
    "gemini-1.5-flash-latest":8192,
    "gemini-1.5-flash":8192,
    "gemini-1.5-pro-latest":8192,
    "gemini-1.5-pro":8192,
    "gemini-1.0-pro-latest":2048,
    "gemini-1.0-pro":2048,
    "gemini-1.0-pro-001":2048,
    "gemini-1.5-flash-002":2048,
    "gemini-1.5-pro-002":2048,
}

gemini_parameters = {
    "model": "gemini-2.0-flash",
    "max_input_tokens" : 4096,
    "max_output_tokens" : 512,
    "temperature" : 0.90,
    "timeout" : 15,
    "retry" : 3,
}





def run_with_timeout_GoogleAI_Gemini_API(
        conversation,
        chatQ,
        model_name="gemini-2.0-flash",
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
        model_name = "gemini-2.0-flash",
        max_output_tokens = 512,
        temperature = 0.9,
        retry = 3,
        ):
    def convert2gemini_conversation(conversation):
        system_contents = []
        gemini_conversation = []

        for entry in conversation:
            role = entry['role']
            content = entry['content']

            if role == 'system':
                system_contents.append(content)
                continue

            if role == 'assistant':
                role = 'model'

            gemini_conversation.append(types.Content(role=role, parts=[types.Part(text=content)]))

        system_text = '\n'.join(system_contents) if system_contents else None

        return system_text, gemini_conversation

    system_instruction, conversation_for_gemini = convert2gemini_conversation(conversation)

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

    client = genai.Client(
        api_key=AIVT_Config.google_api_key,
    )

    generation_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        safety_settings=safety_settings,
        thinking_config=types.ThinkingConfig(thinking_budget=0), # Disables thinking
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        # top_p=0.95,
        # top_k=20,
        # candidate_count=1,
    )

    reT = 0
    while reT < retry:
        reT += 1

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=conversation_for_gemini,
                config=generation_config,
            )

            try:
                if response.candidates:
                    message = response.candidates[0].content.parts[0].text
                else:
                    print(f"\nResponse was blocked or empty. Feedback: {response.prompt_feedback}\n")
                    ans.put("")
                    return
            except (IndexError, AttributeError) as e:
                print(f"\nError parsing response structure: {e}\nResponse: {response}\n")
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




