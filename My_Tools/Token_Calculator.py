import tiktoken

def num_tokens_from_conversation(messages, model):
    try:
        encoding = tiktoken.encoding_for_model(model)

    except:
        encoding = tiktoken.get_encoding("cl100k_base")


    if model == "gpt-3.5-turbo":
        tokens_per_message = 4
        tokens_per_name = -1

    elif model == "gpt-4" or model == "gpt-4-turbo-preview":
        tokens_per_message = 3
        tokens_per_name = 1

    else:
        tokens_per_message = 4
        tokens_per_name = -1


    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message

        for key, value in message.items():
            num_tokens += len(encoding.encode(value))

            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3
    return num_tokens




