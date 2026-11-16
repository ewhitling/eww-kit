"""Tests for bin/eww-course. The program has no .py ending, so it is loaded by path."""
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

PROGRAM = Path(__file__).resolve().parents[1] / "bin" / "eww-course"
loader = importlib.machinery.SourceFileLoader("eww_course", str(PROGRAM))
spec = importlib.util.spec_from_loader("eww_course", loader)
course = importlib.util.module_from_spec(spec)
sys.modules["eww_course"] = course
loader.exec_module(course)

FILLER = " ".join(["Each plain sentence here adds a few more words to the part."] * 4)
DIAGRAM = "```mermaid\nflowchart TD\n  A[Full system] --> B[Remove one part]\n  B --> C{Result changed?}\n```"


def lesson(**changed: str) -> str:
    """A well-formed reply. Pass a heading's text to replace that part."""
    parts = []
    for heading in course.SECTIONS:
        text = FILLER
        if heading == course.DIAGRAM_SECTION:
            text = f"{FILLER}\n\n{DIAGRAM}"
        if heading == course.QUESTION_SECTION:
            text = f"{FILLER}\n\n**Answer.** The result changes."
        parts.append(f"## {heading}\n\n{changed.get(heading, text)}")
    return "\n\n".join(parts) + "\n"


GOOD = lesson()


def stand_in(tmp_path: Path, reply: str, exit_code: int = 0) -> str:
    """A fake agent: a script that saves the prompt and prints a fixed reply. Returns its command line."""
    reply_file = tmp_path / "reply.txt"
    reply_file.write_text(reply)
    script = tmp_path / "agent.sh"
    script.write_text(f"#!/bin/sh\ncat >'{tmp_path / 'prompt.txt'}'\ncat '{reply_file}'\nexit {exit_code}\n")
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
    assert course.note_title("  offline   learning ") == "Offline learning"
    assert course.note_title("a/b: c?") == "Ab c"


def test_vault_path_is_the_first_listed_vault(home: Path, tmp_path: Path) -> None:
    assert course.vault_path(tmp_path / "home") == home
    assert course.vault_path(tmp_path / "nowhere") is None


def test_existing_note_ignores_case(tmp_path: Path) -> None:
    (tmp_path / "ablation.md").write_text("x")
    assert course.existing_note(tmp_path, "Ablation") == tmp_path / "ablation.md"
    assert course.existing_note(tmp_path, "Other") is None
    assert course.existing_note(tmp_path / "missing", "Ablation") is None


def test_definition_text_drops_the_title_and_tag(tmp_path: Path) -> None:
    folder = tmp_path / "collections" / "definition"
    folder.mkdir(parents=True)
    (folder / "ablation.md").write_text("# Ablation\n#llm-generated\n\n**Mechanism.** Remove one part.\n")
    assert course.definition_text(tmp_path, "Ablation") == "**Mechanism.** Remove one part."
    assert course.definition_text(tmp_path, "Other") is None
    (folder / "Empty.md").write_text("# Empty\n#llm-generated\n")
    assert course.definition_text(tmp_path, "Empty") is None


def test_build_prompt_includes_the_definition_only_when_given() -> None:
    assert "<definition>" not in course.build_prompt("Ablation", None)
    assert course.build_prompt("Ablation", None).rstrip().endswith("Term: Ablation")
    with_definition = course.build_prompt("Ablation", "Remove {one} part.")
    assert "<definition>\nRemove {one} part.\n</definition>" in with_definition


def test_diagram_nodes_counts_labelled_ids() -> None:
    assert course.diagram_nodes("flowchart TD\n  A[One] --> B(Two)\n  B --> C{Three}\n  A --> C") == {"A", "B", "C"}


def test_lesson_sections_returns_headings_in_order() -> None:
    sections = course.lesson_sections(GOOD)
    assert [heading for heading, _ in sections] == list(course.SECTIONS)
    assert sections[0][1] == FILLER


def test_checked_body_accepts_a_good_reply_and_removes_em_dashes() -> None:
    assert course.checked_body(GOOD) == GOOD.strip()
    assert "—" not in course.checked_body(GOOD.replace("plain sentence", "plain — sentence"))


