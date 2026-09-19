# Collecting EnergyPlus transition data

`collect_transition_data.py` assembles the versioned reference data used to
implement and test one EnergyPlus epJSON upgrade. It is designed to be
repeatable and to leave the EnergyPlus source checkout unchanged.

## What it collects

For a transition such as 23.2.0 to 24.1.0, the script collects:

- the source and destination `Energy+.schema.epJSON` files;
- the source and destination `Energy+.idd` files;
- the input-change rules document;
- the output-change document;
- the report-variable and meter-name mapping CSV;
- every IDF, IMF, and native epJSON file under `testfiles` in the source tag;
- a JSON manifest containing Git revisions, SHA-256 hashes, tool identities,
  conversion results, validation results, and exclusions.

IDFs are converted with the source release's `ConvertInputFormat`. Root IMF
examples are expanded with the source release's `EPMacro` and then converted.
IMF files included by another IMF are recorded as support fragments instead of
being treated as independent examples. Existing epJSON examples are copied
without re-encoding. Directory structure below `testfiles` is preserved.

Some test files in an EnergyPlus release tag retain an older `Version` object
even though their contents belong to the tagged release. The collector changes
only that version value in its temporary extracted copy before conversion. It
does not modify the EnergyPlus checkout or run older transition rules over the
file. Every affected filename, original version, normalized version, and the
before/after hashes are recorded in the manifest. The filenames are also
printed in the normal summary so the stale metadata can be reported upstream.

The official Fortran transition implementation is **not copied**. The script
checks that the target EnergyPlus tag contains it and records its repository
path and SHA-256 hash. It also fingerprints the installed official transition
executable so that later behavior comparisons can identify the exact oracle.

## Prerequisites

- Git must be available on `PATH`.
- The EnergyPlus Git checkout must contain the source and target release tags.
- Both EnergyPlus releases must be installed locally.
- The source installation must contain:
  - `energyplus`;
  - `ConvertInputFormat`;
  - `EPMacro`;
  - `Energy+.schema.epJSON`;
  - `Energy+.idd`.
- The target installation must contain:
  - `energyplus`;
  - `Energy+.schema.epJSON`;
  - `Energy+.idd`;
  - the transition executable under `PreProcess/IDFVersionUpdater`.
- Run the script through the Hatch development environment so that
  `jsonschema-rs` is available.

`--from-install` and `--to-install` are the roots of the installed releases,
not source or build directories. The script verifies versions reported by the
executables and versions declared by the schemas; directory names are not
trusted.

## Usage

From the `energyplus-version` repository on Windows:

```powershell
hatch run python scripts/collect_transition_data.py `
  --energyplus-repo C:\Users\me\Projects\EnergyPlus `
  --from-version 23.2.0 `
  --to-version 24.1.0 `
  --from-install C:\EnergyPlusV23-2-0 `
  --to-install C:\EnergyPlusV24-1-0
```

On Linux or macOS:

```bash
hatch run python scripts/collect_transition_data.py \
  --energyplus-repo /work/EnergyPlus \
  --from-version 23.2.0 \
  --to-version 24.1.0 \
  --from-install /opt/EnergyPlus-23-2-0 \
  --to-install /opt/EnergyPlus-24-1-0
```

Versions must always contain three components. By default, `23.2.0` selects
the `v23.2.0` tag and `24.1.0` selects `v24.1.0`. Use `--source-tag` or
`--target-tag` only when intentionally collecting from another immutable Git
revision.

Use `--dry-run` to execute extraction, conversion, and validation without
publishing any collected files:

```powershell
hatch run python scripts/collect_transition_data.py <required options> --dry-run
```

Use `--verbose` to print details for every failed file. The output includes the
source filename, expected output filename, `EPMacro` or `ConvertInputFormat`
exit code, captured tool diagnostics, and complete schema-validation error:

```powershell
hatch run python scripts/collect_transition_data.py <required options> --dry-run --verbose
```

Verbose diagnostics are written to standard error so they can be captured
separately when desired:

```powershell
hatch run python scripts/collect_transition_data.py <required options> --dry-run --verbose `
  2> collection-failures.log
```

## Output layout

The default output root is the repository root:

```text
schema/
  23.2.0/Energy+.schema.epJSON
  24.1.0/Energy+.schema.epJSON
idd/
  23.2.0/Energy+.idd
  24.1.0/Energy+.idd
rules/
  Rules23-2-0-to-24-1-0.md
  OutputChanges23-2-0-to-24-1-0.md
  Report Variables 23-2-0 to 24-1-0.csv
test_files/
  23.2.0/...
manifests/
  23.2.0-to-24.1.0.json
```

Three-component directory names keep patch releases distinct.

## Validation and failure behavior

Every collected epJSON file is validated against the source schema with one
reused Rust-backed Draft 7 validator. Its `Version` object is checked
separately and must identify the source version. This extra check is necessary
because the schema's version `default` is an annotation, not a constraint.
Missing converter outputs, invalid JSON, version mismatches, and schema
failures are all written to the manifest.

The normal behavior is conservative:

- Collection happens in temporary staging directories.
- Existing identical files are accepted as unchanged.
- Differing existing files are never overwritten unless `--replace` is used.
- Conversion or validation failures prevent the corpus from being published.
- A failure manifest is written under `manifests` for diagnosis.

Normalized stale-version filenames are always printed. Without `--verbose`,
the console otherwise reports only failure counts and the failure manifest
location. With `--verbose`, the same file-level failure details recorded in
the manifest are also printed immediately.

`ConvertInputFormat` processes files in a batch, may interleave output when
built with OpenMP, and can return process exit code zero even when an individual
file fails. When a batch does not produce an expected epJSON file, the collector
therefore retries that source file by itself. A successful retry is retained as
the collected output. If the retry also fails, boilerplate status lines and
temporary absolute paths are removed from its diagnostic before the concise
per-file error is placed in the manifest or printed by `--verbose`.

`--replace` is appropriate when deliberately refreshing previously collected
data from verified release artifacts. It can replace only the version-specific
targets selected by the command.

`--allow-failures` publishes a partial corpus and records every failure. This
should be used only after reviewing why the official converter cannot process
particular files. A committed manifest should make every exclusion explicit.

## Provenance and reproducibility

The manifest records:

- source and target tag names and resolved commit hashes;
- hashes and reported versions of EnergyPlus and conversion tools;
- hashes of schemas and IDDs;
- source paths and hashes of transition documentation;
- the path and hash of the Fortran reference implementation, marked as not
  copied;
- source/output hashes for each converted or copied example;
- stale Version-object filenames, original and normalized versions, and hashes;
- preprocessing, conversion, and schema-validation failures.

Absolute installation and checkout paths are not stored in the manifest.
Executable hashes may legitimately differ across operating systems, so the
platform is also recorded.

## Scope

The collected corpus provides broad regression coverage; it does not prove
that every transition rule is exercised. Each implemented transition still
needs focused unit tests and an end-to-end fixture containing every documented
change and important edge case.
