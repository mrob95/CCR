from dragonfly import (
    get_engine,
    Dictation,
    IntegerRef,
    MimicFailure,
    AppContext,
    Choice,
    Repeat,
)
from .testutils import TText

import pytest
from breathe import Breathe, CommandContext
from breathe.errors import CommandSkippedWarning
import warnings

engine = get_engine("text")


def test_global_extras():
    Breathe.add_global_extras(Dictation("text"))
    assert len(Breathe.global_extras) == 1
    assert "text" in Breathe.global_extras
    Breathe.add_global_extras([Choice("abc", {"def": "ghi"})])


def test_core_commands():
    Breathe.add_commands(
        None,
        {
            "test one": TText("1"),
            "test two": TText("2"),
            "test three": TText("3"),
            "banana [<n>]": TText("banana") * Repeat("n"),
        },
        [IntegerRef("n", 1, 10, 1)],
    )
    engine.mimic(["test", "three", "test", "two", "banana", "five"])


def test_context_commands():
    Breathe.add_commands(
        AppContext("notepad"),
        {"test [<num>]": lambda num: TText(num).execute()},
        [Choice("num", {"four": "4", "five": "5", "six": "6"})],
        {"num": ""},
    )
    with pytest.raises(MimicFailure):
        engine.mimic(["test", "three", "test", "four"])
    engine.mimic(["test", "three", "test", "four"], executable="notepad")


def test_noccr_commands():
    Breathe.add_commands(
        AppContext("firefox"),
        {"dictation <text>": TText("%(text)s"), "testing static": TText("Static")},
        ccr=False,
    )
    engine.mimic(["testing", "static"], executable="firefox")
    with pytest.raises(MimicFailure):
        engine.mimic(["dictation", "TESTING"])
        engine.mimic(["testing", "static", "testing", "static"], executable="firefox")
    engine.mimic(["dictation", "TESTING"], executable="firefox")


def test_grammar_numbers():
    engine.mimic(["test", "three"])
    # Ensure that we are not adding more grammars than necessary
    assert len(engine.grammars) == 4


def test_nomapping_commands():
    Breathe.add_commands(AppContext("code.exe"), {})


def test_invalid():
    with warnings.catch_warnings(record=True) as w:
        Breathe.add_commands(
            AppContext("code.exe"),
            {
                "test that <nonexistent_extra>": TText("%(nonexistent_extra)s"),
                1: TText("test"),
            },
        )
        assert len(w) == 2
        assert issubclass(w[0].category, CommandSkippedWarning)
    assert len(Breathe.contexts) == 1
    assert len(Breathe.context_commands) == 1


def test_clear():
    Breathe.clear()
