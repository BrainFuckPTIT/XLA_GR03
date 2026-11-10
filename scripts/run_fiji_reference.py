"""Build the pinned Fiji plugin runner with Maven and execute the three fixed cases.

Requires Maven 3.9+ on PATH and a Java 8 JDK selected by JAVA_HOME. Writes a new
run log; refuses to overwrite labels unless --overwrite is explicitly supplied.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from xla_gr03.experiments import sha256, write_csv

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/fiji_rerun")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        raise ValueError("Set JAVA_HOME to a Java 8 JDK.")
    java = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
    version = subprocess.run([str(java), "-version"], capture_output=True, text=True, check=True)
    if '"1.8.' not in version.stderr + version.stdout:
        raise ValueError("The TensorFlow 1.12 ImageJ runtime requires Java 8.")
    fiji = ROOT / "fiji"
    subprocess.run(
        [
            "mvn",
            "-B",
            "-f",
            str(fiji / "pom.xml"),
            "compile",
            "dependency:copy-dependencies",
            "-DoutputDirectory=target/dependency",
        ],
        check=True,
    )
    jars = sorted((fiji / "target/dependency").glob("*.jar"))
    patchers = [p for p in jars if p.name.startswith("ij1-patcher-")]
    if len(patchers) != 1:
        raise ValueError(f"Expected one ij1-patcher JAR, found {patchers}")
    classpath = os.pathsep.join([str(fiji / "target/classes"), *map(str, jars)])
    # The old Java loader can extract JNI without its framework dependency on macOS.
    # Keep both bundled native files together and let the JVM load from that directory.
    native_platform = {
        "darwin": "darwin-x86_64",
        "linux": "linux-x86_64",
        "win32": "windows-x86_64",
    }
    native_dir = fiji / "target/native" / native_platform[sys.platform]
    native_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(fiji / "target/dependency/libtensorflow_jni-1.12.0.jar") as archive:
        prefix = f"org/tensorflow/native/{native_platform[sys.platform]}/"
        for name in archive.namelist():
            if name.startswith(prefix) and not name.endswith("/"):
                (native_dir / Path(name).name).write_bytes(archive.read(name))
    with (fiji / "run_log_dsb2018_reference.csv").open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))
    outputs = [args.output / case["image"] for case in cases]
    if not args.overwrite and any(p.exists() for p in outputs):
        raise FileExistsError("Output labels already exist; choose a fresh --output directory.")
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for case, output in zip(cases, outputs, strict=True):
        if args.overwrite:
            output.unlink(missing_ok=True)
        image = ROOT / "data/dsb2018/dsb2018/test/images" / case["image"]
        command = [
            str(java),
            f"-javaagent:{patchers[0]}",
            f"-Djava.library.path={native_dir}",
            "-Djava.awt.headless=true",
            "-cp",
            classpath,
            "FijiStarDistRunner",
            str(image),
            str(output),
            "1",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        (args.output / f"{case['tag']}.log").write_text(
            result.stdout + result.stderr, encoding="utf-8"
        )
        result.check_returncode()
        match = re.search(r"^RUNTIME_S=([0-9.]+)$", result.stdout, re.MULTILINE)
        if not match or not output.is_file():
            raise RuntimeError(f"Runner did not produce labels/runtime for {image.name}")
        rows.append(
            {
                **case,
                "runtime_s": float(match[1]),
                "run_id": "reproduced",
                "input_sha256": sha256(image),
                "label_sha256": sha256(output),
                "java_runtime": (version.stderr + version.stdout).splitlines()[0],
            }
        )
        write_csv(args.output / "run_log.csv", rows)
    write_csv(
        args.output / "dependency_manifest.csv",
        [{"jar": p.name, "sha256": sha256(p)} for p in jars],
    )


if __name__ == "__main__":
    main()
