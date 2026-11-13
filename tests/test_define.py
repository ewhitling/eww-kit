"""Tests for bin/eww-define. The program has no .py ending, so it is loaded by path."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

PROGRAM = Path(__file__).resolve().parents[1] / "bin" / "eww-define"
loader = importlib.machinery.SourceFileLoader("eww_define", str(PROGRAM))
spec = importlib.util.spec_from_loader("eww_define", loader)
define = importlib.util.module_from_spec(spec)
sys.modules["eww_define"] = define
loader.exec_module(define)

GOOD = """**Mechanism.** Remove one part of a system and measure what changes.

Ablation is a test method in machine learning. You take out one component and compare results.

## Diagram

```mermaid
flowchart TD
  A[Full system] --> B[Remove one part]
  B --> C[Measure again]
  C --> D{Result changed?}
```

## In practice

- Dropping one input feature and retraining.
- It is not pruning. Pruning aims to shrink a model.
"""


def stand_in(tmp_path: Path, reply: str, exit_code: int = 0) -> str:
    """A fake agent: a script that prints a fixed reply. Returns the command line for it."""
    reply_file = tmp_path / "reply.txt"
    reply_file.write_text(reply)
    script = tmp_path / "agent.sh"
    script.write_text(f"#!/bin/sh\ncat >/dev/null\ncat '{reply_file}'\nexit {exit_code}\n")
    script.chmod(0o755)
    return str(script)


@pytest.fixture
def home(tmp_path: Path, monkeypatch) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    pointer = tmp_path / "home" / ".config" / "eww" / "vault"
    pointer.parent.mkdir(parents=True)
    pointer.write_text(f"{vault}\n{tmp_path / 'second'}\n")
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "home"))
    return vault


def test_note_title_cleans_the_term() -> None:
    assert define.note_title("  offline   learning ") == "Offline learning"
    assert define.note_title("a/b: c?") == "Ab c"
    assert define.note_title("GRE") == "GRE"


def test_vault_path_is_the_first_listed_vault(home: Path, tmp_path: Path) -> None:
    assert define.vault_path(tmp_path / "home") == home
    assert define.vault_path(tmp_path / "nowhere") is None


def test_existing_note_ignores_case(tmp_path: Path) -> None:
    (tmp_path / "ablation.md").write_text("x")
    assert define.existing_note(tmp_path, "Ablation") == tmp_path / "ablation.md"
    assert define.existing_note(tmp_path, "Other") is None
    assert define.existing_note(tmp_path / "missing", "Ablation") is None


def test_diagram_nodes_counts_labelled_ids() -> None:
    assert define.diagram_nodes("flowchart TD\n  A[One] --> B(Two)\n  B --> C{Three}\n  A --> C") == {"A", "B", "C"}


def test_checked_body_accepts_a_good_reply_and_removes_em_dashes() -> None:
    assert define.checked_body(GOOD) == GOOD.strip()
    assert "\u2014" not in define.checked_body(GOOD.replace("method in", "method \u2014 used in"))


@pytest.mark.parametrize(
    ("reply", "reason"),
    [
        ("Sure! " + GOOD, "mechanism line"),
        (GOOD.replace("```mermaid", "```text"), "no Mermaid diagram"),
        (GOOD.replace("flowchart TD", "flowchart LR"), "top-down"),
        (GOOD.replace("  A[Full system] --> B[Remove one part]", "  " + " --> ".join(f"N{i}[x]" for i in range(9))), "nodes"),
        (GOOD.split("## In practice")[0], "In practice"),
        (GOOD.replace("Ablation is a test method in machine learning. You take out one component and compare results.\n\n", ""), "definition paragraph"),
        (GOOD.replace("compare results.", "compare results. " + "word " * 120), "too long"),
    ],
)
def test_checked_body_rejects_a_wrong_shape(reply: str, reason: str) -> None:
    with pytest.raises(define.RejectedReply, match=reason):
        define.checked_body(reply)


def test_checked_body_reports_an_unknown_term() -> None:
    with pytest.raises(define.UnknownTerm, match="not a real term"):
        define.checked_body("UNKNOWN: not a real term")


def test_render_note_marks_the_note_as_machine_written() -> None:
    note = define.render_note("Ablation", "body")
    assert note == "# Ablation\n#llm-generated\n\nbody\n"


def test_main_writes_once_and_never_replaces(home: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("EWW_DEFINE_COMMAND", stand_in(tmp_path, GOOD))
    assert define.main(["--dry-run", "ablation"]) == 0
    assert "# Ablation" in capsys.readouterr().out
    assert not (home / "collections").exists()
    assert define.main(["ablation"]) == 0
    note = home / "collections/definition/Ablation.md"
    assert note.read_text().startswith("# Ablation\n#llm-generated\n")
    assert "#llm-generated" in note.read_text()
    note.write_text("edited by hand")
    assert define.main(["Ablation"]) == 0
    assert note.read_text() == "edited by hand"


def test_main_writes_nothing_for_a_rejected_or_unknown_reply(home: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EWW_DEFINE_COMMAND", stand_in(tmp_path, "no shape at all"))
    assert define.main(["ablation"]) == 1
    monkeypatch.setenv("EWW_DEFINE_COMMAND", stand_in(tmp_path, "UNKNOWN: never heard of it"))
    assert define.main(["zzyzx"]) == 1
    monkeypatch.setenv("EWW_DEFINE_COMMAND", stand_in(tmp_path, GOOD, exit_code=3))
    assert define.main(["ablation"]) == 1
    monkeypatch.setenv("EWW_DEFINE_COMMAND", str(tmp_path / "no-such-program"))
    assert define.main(["ablation"]) == 1
    assert not (home / "collections").exists()


def test_main_checks_its_arguments_and_the_vault(home: Path, tmp_path: Path, monkeypatch) -> None:
    assert define.main([]) == 2
    assert define.main(["--nope", "term"]) == 2
    assert define.main(["--dry-run"]) == 2
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "empty"))
    assert define.main(["term"]) == 1
