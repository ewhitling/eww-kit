# Atom for Obsidian

Vendored on 2026-10-19 for the approved Atom + Hood appearance baseline.

- Author: kognise.
- Upstream: https://github.com/kognise/obsidian-atom
- Pinned commit: `650d6463d377a096520373c4752fef66f3f18f46`.
- License: Unlicense. The upstream `LICENSE` is preserved unchanged.
- Discovery: Obsidian's official `community-css-themes.json` maps Atom to this repository.

`theme.css` is an unchanged copy of the installed theme. Its SHA-256 exactly matches
upstream `obsidian.css` at the pinned commit:

```text
b6f80f8ab20f5069d1272a9b289be0bcac4fdb09ba842c4d509fe80d39659e63
```

`manifest.json` is preserved from the installed theme, not from upstream.
It declares version `0.0.0`, minimum Obsidian version `0.16.0`, and author `kognise`.
Use the pinned commit and `SHA256SUMS` to identify this snapshot, not the manifest version.
The minimum version is metadata, not a tested compatibility guarantee.

## Use and updates

Follow `config/obsidian/README.md` from the repository root.
After separate deployment approval, copy `theme.css` and `manifest.json` into
`<vault>/.obsidian/themes/Atom/`. Preserve this license and attribution with redistributed copies.
Select Atom and enable the Hood plugin only after reviewing the existing settings.
The former Hood snippet and separate eww-cursor plugin are superseded; follow the migration guide.
Do not install the latest marketplace version during setup or silently replace local edits.

Keep upstream CSS unchanged. Put custom styling in the Hood plugin's styles.css.
For an upgrade, review the upstream diff and license, compare in a test vault,
then update the commit, hashes, and compatibility notes together.

The user confirmed the former Atom + Hood snippet setup and custom cursor in a Mac test vault.
iPad was accepted based on another vault. Those results do not validate the new unified Hood plugin.
Automated checks establish byte identity, not rendering quality.
See CAPABILITIES.md in the repository root for remaining validation scope.
