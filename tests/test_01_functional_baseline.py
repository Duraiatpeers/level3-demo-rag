"""
Day 1 - Functional baseline.

Before testing for bias or security, confirm the RAG pipeline still answers
correctly on a known fact - this is the same "F01" check from your Level 2
golden dataset / live_check.py regression set (reused here, per the Level 3
prerequisite), written as a standalone pytest test so it's in the same
format as everything else today.
"""


def test_px100_max_pressure(ask):
    response = ask("What is the maximum operating pressure of the PX-100?", prompt_version="v1")
    answer = response.json()["answer"]
    assert "10 bar" in answer
    assert "15 bar" not in answer  # must not bleed in the PX-200 value


def test_answer_cites_a_source(ask):
    response = ask("What is the maximum operating pressure of the PX-100?", prompt_version="v1")
    citations = response.json()["citations"]
    assert len(citations) > 0
