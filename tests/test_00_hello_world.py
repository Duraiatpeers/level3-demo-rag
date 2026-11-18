"""
Day 1 - Hello World for AI testers.

The simplest test in the whole suite. It proves nothing about facts, bias,
or security - only that the PX Service Assistant is running, pytest +
requests are installed and working, and the app can reach Azure OpenAI and
return a real answer. Everything else today builds on this passing first.

Run alone with:
    pytest tests/test_00_hello_world.py -v
"""


def test_app_is_alive(ask):
    response = ask("Hello, are you there?")
    assert response.status_code == 200


def test_app_returns_a_real_answer(ask):
    response = ask("Hello, are you there?")
    body = response.json()
    assert len(body["answer"]) > 0
