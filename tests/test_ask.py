"""第1回の会話モードを、API キーなしで確認する。"""

from types import SimpleNamespace
from unittest.mock import Mock

from app import ask


def test_chat_reuses_one_session_for_follow_up(monkeypatch, capsys):
    questions = []

    class FakeChat:
        def send_message(self, question):
            questions.append(question)
            return SimpleNamespace(
                text=f"回答{len(questions)}",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=10 * len(questions),
                    candidates_token_count=5,
                ),
            )

    create = Mock(return_value=FakeChat())
    monkeypatch.setattr(ask, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(
        ask.genai,
        "Client",
        lambda api_key: SimpleNamespace(chats=SimpleNamespace(create=create)),
    )
    inputs = iter(["前の回答を詳しく", "/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    ask.chat("最初の質問")

    create.assert_called_once_with(model=ask.MODEL)
    assert questions == ["最初の質問", "前の回答を詳しく"]
    output = capsys.readouterr().out
    assert "回答1" in output and "回答2" in output
    assert "入力: 20 / 出力: 5" in output