@pytest.mark.parametrize(
    ("reply", "reason"),
    [
        ("Sure! " + GOOD, "does not start"),
        (GOOD.replace("## Variations", "## Other forms"), "headings are wrong"),
        (GOOD.replace(f"## Variations\n\n{FILLER}\n\n", ""), "headings are wrong"),
        (GOOD.replace("```mermaid", "```text"), "exactly one Mermaid diagram"),
        (lesson(**{"The mechanism": f"{FILLER}\n\n{DIAGRAM}\n\n{DIAGRAM}"}), "exactly one Mermaid diagram"),
        (GOOD.replace("flowchart TD", "flowchart LR"), "top-down"),
        (GOOD.replace("  A[Full system] --> B[Remove one part]", "  " + " --> ".join(f"N{i}[x]" for i in range(11))), "nodes"),
        (lesson(**{"Worked example": f"{FILLER}\n\n{DIAGRAM}"}), "code block or a second diagram"),
        (lesson(**{"Variations": "Too few words."}), '"Variations" is too short'),
        (lesson(**{"Variations": "word " * 200}), '"Variations" is too long'),
        (lesson(**{"Try it": FILLER}), "Answer"),
    ],
)
def test_checked_body_rejects_a_wrong_shape(reply: str, reason: str) -> None:
    with pytest.raises(course.RejectedReply, match=reason):
        course.checked_body(reply)


def test_checked_body_reports_an_unknown_term() -> None:
    with pytest.raises(course.UnknownTerm, match="not a real term"):
        course.checked_body("UNKNOWN: not a real term")


def test_render_note_marks_the_note_and_says_no_sources_were_checked() -> None:
    note = course.render_note("Ablation", "body")
    assert note == f"# Ablation\n#llm-generated\n\n{course.NO_SOURCES_LINE}\n\nbody\n"


def test_main_writes_once_and_never_replaces(home: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("EWW_COURSE_COMMAND", stand_in(tmp_path, GOOD))
    assert course.main(["--dry-run", "ablation"]) == 0
    assert "# Ablation" in capsys.readouterr().out
    assert not (home / "collections").exists()
    assert "<definition>" not in (tmp_path / "prompt.txt").read_text()
    assert course.main(["ablation"]) == 0
    note = home / "collections/lesson/Ablation.md"
    assert note.read_text().startswith("# Ablation\n#llm-generated\n")
    note.write_text("edited by hand")
    assert course.main(["Ablation"]) == 0
    assert note.read_text() == "edited by hand"


def test_main_gives_the_agent_an_existing_definition(home: Path, tmp_path: Path, monkeypatch) -> None:
    definition = home / "collections/definition/ablation.md"
    definition.parent.mkdir(parents=True)
    definition.write_text("# Ablation\n#llm-generated\n\n**Mechanism.** Remove one part and measure.\n")
    monkeypatch.setenv("EWW_COURSE_COMMAND", stand_in(tmp_path, GOOD))
    assert course.main(["ablation"]) == 0
    assert "Remove one part and measure." in (tmp_path / "prompt.txt").read_text()
    assert definition.read_text().endswith("measure.\n")
    assert (home / "collections/lesson/Ablation.md").is_file()


def test_main_writes_nothing_for_a_rejected_or_unknown_reply(home: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EWW_COURSE_COMMAND", stand_in(tmp_path, "no shape at all"))
    assert course.main(["ablation"]) == 1
    monkeypatch.setenv("EWW_COURSE_COMMAND", stand_in(tmp_path, "UNKNOWN: never heard of it"))
    assert course.main(["zzyzx"]) == 1
    monkeypatch.setenv("EWW_COURSE_COMMAND", stand_in(tmp_path, GOOD, exit_code=3))
    assert course.main(["ablation"]) == 1
    monkeypatch.setenv("EWW_COURSE_COMMAND", str(tmp_path / "no-such-program"))
    assert course.main(["ablation"]) == 1
    assert not (home / "collections").exists()


def test_main_checks_its_arguments_and_the_vault(home: Path, tmp_path: Path, monkeypatch) -> None:
    assert course.main([]) == 2
    assert course.main(["--nope", "term"]) == 2
    assert course.main(["--dry-run"]) == 2
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "empty"))
    assert course.main(["term"]) == 1
