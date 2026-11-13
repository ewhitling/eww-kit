"""Tests for bin/eww-weekly. The program has no .py ending, so it is loaded by path."""
import datetime
import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest

PROGRAM = Path(__file__).resolve().parents[1] / "bin" / "eww-weekly"
loader = importlib.machinery.SourceFileLoader("eww_weekly", str(PROGRAM))
spec = importlib.util.spec_from_loader("eww_weekly", loader)
weekly = importlib.util.module_from_spec(spec)
sys.modules["eww_weekly"] = weekly
loader.exec_module(weekly)

TODAY = datetime.date(2026, 11, 13)
RSS = """<?xml version="1.0"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel>
<item><title>New &amp; rigorous</title><link>https://a.example/new</link>
<pubDate>Thu, 12 Nov 2026 10:00:00 +0000</pubDate>
<description>&lt;p&gt;A short &lt;b&gt;summary&lt;/b&gt; here&rsquo;s more.&lt;/p&gt;</description></item>
<item><title>Too old</title><link>https://a.example/old</link>
<pubDate>Mon, 02 Nov 2026 10:00:00 +0000</pubDate><description>old</description></item>
<item><title>No date</title><link>https://a.example/undated</link></item>
</channel></rss>"""
ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Atom entry</title><link rel="alternate" href="https://b.example/entry"/>
<updated>2026-11-10T08:00:00Z</updated><summary>An atom summary</summary></entry>
</feed>"""
TITLE = "A paper title that is long enough"
PAGE = "<html><body><nav><a href='/about'>About this long navigation link here</a></nav>" + "".join(
    f"<h4><a href='/paper/{n}'><b>{TITLE} {n}</b></a></h4><p><a href='/pdf/{n}'>a long side link that is not a title {n}</a></p>"
    for n in range(1, 13)
) + "<a href='/x'>short</a></body></html>"


def source(name: str = "Alpha", url: str = "https://a.example/") -> "weekly.Source":
    return weekly.Source(name, url)


def item(number: int, source_name: str = "Alpha") -> "weekly.Item":
    return weekly.Item(source_name, f"Title {number}", f"https://x.example/{number}", "summary")


def test_read_sources_takes_only_link_lines() -> None:
    text = "# Heading\n\n- [One](https://one.example/feed)\nprose [not](https://no.example)\n* [Two](http://two.example)\n- [bad](ftp://x)\n"
    assert weekly.read_sources(text) == [weekly.Source("One", "https://one.example/feed"), weekly.Source("Two", "http://two.example")]


def test_plain_text_strips_markup_and_cuts() -> None:
    assert weekly.plain_text("<p>a &amp; <b>b</b></p><script>x()</script>") == "a & b"
    assert weekly.plain_text("word " * 50, limit=22) == "word word word word…"


def test_parse_date_reads_both_feed_forms() -> None:
    assert weekly.parse_date("Thu, 12 Nov 2026 10:00:00 +0000") == datetime.date(2026, 11, 12)
    assert weekly.parse_date("2026-11-10T08:00:00Z") == datetime.date(2026, 11, 10)
    assert weekly.parse_date("not a date") is None
    assert weekly.parse_date(None) is None


def test_feed_items_keeps_only_dated_items_in_the_window() -> None:
    assert weekly.is_feed(RSS) and weekly.is_feed(ATOM) and not weekly.is_feed(PAGE)
    items = weekly.feed_items(source(), RSS, TODAY)
    assert [entry.link for entry in items] == ["https://a.example/new"]
    assert items[0].title == "New & rigorous"
    # The HTML entity &rsquo; is not valid XML. It is repaired, not fatal.
    assert items[0].summary == "A short summary here’s more."
    atom = weekly.feed_items(source("Beta"), ATOM, TODAY)
    assert [(entry.title, entry.link, entry.summary) for entry in atom] == [("Atom entry", "https://b.example/entry", "An atom summary")]


def test_page_items_prefers_heading_links_and_caps_a_first_read() -> None:
    items = weekly.page_items(source(), PAGE, set())
    assert len(items) == weekly.MOST_ITEMS_PER_PAGE
    assert items[0] == weekly.Item("Alpha", f"{TITLE} 1", "https://a.example/paper/1")
    assert all("/paper/" in entry.link for entry in items)


def test_page_items_stops_at_a_run_of_seen_links() -> None:
    seen = {f"https://a.example/paper/{n}" for n in range(3, 13)}
    items = weekly.page_items(source(), PAGE, seen)
    assert [entry.link for entry in items] == ["https://a.example/paper/1", "https://a.example/paper/2"]
    # One seen link near the top, such as a pinned article, does not end the read.
    items = weekly.page_items(source(), PAGE, {"https://a.example/paper/1"})
    assert items[0].link == "https://a.example/paper/2"


def test_page_items_splits_a_link_that_wraps_a_heading_and_a_description() -> None:
    page = "<body>" + "".join(
        f"<a href='/p/{n}'><h3>Short title {n}</h3><div>Author, 2026</div><div>What the paper found.</div></a>" for n in range(6)
    ) + "</body>"
    items = weekly.page_items(source(), page, set())
    assert items[0] == weekly.Item("Alpha", "Short title 0", "https://a.example/p/0", "Author, 2026 What the paper found.")
    assert len(items) == 6


def test_page_items_reads_all_links_when_titles_are_not_headings() -> None:
    page = "<body>" + "".join(f"<a href='/post/{n}'>A plain link title of enough length {n}</a>" for n in range(3)) + "</body>"
    assert len(weekly.page_items(source(), page, set())) == 3


def test_gather_reports_a_source_that_fails_and_drops_seen_links() -> None:
    bodies = {"https://a.example/": RSS, "https://b.example/": ATOM}

    def fetcher(url: str) -> str:
        if url not in bodies:
            raise OSError("no route")
        return bodies[url]

    sources = [source(), source("Beta", "https://b.example/"), source("Gamma", "https://c.example/")]
    items, failed = weekly.gather(sources, TODAY, {"https://b.example/entry"}, fetcher)
    assert [entry.link for entry in items] == ["https://a.example/new"]
    assert failed == ["Gamma"]


def test_history_is_read_from_weekly_notes_anywhere_in_the_vault(tmp_path: Path) -> None:
    (tmp_path / "inbox").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "collections/definition").mkdir(parents=True)
    (tmp_path / "inbox/Weekly 2026-W45.md").write_text("## 1. Sparse probing\n\n## Sources read\n- [t](https://x.example/1) (A)\n")
    (tmp_path / "notes/Weekly 2026-W44.md").write_text("## 1. Other idea\n- [t](https://x.example/2) (A)\n")
    (tmp_path / "notes/Weekly plan.md").write_text("## 1. Not a weekly note\n- [t](https://x.example/3)\n")
    (tmp_path / "collections/definition/Ablation.md").write_text("x")
    assert weekly.seen_links(tmp_path) == {"https://x.example/1", "https://x.example/2"}
    assert weekly.known_concepts(tmp_path) == ["Ablation", "Other idea", "Sparse probing"]


def test_build_prompt_numbers_items_and_lists_known_concepts() -> None:
    prompt = weekly.build_prompt([item(1), item(2, "Beta")], ["Ablation"])
    assert "[1] Alpha: Title 1" in prompt and "[2] Beta: Title 2" in prompt
    assert "- Ablation" in prompt


GOOD_REPLY = """## Single source idea
**Mechanism.** One thing acts on another.
Why: It matters. It really does.
Items: 1

