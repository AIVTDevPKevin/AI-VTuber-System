import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import string
from collections import Counter

import Google.gemini.GoogleAI_Gemini_API as gemini_api
import OpenAI.gpt.OpenAI_GPT_API as gpt_api










gemini_model_names_list = [name for name in gemini_api.gemini_models_max_input_tokens.keys()]
gpt_model_names_list = [name for name in gpt_api.gpt_models_max_input_tokens.keys()]
model_names_list = gemini_model_names_list + gpt_model_names_list





def Sentiment_Analysis_NLP(
        text,
        Emo_state_categories=["normal", "happy", "shy", "proud", "shock", "sad", "angry", "embarrass", "afraid", "confuse"],
        model="gemini-1.0-pro",
        timeout=5,
    ):
    global gemini_model_names_list, gpt_model_names_list

    SA_system_prompt = f"You will be responsible for analysing the text sent to you and sending back the corresponding sentiment categories in English. According to the following categories of sentiment that I have defined: {Emo_state_categories}, just send back the one most likely sentiment, and only return the name of the sentiment. Don't send me back the text that was sent to you."
    conversation = [
            {"role": "system", "content": SA_system_prompt},
            {"role": "user", "content": "(・_・;) No, PK, why did you suddenly say this? Are you trying to steal my little fish? (＠_＠;)＼(◎o◎)／!"},
            {"role": "assistant", "content": "confuse"},
            {"role": "user", "content": "PK、君は悪いよ(／‵Д′)／~ ╧╧ C0はパクチーが一番嫌い(╬ﾟдﾟ) パク​​チーもセロリもこの世に出てはいけない(╯°□°)╯︵ ┻━┻"},
            {"role": "assistant", "content": "angry"},
            {"role": "user", "content": "(゜o゜)  欸欸欸！PK你在幹嘛？學貓叫嗎？ 笑死！這個PK就是遜啦！哈哈！ (≧∇≦)/ "}, # 🥲
            {"role": "assistant", "content": "happy"},
            {"role": "user", "content": text},
        ]


    if model in gemini_model_names_list:
        llm_result = gemini_api.run_with_timeout_GoogleAI_Gemini_API(
                conversation,
                "",
                model_name=model,
                max_output_tokens=64,
                temperature=0.2,
                timeout=timeout,
                retry=1,
                command="no_print",
            )

    elif model in gpt_model_names_list:
        llm_result = gpt_api.run_with_timeout_OpenAI_GPT_API(
                conversation,
                "",
                model_name=model,
                max_output_tokens=10,
                temperature=0.2,
                timeout=timeout,
                retry=1,
                command="no_print",
            )

    #print(f"Emotion State (LLM): {llm_result}")

    try:
        mcsw = most_common_specific_word(llm_result, Emo_state_categories)
    except Exception as e:
        print(f"\n{e}\n")
        return "normal"
            
    mcsw = most_common_specific_word(llm_result, Emo_state_categories)
    #print(f"Emotion State (MCSW): {mcsw}\n")
    print(f"Emotion State: {mcsw}")
    return mcsw



def most_common_specific_word(text, Emo_state_categories):
    punctuation = string.punctuation + "："
    translator = str.maketrans(punctuation, " " * len(punctuation))

    text = text.lower()
    text = text.translate(translator)
    words = text.split()
    word_counts = Counter(words)

    Emo_state_categories = [word.lower() for word in Emo_state_categories]
    result = {word: word_counts[word] for word in Emo_state_categories}
    most_common_word = max(result, key=result.get)
    return most_common_word










if __name__ == "__main__":

    emo_state = Sentiment_Analysis_NLP(
            "Never gonna make you cry never gonna say goodbye"
        )




