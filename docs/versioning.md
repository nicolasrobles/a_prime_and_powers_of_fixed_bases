# Source identity and recording a new version

## The recorded manuscript

The statement numbers used in this repository refer to one version of the manuscript *A prime and powers of fixed bases* by Cristian Cobeli, Nicolas Robles, and Alexandru Zaharescu. That version is recorded under `manuscript` in `data/source_manifest.json`, with

- its version label and filename,
- its size in bytes, its number of lines, and its SHA-256 digest,
- the line ranges of its three numerical tables, by their labels `tab:G2`, `tab:G3` and `tab:k`.

The manuscript is not distributed here, and no verification program reads it. `scripts/check_source_tables.py` compares a local copy of the source with these records and with `data/tables.json`.

The numerical inputs are three files. The binary and ternary witnesses `binary_cover_1440_full.json` and `ap_certificate.json` preserve their original bytes. `data/tables.json` contains the entries of the three numerical tables of the manuscript and the constants claimed in it. The manifest records the size and digest of each input under `inputs`, and every run of the verification compares the files with these records.

The ternary witness retains its original weaker metadata value `certified_gamma="2.2874"`. The verifier checks the target $2.287407$ directly against the allocation entries.

The statement numbers occur in the following places: the docstrings of the programs, the fields `manuscript_statement` written by `scripts/balanced_sieve.py`, `scripts/base3_minimality.py`, `scripts/common_sums.py` and `scripts/odd_sum_counts.py` into their result files, the entry `scope` of the manifest, `README.md`, and `docs/methods.md`. They are Section 4, Tables 1 to 3, Lemma 5.1, Theorem 1.5, Section 6.2, Proposition 7.1 and Table 5.

## Reproducing the stored results

Run the complete checker from the repository root:

```sh
python3 verify_all.py
```

To compare a fresh run with the stored results without overwriting them, use a separate output directory:

```sh
python3 verify_all.py --output-dir _verification_tmp
```

The complete checker writes deterministic JSON. Corresponding JSON values from the two directories should agree. The exact rational fields provide the comparisons used in the proof. Floating-point fields are supplementary displays.

Regenerate tables and figures after the verification output has been updated:

```sh
python3 scripts/make_tables.py
python3 scripts/make_plots.py
```

The optional Matplotlib dependency is listed in `requirements-figures.txt`. The bytes of the image files depend on the Matplotlib version, so regenerating the figures may change the files without changing what they show.

## Recording a new version of the manuscript

1. Compare the three numerical tables of the new source with the inputs:

   ```sh
   python3 scripts/check_source_tables.py --rows-only /path/to/new_source.tex
   ```

2. Compare the constants in `parameters` of `data/tables.json` and the statement numbers listed above with the new source.
3. If the tables, the constants and the statement numbers are unchanged, replace the entry `manuscript` of `data/source_manifest.json` by the version label, filename, size, number of lines, digest and table line ranges of the new source. No other file changes. Then

   ```sh
   python3 scripts/check_source_tables.py /path/to/new_source.tex
   ```

   must end with `SUCCESS`.
4. If a table entry or a constant changes, update `data/tables.json` and its record under `inputs` together. Review the fixed allocation targets, order ranges, prime cutoffs, and expected counts in the code against the new statements. Run the complete checker and review every changed exact result. Regenerate the tables and figures, then execute the notebook.
5. If a statement number changes, update it in the places listed above, and run the complete checker so that the result files carry the new number.
6. Describe the change in the commit message.

Avoid changing the witness files merely to reformat their whitespace, because that needlessly changes their byte hashes.

## Release

The bibliography of the manuscript cites this repository by a release tag. A tag names one fixed state of the repository. It is to be created when the final version of the manuscript has been recorded here; until then the repository has no release and no DOI.

## Earlier drafts

The folder `old_material/` contains the records of the drafts v13, v19, v20, v21 and v23 as they stood before the version labels were removed from the programs. No program reads this folder. It can be deleted; its own `README.md` lists the two sentences elsewhere in the repository that mention it.

## Scope records

Keep three kinds of statements explicit when extending the repository:

- **Finite verifications:** an exhaustive enumeration or exact comparison that the code has actually performed.
- **Mathematical inputs:** theorems used to interpret those finite checks, such as the primitive-divisor supply.
- **Further work:** computations that have not yet been implemented or verified.

For example, the introductory stage factors the differences for the base-three candidate and does not test minimality. Its output points to `base3_minimality.json`, the record of the separate exhaustive computation.
