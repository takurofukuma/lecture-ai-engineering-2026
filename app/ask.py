"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保ちながら続けて質問する

通常モードはツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def print_usage(response) -> None:
    """API が返した入力・出力トークン数を、取得できた場合だけ表示する。"""
    usage = response.usage_metadata
    if usage is None:
        return
    prompt = usage.prompt_token_count
    output = usage.candidates_token_count
    print(f"[tokens] 入力: {prompt if prompt is not None else '不明'} / "
          f"出力: {output if output is not None else '不明'}")


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)
    print_usage(response)
    return response.text


def chat(initial_question: str | None = None) -> None:
    """同じチャットセッションで質問を送り、SDK に会話履歴を保持させる。"""
    client = genai.Client(api_key=get_api_key())
    session = client.chats.create(model=MODEL)
    print(f"[model] {MODEL}")
    print("続けて質問できます。終了するには /exit を入力してください。")

    question = initial_question
    while True:
        if question is None:
            try:
                question = input("質問> ").strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break
        if question == "/exit":
            break
        if not question:
            question = None
            continue
        try:
            response = session.send_message(question)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            question = None
            continue
        print(f"\n{response.text or '(回答テキストなし)'}")
        print_usage(response)
        question = None


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って続けて質問する")
    args = parser.parse_args()

    if args.chat:
        chat(args.question)
        return

    question = args.question or DEFAULT_QUESTION
    print(f"[model] {MODEL}")
    print(f"[質問] {question}\n")
    try:
        print(ask(question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
