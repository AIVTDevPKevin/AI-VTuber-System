import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import threading
import queue

import openai

import AIVT_Config










gpt_models_max_input_tokens = {
    "gpt-3.5-turbo":16385,
    "gpt-3.5-turbo-0125":16385,
    "gpt-3.5-turbo-1106":16385,
    "gpt-4-turbo":128000,
    "gpt-4-turbo-2024-04-09":128000,
    "gpt-4-turbo-preview":128000,
    "gpt-4-0125-preview":128000,
    "gpt-4-1106-preview":128000,
}

gpt_models_max_output_tokens = {
    "gpt-3.5-turbo":4096,
    "gpt-3.5-turbo-0125":4096,
    "gpt-3.5-turbo-1106":4096,
    "gpt-4-turbo":4096,
    "gpt-4-turbo-2024-04-09":4096,
    "gpt-4-turbo-preview":4096,
    "gpt-4-0125-preview":4096,
    "gpt-4-1106-preview":4096,
}

gpt_parameters = {
    "model": "gpt-3.5-turbo",
    "max_input_tokens" : 4096,
    "max_output_tokens" : 256,
    "temperature" : 1.00,
    "timeout" : 15,
    "retry" : 3,
}





def run_with_timeout_OpenAI_GPT_API(
        conversation,
        chatQ,
        model_name="gpt-3.5-turbo",
        max_output_tokens="256",
        temperature=1.00,
        timeout=15,
        retry=3,
        command=None,
        ):

    ans = queue.Queue()
    model = queue.Queue()
    prompt_tokens = queue.Queue()
    completion_tokens = queue.Queue()
    total_tokens = queue.Queue()

    OGAt = threading.Thread(
        target=OpenAI_GPT_API_thread,
        args=(
            conversation,
            ans,
            model,
            prompt_tokens,
            completion_tokens,
            total_tokens,
            ),
        kwargs={
            "model_name":model_name,
            "max_output_tokens":max_output_tokens,
            "temperature":temperature,
            "retry":retry,
            },
        )

    OGAt.start()
    OGAt.join(timeout)

    if OGAt.is_alive():
        return None

    else:
        llm_result = ans.get()
        if command != "no_print":
            print("\nOpenAI_GPT_Answer ----------\n")
            print(f"model: {model.get()}")
            print(f"prompt_tokens: {prompt_tokens.get()}")
            print(f"completion_tokens: {completion_tokens.get()}")
            print(f"total_tokens: {total_tokens.get()}\n")
            print(f"{chatQ}\n")
            print(f"GPT Answer: {llm_result}\n")
            print("----------\n")

        cleaned_llm_result = "\n".join(line.strip() for line in llm_result.splitlines() if line.strip())
        return cleaned_llm_result


def OpenAI_GPT_API_thread(
        conversation,
        ans,
        model,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        model_name = "gpt-3.5-turbo",
        max_output_tokens = 256,
        temperature = 1.00,
        retry = 3,
        ):

    openai.api_key = AIVT_Config.openai_api_key

    reT = 0
    while reT < retry:
        reT += 1

        try:
            response = openai.chat.completions.create(
                model = model_name,
                messages = conversation,
                max_tokens = max_output_tokens,
                temperature = temperature,
                stream=False,
                )

            model.put(response.model)
            prompt_tokens.put(response.usage.prompt_tokens)
            completion_tokens.put(response.usage.completion_tokens)
            total_tokens.put(response.usage.total_tokens)
            message = response.choices[0].message.content

            ans.put(message)
            return

        except Exception as e:
            if reT < retry:
                print(f"!!! OpenAI_GPT_Answer_multi retry {reT} time !!!\n{e}\n")
                continue

            else:
                print(f"!!! OpenAI_GPT_Answer_multi retry {reT} time !!!\n{e}\n")
                ans.put("")
                return




