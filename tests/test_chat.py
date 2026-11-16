"""Tests for bin/eww-chat. The program has no .py ending, so it is loaded by path."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

PROGRAM = Path(__file__).resolve().parents[1] / "bin" / "eww-chat"
loader = importlib.machinery.SourceFileLoader("eww_chat", str(PROGRAM))
spec = importlib.util.spec_from_loader("eww_chat", loader)
chat = importlib.util.module_from_spec(spec)
sys.modules["eww_chat"] = chat
loader.exec_module(chat)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def stand_in(tmp_path: Path, exit_code: int = 0) -> str:
    """A fake agent: a script that saves each argument on its own line block. Returns its command line."""
    script = tmp_path / "agent.sh"
    script.write_text(
        f"#!/bin/sh\nprintf '%s\\n---\\n' \"$@\" >'{tmp_path / 'arguments.txt'}'\nexit {exit_code}\n"
    )
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def vault(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "vault"
    write(root / "collections/definition/Ablation.md", "# Ablation\n#llm-generated\n\nRemove one part and measure.\n")
    write(root / "collections/lesson/ablation.md", "# Ablation\n\n## Why it matters\nThe lesson text.\n")
    write(root / "collections/lesson/Backpropagation.md", "# Backpropagation\n\nThe chain rule, applied.\n")
    write(root / "collections/definition/Causal inference.md", "# Causal inference\n\nFrom data to causes.\n")
    write(root / "collections/definition/Causal graph.md", "# Causal graph\n\nNodes and arrows.\n")
    write(root / "collections/book/Not a topic.md", "# Not a topic\n")
    write(tmp_path / "home/.config/eww/vault", f"{root}\n{tmp_path / 'second'}\n")
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("EWW_CHAT_COMMAND", stand_in(tmp_path))
    return root


def interactive(monkeypatch, answer: str | None) -> None:
    """Pretend the terminal is interactive, with no fzf, and type one answer at the numbered list."""
    monkeypatch.setattr(chat.sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(chat.sys.stderr, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(chat.shutil, "which", lambda name: None)

    def typed(prompt: str = "") -> str:
        if answer is None:
            raise EOFError
        return answer

    monkeypatch.setattr("builtins.input", typed)


def test_vault_path_is_the_first_listed_vault(vault: Path, tmp_path: Path) -> None:
    assert chat.vault_path(tmp_path / "home") == vault
    assert chat.vault_path(tmp_path / "nowhere") is None


def test_topics_merge_both_folders_and_ignore_case(vault: Path) -> None:
    found = chat.topics(vault)
    assert list(found) == ["Ablation", "Backpropagation", "Causal graph", "Causal inference"]
    assert [note.parent.name for note in found["Ablation"]] == ["definition", "lesson"]
    assert [note.parent.name for note in found["Backpropagation"]] == ["lesson"]
    assert chat.topics(vault / "missing") == {}


def test_matching_prefers_an_exact_title_then_titles_that_contain_the_words() -> None:
    titles = ["Ablation", "Causal graph", "Causal inference", "Graph"]
    assert chat.matching(titles, "  ABLATION ") == ["Ablation"]
    assert chat.matching(titles, "graph") == ["Graph"]
    assert chat.matching(titles, "causal") == ["Causal graph", "Causal inference"]
    assert chat.matching(titles, "inference causal") == ["Causal inference"]
    assert chat.matching(titles, "zzyzx") == []
    assert chat.matching(titles, "") == []


def test_topic_label_names_the_folders(vault: Path) -> None:
    found = chat.topics(vault)
    assert chat.topic_label("Ablation", found["Ablation"]) == "Ablation  (definition, lesson)"


def test_choose_reads_a_number_and_treats_anything_else_as_cancel(monkeypatch, capsys) -> None:
    labels = {"Ablation": "Ablation  (lesson)", "Graph": "Graph  (definition)"}
    interactive(monkeypatch, "2")
    assert chat.choose(labels) == "Graph"
    assert "  2  Graph  (definition)" in capsys.readouterr().err
    for answer in ("q", "0", "3", "", None):
        interactive(monkeypatch, answer)
        assert chat.choose(labels) is None


def test_session_prompt_holds_the_instruction_and_each_note(vault: Path) -> None:
    prompt = chat.session_prompt("Ablation", chat.topics(vault)["Ablation"], vault)
    assert 'The topic is "Ablation".' in prompt
    assert '<note path="collections/definition/Ablation.md">' in prompt
    assert "Remove one part and measure." in prompt
    assert prompt.index("Remove one part") < prompt.index("The lesson text.")
    assert "—" not in chat.INSTRUCTION


def test_session_prompt_cuts_a_very_long_note(vault: Path, monkeypatch) -> None:
    monkeypatch.setattr(chat, "LONGEST_NOTE_CHARACTERS", 20)
    prompt = chat.session_prompt("Ablation", chat.topics(vault)["Ablation"], vault)
    assert "The rest was left out." in prompt
    assert "Remove one part and measure." not in prompt


def test_main_opens_an_exact_topic_with_both_notes(vault: Path, tmp_path: Path) -> None:
    assert chat.main(["ablation"]) == 0
    arguments = (tmp_path / "arguments.txt").read_text()
    assert arguments.startswith("--append-system-prompt\n---\n")
    assert "Remove one part and measure." in arguments and "The lesson text." in arguments
    assert arguments.rstrip().endswith('Start the session on "Ablation".\n---')


def test_main_opens_the_only_topic_that_contains_the_words(vault: Path, tmp_path: Path) -> None:
    assert chat.main(["backprop"]) == 0
    assert "The chain rule, applied." in (tmp_path / "arguments.txt").read_text()


def test_main_returns_the_agent_exit_code(vault: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EWW_CHAT_COMMAND", stand_in(tmp_path, exit_code=3))
    assert chat.main(["ablation"]) == 3
    monkeypatch.setenv("EWW_CHAT_COMMAND", str(tmp_path / "no-such-program"))
    assert chat.main(["ablation"]) == 1


def test_main_without_a_topic_shows_every_topic_in_the_picker(vault: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    interactive(monkeypatch, "2")
    assert chat.main([]) == 0
    listed = capsys.readouterr().err
    assert "  1  Ablation  (definition, lesson)" in listed and "  4  Causal inference  (definition)" in listed
    assert "The chain rule, applied." in (tmp_path / "arguments.txt").read_text()


def test_main_narrows_the_picker_to_topics_that_match(vault: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    interactive(monkeypatch, "1")
    assert chat.main(["causal"]) == 0
    listed = capsys.readouterr().err
    assert '2 topics match "causal"' in listed
    assert "Ablation" not in listed.split("topics match")[1].split("starting")[0]
    assert "Nodes and arrows." in (tmp_path / "arguments.txt").read_text()


def test_main_shows_every_topic_when_none_matches(vault: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    interactive(monkeypatch, "q")
    assert chat.main(["zzyzx"]) == 0
    listed = capsys.readouterr().err
    assert 'no topic matches "zzyzx"' in listed and "  3  Causal graph  (definition)" in listed
    assert not (tmp_path / "arguments.txt").exists()


def test_main_prints_the_list_when_the_terminal_is_not_interactive(vault: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(chat.sys.stdin, "isatty", lambda: False, raising=False)
    assert chat.main([]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "Ablation  (definition, lesson)"
    assert chat.main(["zzyzx"]) == 1
    assert not (tmp_path / "arguments.txt").exists()


def test_main_checks_its_arguments_the_vault_and_the_folders(vault: Path, tmp_path: Path, monkeypatch) -> None:
    assert chat.main(["--nope"]) == 2
    assert chat.main(["--help"]) == 0
    write(tmp_path / "bare/.config/eww/vault", f"{tmp_path / 'bare-vault'}\n")
    (tmp_path / "bare-vault").mkdir()
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "bare"))
    assert chat.main(["ablation"]) == 1
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "empty"))
    assert chat.main(["ablation"]) == 1
