# claude-hooks — vendored copies

Source of record: the `claude-development` repository (`payneewp-boop/claude-development`).
That is where each file below is edited. Edits made here are overwritten the next
time the file is re-copied, and nothing upstream can see them.

| File | Source in claude-development | sha256 |
|---|---|---|
| `skill-frontmatter-lint.py` | `hooks/skill-frontmatter-lint.py` | sha256 `50288fb55df833dd4f767a16a8ae2a7d148634e936f2d32e006de8fed832d8f0` |

Pinned on 2026-10-15, at claude-development `3b18238` (the last commit that changed the source).

The hash is taken over the file with CRLF turned into LF. `.gitattributes` stores
LF but a Windows checkout writes CRLF, and the same file must give the same hash
on both.

## What checks it

`tests/test_provenance.py`, part of the ordinary suite. `python -m unittest discover`
runs it locally, and CI runs the same command on Windows, macOS and Linux. It
does three things:

1. Every `.py` in this directory has a row above, and every row names a file that exists.
2. Each file matches its recorded hash. This is a **pin**: it catches an edit made
   to the copy here.
3. When a `claude-development` checkout can be found, each file also matches the
   source. This catches the other direction, upstream moving on. It looks in
   `$CLAUDE_DEVELOPMENT`, then in a sibling folder named `Claude-development` or
   `claude-development`. CI has no sibling checkout, so there it is skipped, and
   the skip says why. Run the suite on the machine that has both folders to get
   the full check.

## Updating

1. Edit the file upstream, in `claude-development`.
2. Copy it here.
3. Run `python -m unittest tests.test_provenance`. It fails and prints the new
   hash on the `on disk:` line. Paste that into the table.
4. Update the date and commit in the line under the table.
5. Run the tests again, then commit.

Skipping step 3 fails the suite. That is the check doing its job, not a false alarm.
