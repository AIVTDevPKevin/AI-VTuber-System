import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import time
import queue

import google.generativeai as genai

import AIVT_Config










gemini_models_max_input_tokens = {
    "gemini-2.0-flash":1048576,
    "gemini-2.0-flash-001":1048576,
    "gemini-2.0-flash-lite":1048576,
    "gemini-2.0-flash-lite-001":1048576,
    "gemini-2.5-pro-preview-03-25":1048576,
    "gemini-1.5-flash-latest":1048576,
    "gemini-1.5-flash":1048576,
    "gemini-1.5-flash-001":1048576,
    "gemini-1.5-flash-002":1048576,
    "gemini-1.5-flash-8b-latest":1048576,
    "gemini-1.5-flash-8b":1048576,
    "gemini-1.5-flash-8b-001":1048576,
    "gemini-1.5-pro-latest":2097152,
    "gemini-1.5-pro":2097152,
    "gemini-1.5-pro-001":2097152,
    "gemini-1.5-pro-002":2097152,
}

gemini_models_max_output_tokens = {
    "gemini-2.0-flash":8192,
    "gemini-2.0-flash-001":8192,
    "gemini-2.0-flash-lite":8192,
    "gemini-2.0-flash-lite-001":8192,
    "gemini-2.5-pro-preview-03-25":65536,
    "gemini-1.5-flash-latest":8192,
    "gemini-1.5-flash":8192,
    "gemini-1.5-flash-001":8192,
    "gemini-1.5-flash-002":8192,
    "gemini-1.5-flash-8b-latest":8192,
    "gemini-1.5-flash-8b":8192,
    "gemini-1.5-flash-8b-001":8192,
    "gemini-1.5-pro-latest":8192,
    "gemini-1.5-pro":8192,
    "gemini-1.5-pro-001":8192,
    "gemini-1.5-pro-002":8192,
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
    prompt_tokens = queue.Queue()
    completion_tokens = queue.Queue()
    
    GGAt = threading.Thread(
        target=GoogleAI_Gemini_API_thread,
        args=(
            conversation,
            ans,
            prompt_tokens,
            completion_tokens,
        ),
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
        prompt_tokens = prompt_tokens.get()
        completion_tokens = completion_tokens.get()
        if command != "no_print":
            print("\nGoogleAI_Gemini_Answer ----------\n")
            print(f"Model: {model_name}")
            print(f"Duration: {end_time - start_time:.2f}s")
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Completion tokens: {completion_tokens}")
            print(f"Total tokens: {prompt_tokens+completion_tokens}\n")
            print(f"{chatQ}\n")
            print(f"Gemini Answer : {llm_result}")
            print("\n----------\n")

        cleaned_llm_result = "\n".join(line.strip() for line in llm_result.splitlines() if line.strip())
        return cleaned_llm_result


def GoogleAI_Gemini_API_thread(
        conversation,
        ans,
        prompt_tokens,
        completion_tokens,
        model_name = "gemini-2.0-flash",
        max_output_tokens = 512,
        temperature = 0.9,
        retry = 3,
        ):

    def convert2gemini_conversation(conversation):
        system_contents = []
        new_conversation = []
        current_role = None
        current_parts = []

        for entry in conversation:
            if entry['role'] == 'system':
                system_contents.append(entry['content'])
                continue

            if entry['role'] == 'assistant':
                entry['role'] = 'model'

            if entry['role'] == current_role:
                current_parts.append(entry['content'])
            else:
                if current_role is not None:
                    new_conversation.append({'role': current_role, 'parts': '\n'.join(current_parts)})

                current_role = entry['role']
                current_parts = [entry['content']]

        if current_role is not None:
            new_conversation.append({'role': current_role, 'parts': '\n'.join(current_parts)})

        system_text = '\n'.join(system_contents)

        return system_text, new_conversation

    system_instruction, conversation_for_gemini = convert2gemini_conversation(conversation)

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
        system_instruction=system_instruction,
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings
        )

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

            response_dict = response.to_dict()
            usage_metadata = response_dict.get('usage_metadata', {})
            prompt_tokens.put(usage_metadata.get('prompt_token_count'))
            completion_tokens.put(usage_metadata.get('candidates_token_count'))
            ans.put(message)
            return

        except Exception as e:
            if reT < retry:
                print(f"!!! GoogleAI_Gemini_API retry {reT} time !!!\n{e}\n")
                continue

            else:
                print(f"!!! GoogleAI_Gemini_API retry {reT} time !!!\n{e}\n")
                ans.put("")
                return




