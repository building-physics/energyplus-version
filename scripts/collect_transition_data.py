# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
"""Collect the reference data needed to implement an EnergyPlus transition.

The EnergyPlus source checkout is accessed only through read-only ``git``
commands. Installed EnergyPlus releases provide generated schemas, IDDs, and
the version-matched conversion tools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import jsonschema_rs


VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class CollectionError(RuntimeError):
    """Raised when release data cannot be collected safely."""


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "Version":
        match = VERSION_PATTERN.fullmatch(value)
        if match is None:
            raise argparse.ArgumentTypeError(
                f'Invalid version "{value}"; use a three-component version such as 23.2.0.'
            )
        return cls(*(int(part) for part in match.groups()))

    def dotted(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def dashed(self) -> str:
        return f"{self.major}-{self.minor}-{self.patch}"

    def short(self) -> str:
        return f"{self.major}.{self.minor}"

    def tag(self) -> str:
        return f"v{self.dotted()}"


def run(
    command: Sequence[os.PathLike[str] | str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=text,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if text else ""
        stdout = result.stdout.strip() if text else ""
        details = stderr or stdout or f"exit status {result.returncode}"
        raise CollectionError(f"Command failed: {' '.join(map(str, command))}\n{details}")
    return result


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_text(repo: Path, *arguments: str) -> str:
    return run(["git", "-C", repo, *arguments]).stdout


def git_bytes(repo: Path, revision: str, source_path: str) -> bytes:
    result = run(
        ["git", "-C", repo, "show", f"{revision}:{source_path}"],
        text=False,
    )
    return result.stdout


def resolve_commit(repo: Path, revision: str) -> str:
    return git_text(repo, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()


def list_git_files(repo: Path, revision: str, source_path: str) -> list[str]:
    output = git_text(repo, "ls-tree", "-r", "--name-only", revision, "--", source_path)
    return sorted(line for line in output.splitlines() if line)


def executable_names(base_name: str) -> tuple[str, ...]:
    return (f"{base_name}.exe", base_name) if os.name == "nt" else (base_name, f"{base_name}.exe")


def find_install_file(install: Path, relative_directories: Iterable[str], names: Iterable[str]) -> Path:
    checked = []
    for directory in relative_directories:
        for name in names:
            candidate = install / directory / name
            checked.append(candidate)
            if candidate.is_file():
                return candidate.resolve()
    locations = "\n  ".join(str(path) for path in checked)
    raise CollectionError(f"Required installation file was not found. Checked:\n  {locations}")


def find_schema(install: Path) -> Path:
    return find_install_file(install, ("",), ("Energy+.schema.epJSON",))


def find_idd(install: Path) -> Path:
    return find_install_file(install, ("",), ("Energy+.idd",))


def find_energyplus(install: Path) -> Path:
    return find_install_file(install, ("",), executable_names("energyplus"))


def find_converter(install: Path) -> Path:
    return find_install_file(install, ("",), executable_names("ConvertInputFormat"))


def find_epmacro(install: Path) -> Path:
    return find_install_file(install, ("",), executable_names("EPMacro"))


def find_transition(install: Path, from_version: Version, to_version: Version) -> Path:
    name = f"Transition-V{from_version.dashed()}-to-V{to_version.dashed()}"
    return find_install_file(
        install,
        ("PreProcess/IDFVersionUpdater", ""),
        executable_names(name),
    )


def command_version(executable: Path) -> str:
    result = run([executable, "--version"])
    return "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())


def verify_reported_version(label: str, reported: str, expected: Version) -> None:
    # EnergyPlus tools may print a build suffix, but the release triplet must be present.
    pattern = re.compile(rf"(?<!\d){re.escape(expected.dotted())}(?!\d)")
    if pattern.search(reported) is None:
        raise CollectionError(
            f"{label} does not report expected version {expected.dotted()}. Reported: {reported!r}"
        )


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def schema_declared_version(schema: object) -> str:
    try:
        value = schema["properties"]["Version"]["patternProperties"][".*"]["properties"][
            "version_identifier"
        ]["default"]
    except (KeyError, TypeError) as exc:
        raise CollectionError("Schema does not contain the expected Version default.") from exc
    return str(value)


def verify_schema(path: Path, expected: Version) -> object:
    schema = load_json(path)
    declared = schema_declared_version(schema)
    if declared != expected.short() and declared != expected.dotted():
        raise CollectionError(
            f"Schema {path} declares version {declared}, expected {expected.dotted()}."
        )
    # Compilation also validates that jsonschema-rs accepts the schema.
    jsonschema_rs.Draft7Validator(schema)
    return schema


def transition_source_paths(from_version: Version, to_version: Version) -> dict[str, str]:
    pair = f"{from_version.dashed()}-to-{to_version.dashed()}"
    return {
        "input_rules": f"src/Transition/InputRulesFiles/Rules{pair}.md",
        "output_changes": f"src/Transition/OutputRulesFiles/OutputChanges{pair}.md",
        "report_variables": (
            "src/Transition/SupportFiles/Report Variables "
            f"{from_version.dashed()} to {to_version.dashed()}.csv"
        ),
        "fortran_reference": (
            "src/Transition/CreateNewIDFUsingRules"
            f"V{to_version.major}_{to_version.minor}_{to_version.patch}.f90"
        ),
    }


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def files_equal(left: Path, right: Path) -> bool:
    return left.is_file() and right.is_file() and sha256_file(left) == sha256_file(right)


def trees_equal(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False
    left_files = sorted(path.relative_to(left) for path in left.rglob("*") if path.is_file())
    right_files = sorted(path.relative_to(right) for path in right.rglob("*") if path.is_file())
    return left_files == right_files and all(files_equal(left / path, right / path) for path in left_files)


def publish_file(staged: Path, destination: Path, replace: bool) -> str:
    if destination.exists():
        if files_equal(staged, destination):
            return "unchanged"
        if not replace:
            raise CollectionError(f"Refusing to replace changed file without --replace: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged, destination)
    return "written"


def publish_tree(staged: Path, destination: Path, replace: bool) -> str:
    if destination.exists():
        if trees_equal(staged, destination):
            return "unchanged"
        if not replace:
            raise CollectionError(f"Refusing to replace changed directory without --replace: {destination}")
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staged), str(destination))
    return "written"


def ensure_publishable_file(staged: Path, destination: Path, replace: bool) -> None:
    if destination.exists() and not files_equal(staged, destination) and not replace:
        raise CollectionError(f"Refusing to replace changed file without --replace: {destination}")


def ensure_publishable_tree(staged: Path, destination: Path, replace: bool) -> None:
    if destination.exists() and not trees_equal(staged, destination) and not replace:
        raise CollectionError(f"Refusing to replace changed directory without --replace: {destination}")


def extract_examples(repo: Path, revision: str, staging_root: Path) -> list[str]:
    staging_root.mkdir(parents=True, exist_ok=True)
    archive_path = staging_root.parent / "source-examples.tar"
    with archive_path.open("wb") as archive_stream:
        result = subprocess.run(
            ["git", "-C", str(repo), "archive", "--format=tar", revision, "--", "testfiles"],
            check=False,
            stdout=archive_stream,
            stderr=subprocess.PIPE,
            text=False,
        )
    if result.returncode != 0:
        raise CollectionError(
            "Could not archive EnergyPlus examples:\n" + result.stderr.decode(errors="replace").strip()
        )

    selected = []
    with tarfile.open(archive_path, "r") as archive:
        for member in archive.getmembers():
            if not member.isfile() or Path(member.name).suffix.lower() not in {".idf", ".imf", ".epjson"}:
                continue
            member_path = Path(member.name)
            if not member_path.parts or member_path.parts[0] != "testfiles" or ".." in member_path.parts:
                raise CollectionError(f"Unsafe path in Git archive: {member.name}")
            source = archive.extractfile(member)
            if source is None:
                raise CollectionError(f"Could not read Git archive member: {member.name}")
            relative = Path(*member_path.parts[1:])
            write_bytes(staging_root / relative, source.read())
            selected.append(member.name)
    archive_path.unlink()
    return sorted(selected)


def clean_converter_diagnostic(stdout: str, stderr: str, source: Path) -> str:
    noise = (
        "Input file converted to ",
        "Input file conversion failed:",
        "Errors occurred when validating input file. Preceding condition(s) cause termination.",
        "Errors occurred when processing input file. Preceding condition(s) cause termination.",
    )
    source_strings = {str(source), source.as_posix(), str(source.resolve()), source.resolve().as_posix()}
    cleaned = []
    for line in (stderr + "\n" + stdout).splitlines():
        line = line.strip()
        if not line or line.startswith(noise):
            continue
        for source_string in sorted(source_strings, key=len, reverse=True):
            line = line.replace(source_string, source.name)
        if not cleaned or cleaned[-1] != line:
            cleaned.append(line)
    return "\n".join(cleaned) or "ConvertInputFormat did not create the expected output or report a specific error."


def retry_conversion_for_diagnostics(converter: Path, source: Path, destination: Path) -> tuple[int, str, bool]:
    with tempfile.TemporaryDirectory(prefix="energyplus-version-convert-diagnostic-") as temporary_directory:
        diagnostic_output = Path(temporary_directory)
        result = run(
            [converter, "--output", diagnostic_output, "--format", "epJSON", source],
            check=False,
        )
        generated = diagnostic_output / f"{source.stem}.epJSON"
        if generated.is_file():
            copy_file(generated, destination)
            return result.returncode, "Per-file retry created the expected output.", True
        return (
            result.returncode,
            clean_converter_diagnostic(result.stdout, result.stderr, source),
            False,
        )


def convert_idfs(converter: Path, source_root: Path, output_root: Path) -> tuple[list[dict], list[dict]]:
    converted: list[dict] = []
    failures: list[dict] = []
    idfs_by_directory: dict[Path, list[Path]] = {}
    for source in sorted(source_root.rglob("*.idf")):
        idfs_by_directory.setdefault(source.parent, []).append(source)

    for source_directory, sources in idfs_by_directory.items():
        relative_directory = source_directory.relative_to(source_root)
        destination_directory = output_root / relative_directory
        destination_directory.mkdir(parents=True, exist_ok=True)
        list_file = source_directory / ".energyplus-version-convert-list.txt"
        list_file.write_text("\n".join(str(path.resolve()) for path in sources) + "\n", encoding="utf-8")
        result = run(
            [converter, "--input", list_file, "--output", destination_directory, "--format", "epJSON"],
            check=False,
        )
        list_file.unlink()

        for source in sources:
            destination = destination_directory / f"{source.stem}.epJSON"
            source_name = source.relative_to(source_root).as_posix()
            output_name = destination.relative_to(output_root).as_posix()
            diagnostic_exit_code = result.returncode
            diagnostic_message = ""
            if not destination.is_file():
                diagnostic_exit_code, diagnostic_message, recovered = retry_conversion_for_diagnostics(
                    converter, source, destination
                )
                if recovered:
                    diagnostic_message = ""
            if destination.is_file():
                converted.append(
                    {
                        "source": source_name,
                        "output": output_name,
                        "source_sha256": sha256_file(source),
                        "output_sha256": sha256_file(destination),
                    }
                )
            else:
                failures.append(
                    {
                        "source": source_name,
                        "expected_output": output_name,
                        "reason": "ConvertInputFormat did not create the expected output.",
                        "converter_exit_code": diagnostic_exit_code,
                        "converter_message": diagnostic_message,
                    }
                )
    return converted, failures


def expand_imfs(epmacro: Path, source_root: Path, expanded_root: Path) -> tuple[list[dict], list[dict], list[str]]:
    imf_paths = sorted(source_root.rglob("*.imf"))
    included_paths: set[Path] = set()
    include_pattern = re.compile(r"^\s*##include\s+['\"]?([^'\"\s]+)", re.IGNORECASE | re.MULTILINE)
    for path in imf_paths:
        contents = path.read_text(encoding="utf-8", errors="replace")
        for match in include_pattern.finditer(contents):
            included_paths.add((path.parent / match.group(1)).resolve())

    roots = [path for path in imf_paths if path.resolve() not in included_paths]
    expanded = []
    failures = []
    for root in roots:
        relative = root.relative_to(source_root)
        with tempfile.TemporaryDirectory(prefix="energyplus-version-epmacro-") as temporary_directory:
            work = Path(temporary_directory)
            for support_file in imf_paths:
                if support_file.parent == root.parent:
                    copy_file(support_file, work / support_file.name)
            shutil.copyfile(work / root.name, work / "in.imf")
            result = run([epmacro], cwd=work, check=False)
            generated = work / "out.idf"
            if result.returncode != 0 or not generated.is_file():
                epmacro_message = (result.stderr or result.stdout).strip()
                epmacro_message = epmacro_message.replace(str(work), "<epmacro-staging>")[-2000:]
                failures.append(
                    {
                        "source": relative.as_posix(),
                        "epmacro_exit_code": result.returncode,
                        "epmacro_message": epmacro_message,
                    }
                )
                continue
            destination = expanded_root / relative.with_suffix(".idf")
            copy_file(generated, destination)
            expanded.append(
                {
                    "source": relative.as_posix(),
                    "expanded_idf": destination.relative_to(expanded_root).as_posix(),
                    "source_sha256": sha256_file(root),
                    "expanded_sha256": sha256_file(destination),
                }
            )
    support_files = sorted(path.relative_to(source_root).as_posix() for path in imf_paths if path not in roots)
    return expanded, failures, support_files


def copy_native_epjson(source_root: Path, output_root: Path) -> list[dict]:
    copied = []
    for source in sorted(source_root.rglob("*.epJSON")):
        relative = source.relative_to(source_root)
        destination = output_root / relative
        if destination.exists() and not files_equal(source, destination):
            raise CollectionError(f"Native and converted epJSON files collide: {relative.as_posix()}")
        copy_file(source, destination)
        copied.append(
            {
                "source": relative.as_posix(),
                "output": relative.as_posix(),
                "source_sha256": sha256_file(source),
                "output_sha256": sha256_file(destination),
            }
        )
    return copied


def validate_examples(output_root: Path, schema: object) -> list[dict]:
    validator = jsonschema_rs.Draft7Validator(schema)
    failures = []
    for path in sorted(output_root.rglob("*.epJSON")):
        try:
            instance = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"file": path.relative_to(output_root).as_posix(), "error": str(exc)})
            continue
        try:
            validator.validate(instance)
        except jsonschema_rs.ValidationError as exc:
            failures.append({"file": path.relative_to(output_root).as_posix(), "error": str(exc)})
    return failures


def artifact_metadata(path: Path, reported_version: str | None = None) -> dict:
    metadata = {"name": path.name, "sha256": sha256_file(path)}
    if reported_version is not None:
        metadata["reported_version"] = reported_version
    return metadata


def print_failure_details(conversion_failures: list[dict], validation_failures: list[dict]) -> None:
    if conversion_failures:
        print("\nConversion and preprocessing failures:", file=sys.stderr)
        for failure in conversion_failures:
            print(f"  {failure['source']}", file=sys.stderr)
            if "expected_output" in failure:
                print(f"    expected output: {failure['expected_output']}", file=sys.stderr)
            if "reason" in failure:
                print(f"    reason: {failure['reason']}", file=sys.stderr)
            if "epmacro_exit_code" in failure:
                print(f"    EPMacro exit code: {failure['epmacro_exit_code']}", file=sys.stderr)
            if "converter_exit_code" in failure:
                print(f"    ConvertInputFormat exit code: {failure['converter_exit_code']}", file=sys.stderr)
            message = failure.get("epmacro_message") or failure.get("converter_message")
            if message:
                print("    diagnostic:", file=sys.stderr)
                for line in message.splitlines():
                    print(f"      {line}", file=sys.stderr)

    if validation_failures:
        print("\nSchema-validation failures:", file=sys.stderr)
        for failure in validation_failures:
            print(f"  {failure['file']}", file=sys.stderr)
            for line in failure["error"].splitlines():
                print(f"    {line}", file=sys.stderr)


def collect(args: argparse.Namespace) -> int:
    source_version: Version = args.from_version
    target_version: Version = args.to_version
    if target_version <= source_version:
        raise CollectionError("--to-version must be newer than --from-version.")

    repo = args.energyplus_repo.resolve()
    source_install = args.from_install.resolve()
    target_install = args.to_install.resolve()
    output_root = args.output_root.resolve()
    if not (repo / ".git").exists():
        raise CollectionError(f"Not an EnergyPlus Git checkout: {repo}")

    source_revision = args.source_tag or source_version.tag()
    target_revision = args.target_tag or target_version.tag()
    source_commit = resolve_commit(repo, source_revision)
    target_commit = resolve_commit(repo, target_revision)

    source_energyplus = find_energyplus(source_install)
    target_energyplus = find_energyplus(target_install)
    converter = find_converter(source_install)
    epmacro = find_epmacro(source_install)
    source_schema_path = find_schema(source_install)
    target_schema_path = find_schema(target_install)
    source_idd_path = find_idd(source_install)
    target_idd_path = find_idd(target_install)
    transition_executable = find_transition(target_install, source_version, target_version)

    source_energyplus_version = command_version(source_energyplus)
    target_energyplus_version = command_version(target_energyplus)
    converter_version = command_version(converter)
    verify_reported_version("source EnergyPlus", source_energyplus_version, source_version)
    verify_reported_version("target EnergyPlus", target_energyplus_version, target_version)
    verify_reported_version("source ConvertInputFormat", converter_version, source_version)

    source_schema = verify_schema(source_schema_path, source_version)
    verify_schema(target_schema_path, target_version)

    source_paths = transition_source_paths(source_version, target_version)
    transition_data = {
        name: git_bytes(repo, target_revision, source_path)
        for name, source_path in source_paths.items()
    }

    pair_name = f"{source_version.dotted()}-to-{target_version.dotted()}"
    with tempfile.TemporaryDirectory(prefix="energyplus-version-collect-") as temporary_directory:
        staging = Path(temporary_directory)
        extracted_examples = staging / "source-examples"
        expanded_examples = staging / "expanded-examples"
        staged_examples = staging / "test_files" / source_version.dotted()
        staged_examples.mkdir(parents=True)
        source_example_paths = extract_examples(repo, source_revision, extracted_examples)
        converted, conversion_failures = convert_idfs(
            converter, extracted_examples, staged_examples
        )
        expanded_imfs, epmacro_failures, macro_support_files = expand_imfs(
            epmacro, extracted_examples, expanded_examples
        )
        converted_imfs, converted_imf_failures = convert_idfs(
            converter, expanded_examples, staged_examples
        )
        imf_sources = {entry["expanded_idf"]: entry["source"] for entry in expanded_imfs}
        for entry in converted_imfs:
            entry["expanded_idf"] = entry["source"]
            entry["source"] = imf_sources[entry["source"]]
            entry["preprocessor"] = "EPMacro"
        for entry in converted_imf_failures:
            expanded_idf = entry["source"]
            entry["expanded_idf"] = expanded_idf
            entry["source"] = imf_sources[expanded_idf]
            entry["preprocessor"] = "EPMacro"
        conversion_failures.extend(epmacro_failures)
        conversion_failures.extend(converted_imf_failures)
        native = copy_native_epjson(extracted_examples, staged_examples)
        validation_failures = validate_examples(staged_examples, source_schema)

        if (conversion_failures or validation_failures) and not args.allow_failures:
            summary = (
                f"Collection found {len(conversion_failures)} conversion failures and "
                f"{len(validation_failures)} validation failures. Re-run with "
                "--allow-failures only after reviewing the manifest."
            )
        else:
            summary = "Collection completed."

        installed_artifacts = {
            output_root / "schema" / source_version.dotted() / "Energy+.schema.epJSON": source_schema_path,
            output_root / "schema" / target_version.dotted() / "Energy+.schema.epJSON": target_schema_path,
            output_root / "idd" / source_version.dotted() / "Energy+.idd": source_idd_path,
            output_root / "idd" / target_version.dotted() / "Energy+.idd": target_idd_path,
        }
        staged_files = {}
        for destination, source in installed_artifacts.items():
            staged_path = staging / "artifacts" / destination.relative_to(output_root)
            copy_file(source, staged_path)
            staged_files[destination] = staged_path

        rule_destinations = {
            "input_rules": output_root / "rules" / Path(source_paths["input_rules"]).name,
            "output_changes": output_root / "rules" / Path(source_paths["output_changes"]).name,
            "report_variables": output_root / "rules" / Path(source_paths["report_variables"]).name,
        }
        for name, destination in rule_destinations.items():
            staged_path = staging / "artifacts" / destination.relative_to(output_root)
            write_bytes(staged_path, transition_data[name])
            staged_files[destination] = staged_path

        manifest = {
            "format_version": 1,
            "transition": {"from": source_version.dotted(), "to": target_version.dotted()},
            "energyplus_source": {
                "source_revision": source_revision,
                "source_commit": source_commit,
                "target_revision": target_revision,
                "target_commit": target_commit,
            },
            "tools": {
                "platform": platform.platform(),
                "source_energyplus": artifact_metadata(source_energyplus, source_energyplus_version),
                "target_energyplus": artifact_metadata(target_energyplus, target_energyplus_version),
                "source_converter": artifact_metadata(converter, converter_version),
                "source_epmacro": artifact_metadata(epmacro),
                "official_transition": artifact_metadata(transition_executable),
            },
            "reference_files": {
                name: {
                    "source_path": source_paths[name],
                    "sha256": sha256_bytes(data),
                    "copied": name != "fortran_reference",
                }
                for name, data in transition_data.items()
            },
            "schemas": {
                source_version.dotted(): artifact_metadata(source_schema_path),
                target_version.dotted(): artifact_metadata(target_schema_path),
            },
            "idds": {
                source_version.dotted(): artifact_metadata(source_idd_path),
                target_version.dotted(): artifact_metadata(target_idd_path),
            },
            "examples": {
                "source_path": "testfiles",
                "source_files_selected": len(source_example_paths),
                "converted_idfs": converted,
                "converted_imfs": converted_imfs,
                "native_epjson": native,
                "expanded_imfs": expanded_imfs,
                "macro_support_files": macro_support_files,
                "conversion_failures": conversion_failures,
                "validation_failures": validation_failures,
            },
        }
        staged_manifest = staging / "artifacts" / "manifests" / f"{pair_name}.json"
        staged_manifest.parent.mkdir(parents=True, exist_ok=True)
        staged_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest_destination = output_root / "manifests" / f"{pair_name}.json"
        staged_files[manifest_destination] = staged_manifest

        print(summary)
        print(f"  IDFs converted: {len(converted)}")
        print(f"  Expanded IMF examples converted: {len(converted_imfs)}")
        print(f"  Native epJSON files copied: {len(native)}")
        print(f"  Root IMF examples expanded: {len(expanded_imfs)}")
        print(f"  Included IMF support fragments: {len(macro_support_files)}")
        print(f"  Conversion failures: {len(conversion_failures)}")
        print(f"  Validation failures: {len(validation_failures)}")
        if args.verbose:
            print_failure_details(conversion_failures, validation_failures)

        if args.dry_run:
            print("Dry run: no collected data was published.")
            if conversion_failures or validation_failures:
                return 1
        elif not conversion_failures and not validation_failures or args.allow_failures:
            for destination, staged_source in staged_files.items():
                ensure_publishable_file(staged_source, destination, args.replace)
            examples_destination = output_root / "test_files" / source_version.dotted()
            ensure_publishable_tree(staged_examples, examples_destination, args.replace)
            for destination, staged_source in staged_files.items():
                publish_file(staged_source, destination, args.replace)
            publish_tree(
                staged_examples,
                examples_destination,
                args.replace,
            )
            print(f"Published data under {output_root}")
        else:
            failure_manifest = output_root / "manifests" / f"{pair_name}.failed.json"
            failure_manifest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staged_manifest, failure_manifest)
            print(f"Failure manifest written to {failure_manifest}", file=sys.stderr)
            return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description=(
            "Collect schemas, IDDs, transition rules, report-variable mappings, and a "
            "validated epJSON example corpus for one EnergyPlus upgrade."
        )
    )
    parser.add_argument("--energyplus-repo", type=Path, required=True, help="EnergyPlus Git checkout (read-only).")
    parser.add_argument("--from-version", type=Version.parse, required=True, help="Source version, e.g. 23.2.0.")
    parser.add_argument("--to-version", type=Version.parse, required=True, help="Target version, e.g. 24.1.0.")
    parser.add_argument("--from-install", type=Path, required=True, help="Root of the installed source release.")
    parser.add_argument("--to-install", type=Path, required=True, help="Root of the installed target release.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=project_root,
        help=f"Repository receiving collected data (default: {project_root}).",
    )
    parser.add_argument("--source-tag", help="Source Git revision (default: v<from-version> tag).")
    parser.add_argument("--target-tag", help="Target Git revision (default: v<to-version> tag).")
    parser.add_argument("--replace", action="store_true", help="Replace collected files that differ from a prior run.")
    parser.add_argument(
        "--allow-failures",
        action="store_true",
        help="Publish a partial corpus despite conversion or schema-validation failures.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Run collection and validation without publishing files.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print file-level conversion, preprocessing, and schema-validation failure details.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return collect(args)
    except CollectionError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
