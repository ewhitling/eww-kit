"""Tests for bin/eww-daily. The program has no .py ending, so it is loaded by path."""
import datetime
import importlib.machinery
import importlib.util
import random
import sys
from pathlib import Path

PROGRAM = Path(__file__).resolve().parents[1] / "bin" / "eww-daily"
loader = importlib.machinery.SourceFileLoader("eww_daily", str(PROGRAM))
spec = importlib.util.spec_from_loader("eww_daily", loader)
daily = importlib.util.module_from_spec(spec)
sys.modules["eww_daily"] = daily
loader.exec_module(daily)

LONG = "This sentence is long enough to count as a passage worth showing again."
TODAY = datetime.date(2026, 11, 13)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def make_vault(root: Path) -> Path:
    write(root / "collections/book/Alpha.md", f"---\ntags:\n  - topic/x\n---\n# Alpha\n\n## Highlights\n- {LONG} one\n- {LONG} two\n")
    write(root / "collections/quote/Beta.md", f"# Beta\n\n> {LONG}\n")
    write(root / "collections/definition/Gamma.md", f"# Gamma\n\n{LONG}\n")
    write(root / "collections/article/Delta.md", f"# Delta\n\n{LONG}\n")
    write(root / "collections/ttrpg/Campaign.md", f"# Campaign\n\n{LONG}\n")
    write(root / "collections/book/Hidden.md", f"# Hidden\n#no-resurface\n\n{LONG}\n")
    write(root / "collections/book/Machine.md", f"# Machine\n#llm-generated\n\n{LONG}\n")
    write(root / "collections/book/Empty.md", "# Empty\n\n- short\n")
    return root


def test_shorten_cuts_on_a_word_boundary() -> None:
    assert daily.shorten("a  b\nc") == "a b c"
    cut = daily.shorten("word " * 100, limit=22)
    assert cut == "word word word word…"


def test_highlight_passages_reads_bullets_and_continuation_lines() -> None:
    body = f"## Highlights\n- {LONG} ([Location 5](https://example.com/x))\n  continued here\n    - nested note\n- short\n\n## Notes\n- {LONG} later\n"
    # The indented line joins its bullet, the nested bullet is dropped, and the next section is not read.
    assert daily.highlight_passages(body) == [f"{LONG} ([Location 5](https://example.com/x)) continued here"]


def test_highlight_source_link_at_the_end_is_removed() -> None:
    body = f"## Highlights\n- {LONG} ([Location 5](https://example.com/x))\n"
    assert daily.highlight_passages(body) == [LONG]


def test_quote_passages_joins_consecutive_lines() -> None:
    assert daily.quote_passages(f"> {LONG}\n> and more\n\ntext\n") == [f"{LONG} and more"]


def test_first_paragraph_skips_headings_lists_and_embeds() -> None:
    body = f"# Title\n\n- a list item that is long enough to be a passage, but is a list\n\n![[image.png]] {LONG}\n\n{LONG}\n"
    assert daily.first_paragraph(body) == [LONG]


def test_passages_in_ignores_front_matter() -> None:
    assert daily.passages_in(f"---\nsummary: {LONG}\n---\n# T\n\n{LONG} body\n") == [f"{LONG} body"]


def test_is_excluded_reads_inline_and_front_matter_tags() -> None:
    assert daily.is_excluded("text #no-resurface")
    assert daily.is_excluded("---\ntags:\n  - llm-generated\n---\n")
    assert not daily.is_excluded("plain text")


def test_machine_written_definitions_are_shown_unless_marked() -> None:
    assert daily.is_excluded("# T\n#llm-generated\n", "book")
    assert not daily.is_excluded("# T\n#llm-generated\n", "definition")
    assert daily.is_excluded("# T\n#llm-generated #no-resurface\n", "definition")


def test_a_definition_note_offers_its_mechanism_line() -> None:
    note = f"---\ncreated: 2026-11-13\n---\n# Term\n#llm-generated\n\n**Mechanism.** {LONG}\n\nA definition.\n\n## Diagram\n"
    assert daily.passages_in(note) == [f"**Mechanism.** {LONG}"]


def test_display_title_drops_a_clash_ending() -> None:
    assert daily.display_title("Sikhism-2") == "Sikhism"
    assert daily.display_title("A|B [c]") == "A-B (c)"


def test_candidates_skip_excluded_kinds_tags_and_empty_notes(tmp_path: Path) -> None:
    found = daily.candidates(make_vault(tmp_path))
    assert set(found) == {"collections/book/Alpha", "collections/quote/Beta", "collections/definition/Gamma", "collections/article/Delta"}
    assert found["collections/book/Alpha"][1] == "book"
    assert len(found["collections/book/Alpha"][2]) == 2


