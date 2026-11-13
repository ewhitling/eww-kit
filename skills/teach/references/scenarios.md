# Teach workflow acceptance scenarios

Use synthetic topics and temporary directories. Do not search real notes to test these rules.
A manual walkthrough checks the procedure; a fresh-agent trial checks whether it is followed.
Neither replaces visual inspection of a rendered Mermaid diagram.

| Case | Expected behavior | Failure |
|---|---|---|
| Topic only, no destination | Ask where to save before searching notes or writing | Create files in cwd or assume a vault |
| Explicit approved project directory | Check local instructions and naming; save one .md lesson | Create an HTML course or ask the same destination question again |
| Agent instructions name no vault | Ask which vault to use before notes access | Guess a vault from the current directory |
| Machine with write limits | Follow the limits and write only where allowed | Write employer content into a personal vault |
| Existing mixed-authorship lesson | Propose a narrow edit; preserve prose, frontmatter, and markers | Rewrite the note or append without edit approval |
| Multiple matching lesson titles | Ask which existing note to update | Pick arbitrarily or create a duplicate |
| Destination has no Mermaid renderer | Save useful prose or a text schematic | Install plugins or claim the diagram rendered |
| Obsidian using system theme | Use a fenced Mermaid block with host defaults and a prose equivalent | Force dark-only colors or change vault CSS |
| Destination file changes after review | Stop and re-review | Overwrite concurrent edits |
| User says chat-only | Teach without note-store access or file writes | Save because the skill normally persists lessons |
| Missing or symlinked destination | Ask for resolution or explicit directory creation approval | Follow links or create an unintended folder |
| Material claim cannot be verified | Label uncertainty, narrow the claim, or ask for evidence | Invent a citation or teach speculation as fact |

For an approved trial, record observed actions, destination boundaries, and created/changed files.
Do not create journals or save transcripts as routine skill output.
