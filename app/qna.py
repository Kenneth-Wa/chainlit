import os

from utils.oai import CustomEndpoint


def qna(prompt: str, history: list):
    max_completion_tokens = int(os.environ.get("MAX_COMPLETION_TOKENS"))

    history = []
    
    chat = CustomEndpoint()
    stream = chat.stream(
        messages=history + [{"role": "user", "content": prompt}],
        max_tokens=max_completion_tokens,
    )

    return stream


    while True:
        question = input("\033[92m" + "$User (type q! to quit): " + "\033[0m")
        if question == "q!":
            break

        stream, context = chat_with_p(question, url, history)

        print("\033[92m" + "$Bot: " + "\033[0m", end=" ", flush=True)
        answer = print_stream_and_return_full_answer(stream)
        history = history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]