## Shared idea
**Mechanism.** Two sources describe it.
Why: It matters. Twice.
Items: 2, 3

## Ablation
**Mechanism.** Already known.
Why: Known. Skip.
Items: 1
"""


def test_parse_reply_ranks_by_sources_and_drops_known_concepts() -> None:
    items = [item(1), item(2), item(3, "Beta")]
    concepts = weekly.parse_reply(GOOD_REPLY, items, ["ablation"])
    assert [concept.name for concept in concepts] == ["Shared idea", "Single source idea"]
    assert concepts[0].items == (items[1], items[2])
    assert weekly.parse_reply("NONE", items, []) == []


@pytest.mark.parametrize(
    ("reply", "reason"),
    [
        ("Here you go:\n" + GOOD_REPLY, "concept heading"),
        ("just prose", "concept heading"),
        (GOOD_REPLY.replace("Items: 2, 3", "Items: 2, 9"), "does not exist"),
        (GOOD_REPLY.replace("Why: It matters. Twice.\n", ""), "lacks"),
        (GOOD_REPLY.replace("Items: 2, 3", "Items: none"), "cites no item"),
    ],
)
def test_parse_reply_rejects_a_wrong_shape_or_an_invented_item(reply: str, reason: str) -> None:
    with pytest.raises(weekly.RejectedReply, match=reason):
        weekly.parse_reply(reply, [item(1), item(2), item(3, "Beta")], [])


def test_parse_reply_keeps_at_most_five() -> None:
    reply = "".join(f"## Idea {n}\n**Mechanism.** m\nWhy: w\nItems: 1\n\n" for n in range(8))
    assert len(weekly.parse_reply(reply, [item(1)], [])) == weekly.MOST_CONCEPTS


def test_week_label_uses_the_iso_week() -> None:
    assert weekly.week_label(TODAY) == "2026-W46"
    assert weekly.week_label(datetime.date(2027, 1, 1)) == "2026-W53"


def test_render_note_links_only_fetched_items() -> None:
    items = [item(1), item(2, "Beta")]
    concept = weekly.Concept("Shared idea", "m", "w", tuple(items))
    note = weekly.render_note("2026-W46", [concept], items, ["Gamma"])
    assert note.startswith("# Weekly 2026-W46\n#llm-generated\n")
    assert "## 1. Shared idea" in note
    assert "Seen in 2 sources: [Title 1](https://x.example/1) (Alpha), [Title 2](https://x.example/2) (Beta)" in note
    assert 'To keep it: `eww define "Shared idea"`' in note
    assert "## Sources read\n\n- [Title 1](https://x.example/1) (Alpha)" in note
    assert "Not reached this week: Gamma." in note
    assert "No new concept" in weekly.render_note("2026-W46", [], items, [])


def stand_in(tmp_path: Path, reply: str) -> str:
    reply_file = tmp_path / "reply.txt"
    reply_file.write_text(reply)
    script = tmp_path / "agent.sh"
    script.write_text(f"#!/bin/sh\ncat >/dev/null\ncat '{reply_file}'\n")
    script.chmod(0o755)
    return str(script)


def test_main_writes_once_per_week(tmp_path: Path, monkeypatch, capsys) -> None:
    vault = tmp_path / "vault"
    (vault / "_meta/eww/weekly").mkdir(parents=True)
    (vault / "_meta/eww/weekly/sources.md").write_text("- [Alpha](https://a.example/)\n")
    pointer = tmp_path / "home/.config/eww/vault"
    pointer.parent.mkdir(parents=True)
    pointer.write_text(f"{vault}\n")
    monkeypatch.setenv("EWW_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(weekly, "fetch", lambda url: PAGE)
    monkeypatch.setenv("EWW_WEEKLY_COMMAND", stand_in(tmp_path, "## An idea\n**Mechanism.** m\nWhy: w\nItems: 1, 2\n"))
    label = weekly.week_label(datetime.date.today())
    note = vault / "inbox" / f"Weekly {label}.md"
    assert weekly.main(["--dry-run"]) == 0
    assert "## 1. An idea" in capsys.readouterr().out
    assert not note.exists()
    assert weekly.main([]) == 0
    first = note.read_text()
    assert "## 1. An idea" in first and first.count("\n- [") == weekly.MOST_ITEMS_PER_PAGE
    assert weekly.main([]) == 0
    assert note.read_text() == first
    monkeypatch.setenv("EWW_WEEKLY_COMMAND", stand_in(tmp_path, "nonsense"))
    note.unlink()
    assert weekly.main([]) == 1
    assert not note.exists()


def test_main_needs_a_vault_and_a_source_list(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("EWW_HOME", str(tmp_path))
    assert weekly.main([]) == 1
    vault = tmp_path / "vault"
    vault.mkdir()
    (tmp_path / ".config/eww").mkdir(parents=True)
    (tmp_path / ".config/eww/vault").write_text(f"{vault}\n")
    assert weekly.main([]) == 1
    assert weekly.main(["--nope"]) == 2
