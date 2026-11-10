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

## The v19 revision

- Source filename: `prime_and_fixed_base_powers_v19.tex`.
- Source size: 142,639 bytes, 3,178 lines.
- Source SHA-256:

```text
71c0bf24fb9e36e42702a8e6b4916123746b78e08bda795b635fda12207adefe
```

The three numerical tables of v19 agree with `data/tables_v13.json` in every entry; only the empty cell of the third table is typeset differently. The targets $Z_2$, $Z_3$ and the bounds for $P_i$, $Z_iP_i$ and $C_i$ are unchanged. The two allocation witnesses and the results of the stages `finite` and `tail` therefore apply to v19 as they stand, and they keep their v13 identification.

Two stages were added for statements that first appear after v13:

- `balanced` (Lemma 5.1), implemented in `scripts/balanced_sieve.py`, with the result file `balanced_sieve.json`;
- `base3` (Theorem 1.5), implemented in `scripts/base3_minimality.py`, with the result file `base3_minimality.json`.

The revision is recorded under `revisions` in `data/source_manifest.json`, with the line ranges of the three tables in the v19 source. `scripts/check_source_tables.py` accepts either recorded source.

## The v20 revision

- Source filename: `prime_and_fixed_base_powers_v20.tex`.
- Source size: 157,071 bytes, 3,472 lines.
- Source SHA-256:

```text
1ec50e6c79525322824cc2318567350bddf7fea8322647a4407f6fc6ff599381
```

The tables and constants are those of v19. Two stages were added for the section on two distinct bases:

- `common` (Proposition 7.1), implemented in `scripts/common_sums.py`, with the result file `common_sums.json`;
- `counts` (Table 5), implemented in `scripts/odd_sum_counts.py`, with the result file `odd_sum_counts.json`. These counts are numerical data.

## The v21 revision

- Source filename: `prime_and_fixed_base_powers_v21.tex`.
- Source size: 162,036 bytes, 3,561 lines.
- Source SHA-256:

```text
898d6e77868d14d992a52bad2340472f8953d69c7b0311068cc0e9047d871c16
```

The tables and constants are those of v20, and no stage was added. The revision adds the concluding section of the manuscript, which names no new computation, and one clarification in the proof of the theorem on balanced triples.

## The v23 revision

- Source filename: `prime_and_fixed_base_powers_v23.tex`.
- Source size: 175,370 bytes, 3,797 lines.
- Source SHA-256:

```text
81ee9d05d72cbd108473946450b44816c02f7db637adcac59bfbf8773ee1a07a
```

The tables and constants are those of v20, and no stage was added. The revision completes the introduction and adds the abstract; the three tables are at later lines of the source. The intermediate v22 is not recorded.

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
- **Further work:** computations that have not yet been implemented or verified.

For example, the introductory stage factors the differences for the base-three candidate and does not test minimality. Its output points to `base3_minimality.json`, the record of the separate exhaustive computation.
