# Old material

This folder keeps the records of earlier drafts of the manuscript. No program in the repository reads it, and the verification, the table generator, the figure generator, the notebook and the automatic checks do not depend on it.

| File | Contents |
|---|---|
| `tables_v13.json` | The table data file as it was extracted from the draft v13, with the digest of that draft and the line ranges of its three tables. Its table entries and constants are those of `data/tables.json`. |
| `source_manifest_v13_to_v23.json` | The source manifest as it stood when it identified the draft v13 and recorded the drafts v19, v20, v21 and v23, with their digests, sizes and table line ranges. |
| `versioning_v13_to_v23.md` | The versioning notes of that state, which describe what changed from one of these drafts to the next. |

The three files are unchanged copies. The paths and commands named inside them are those of that earlier state of the repository and need not exist any more.

## Deleting this folder

The folder can be deleted without changing any program or result. Two places mention it and should then be removed as well:

- the row `old_material/` of the table in the section "Files" of `README.md`;
- the section "Earlier drafts" of `docs/versioning.md`.

The earlier states of the repository remain available in the Git history.