def test_pick_prefers_different_kinds_and_fresh_notes(tmp_path: Path) -> None:
    notes = daily.candidates(make_vault(tmp_path))
    for seed in range(20):
        passages = daily.pick(notes, {"collections/book/Alpha"}, random.Random(seed))
        assert len(passages) == 3
        assert len({passage.kind for passage in passages}) == 3
        assert "collections/book/Alpha" not in {passage.link for passage in passages}


def test_pick_falls_back_to_shown_notes_when_fresh_ones_run_out(tmp_path: Path) -> None:
    notes = daily.candidates(make_vault(tmp_path))
    shown = set(notes) - {"collections/quote/Beta"}
    passages = daily.pick(notes, shown, random.Random(1))
    assert len(passages) == 3
    assert passages[0].link == "collections/quote/Beta"


def test_render_and_append_keep_existing_text_and_run_once(tmp_path: Path) -> None:
    note = write(tmp_path / "journal/2026/2026-11-13.md", "my own line")
    section = daily.render_section([daily.Passage("collections/book/Alpha", "Alpha", "book", "an excerpt")])
    assert daily.append_section(note, section) is True
    assert note.read_text() == "my own line\n\n## Resurfaced\n\n- [[collections/book/Alpha|Alpha]] (book)\n  > an excerpt\n"
    assert daily.append_section(note, section) is False
    assert note.read_text().count("## Resurfaced") == 1


def test_day_note_path_follows_the_obsidian_setting(tmp_path: Path) -> None:
    assert daily.day_note_path(tmp_path, TODAY) == tmp_path / "2026-11-13.md"
    setting = write(tmp_path / ".obsidian/daily-notes.json", '{"folder": "/", "format": "YYYY-MM-DD"}')
    assert daily.day_note_path(tmp_path, TODAY) == tmp_path / "2026-11-13.md"
    setting.write_text('{"folder": "journal", "format": "YYYY/YYYY-MM-DD"}')
    assert daily.day_note_path(tmp_path, TODAY) == tmp_path / "journal/2026/2026-11-13.md"


def test_format_date_rejects_parts_it_does_not_know() -> None:
    assert daily.format_date("YYYY.MM.DD", TODAY) == "2026.11.13"
    try:
        daily.format_date("dddd, MMMM Do", TODAY)
    except ValueError as error:
        assert "YYYY, MM, and DD" in str(error)
    else:
        raise AssertionError("an unsupported format was accepted")


def test_append_creates_a_missing_day_note(tmp_path: Path) -> None:
    note = write(tmp_path / ".obsidian/daily-notes.json", '{"folder": "journal", "format": "YYYY/YYYY-MM-DD"}') and daily.day_note_path(tmp_path, TODAY)
    assert note == tmp_path / "journal/2026/2026-11-13.md"
    assert daily.append_section(note, "## Resurfaced\n") is True
    assert note.read_text() == "## Resurfaced\n"


def test_recently_shown_reads_only_recent_resurfaced_sections(tmp_path: Path) -> None:
    write(tmp_path / "journal/2026/2026-11-10.md", "## Resurfaced\n\n- [[collections/book/Alpha|Alpha]] (book)\n\n## Other\n- [[collections/quote/Beta]]\n")
    write(tmp_path / "journal/2026/2026-08-01.md", "## Resurfaced\n\n- [[collections/article/Delta|Delta]] (article)\n")
    write(tmp_path / "journal/2026/notes.md", "## Resurfaced\n\n- [[collections/definition/Gamma]]\n")
    write(tmp_path / "2026-11-12.md", "## Resurfaced\n\n- [[collections/quote/Beta|Beta]] (quote)\n")
    write(tmp_path / "_meta/archive/2026-11-11.md", "## Resurfaced\n\n- [[collections/definition/Gamma]]\n")
    # A day-note counts wherever it sits: at the root or filed in a folder. _meta is not read.
    assert daily.recently_shown(tmp_path, TODAY) == {"collections/book/Alpha", "collections/quote/Beta"}


def test_main_writes_once_and_dry_run_writes_nothing(tmp_path: Path, monkeypatch, capsys) -> None:
    vault = make_vault(tmp_path / "vault")
    write(tmp_path / "home/.config/eww/vault", f"{vault}\n")
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "home"))
    note = daily.day_note_path(vault, datetime.date.today())
    assert daily.main(["--dry-run"]) == 0
    assert "## Resurfaced" in capsys.readouterr().out
    assert not note.exists()
    assert daily.main([]) == 0
    first = note.read_text()
    assert first.count("\n- [[") == 3
    assert daily.main([]) == 0
    assert note.read_text() == first
    assert daily.main(["--nope"]) == 2


def test_main_needs_a_vault(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EWW_HOME", str(tmp_path))
    assert daily.main([]) == 1
