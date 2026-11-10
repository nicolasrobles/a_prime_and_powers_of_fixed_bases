# Source identity and later revisions

## The v13 snapshot

The numerical inputs in this repository correspond to:

- Manuscript title: *A prime and powers of fixed bases*.
- Authors: Cristian Cobeli, Nicolas Robles, and Alexandru Zaharescu.
- Source filename: `prime_and_fixed_base_powers_v13.tex`.
- Source size: 84,482 bytes, 1,934 lines.
- Source SHA-256:

```text
af63bc8cb54d4ba3b2e93d6b068d223fce2c822a521640568a353e6a312b7df7
```

The manuscript is identified by its hash. The repository's inputs contain the extracted numerical tables and the two original allocation witnesses, so verification does not require a local copy of the draft.

The binary and ternary witness files preserve their original bytes. In particular, the ternary witness retains its original weaker metadata value `certified_gamma="2.2874"`. The verifier checks the v13 target $2.287407$ directly against the allocation entries.

The source manifest records the input identities. The table file records the extraction labels and raw line ranges. The exact result files describe what was checked and contain the numerical witnesses needed to inspect the calculations.

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

The optional Matplotlib dependency is listed in `requirements-figures.txt`.

## Recording a manuscript revision

For each later version:

1. Record the new source filename, byte count, and SHA-256 digest.
2. Compare the three numerical tables and all claimed constants with the current inputs.
3. If an input changes, update its data file and the manifest together. Preserve the previous version in Git history.
4. Review the explicit v13 version guard in `scripts/verification.py` and update it when advancing the supported manuscript version. Review the fixed allocation targets, order ranges, prime cutoffs, and expected counts in the code against the new statements. Keep the input paths and the optional source-table checker consistent with any renamed files. Updating only the manifest and data is insufficient, because the current version guard will reject a different version.
5. Run the complete checker and review any changed exact result.
6. Regenerate the tables and figures, then execute the notebook.
7. Describe the mathematical change in the commit message or release notes.

If only prose changes and every numerical input and claimed constant is unchanged, record that fact with the new manuscript identity. Avoid changing witness files merely to reformat their whitespace, because that needlessly changes their byte hashes.

A release tag can later identify the exact repository state cited by a paper. The paper should cite an actual tag or full commit SHA once that version is fixed. This snapshot does not assign a DOI or claim a formal software release.

## Scope records

Keep three kinds of statements explicit when extending the repository:

- **Finite verifications:** an exhaustive enumeration or exact comparison that the code has actually performed.
- **Mathematical inputs:** theorems used to interpret those finite checks, such as the primitive-divisor supply.
- **Further work:** announced computations that have not yet been run, including a new exhaustive proof of the base-three minimality assertion.

For example, the current introductory output records `base3_minimality_checked: false`. Preserve that field until a separate computation covering every required smaller integer has been implemented, completed, and documented.
