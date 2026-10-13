#!/usr/bin/env python3
"""Extract comparable PPA metrics from OpenROAD finish reports.

The parser is deliberately tolerant of reports that omit a metric: unavailable
values are emitted as null/blank rather than being guessed or silently set to
zero. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"

METRIC_PATTERNS = {
    "tns_ns": re.compile(rf"^\s*tns\s+max\s+({NUMBER})\s*$", re.IGNORECASE | re.MULTILINE),
    "wns_ns": re.compile(rf"^\s*wns\s+max\s+({NUMBER})\s*$", re.IGNORECASE | re.MULTILINE),
    "worst_slack_ns": re.compile(
        rf"^\s*worst\s+slack\s+max\s+({NUMBER})\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}
CLOCK_PATTERN = re.compile(
    rf"^\s*clk\s+period_min\s*=\s*({NUMBER})\s+fmax\s*=\s*({NUMBER})\s*$",
    re.IGNORECASE | re.MULTILINE,
)
AREA_PATTERN = re.compile(
    rf"^\s*Chip area for module\b.*?:\s*({NUMBER})\s*$",
    re.IGNORECASE | re.MULTILINE,
)
POWER_ROW_PATTERN = re.compile(
    rf"^\s*(?P<group>Sequential|Combinational|Clock|Total)\s+"
    rf"(?P<internal>{NUMBER})\s+(?P<switching>{NUMBER})\s+"
    rf"(?P<leakage>{NUMBER})\s+(?P<total>{NUMBER})(?:\s+\S+)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

CSV_FIELDS = [
    "design",
    "report",
    "wns_ns",
    "tns_ns",
    "worst_slack_ns",
    "min_period_ns",
    "fmax_mhz",
    "synthesis_area_um2",
    "sequential_power_w",
    "combinational_power_w",
    "clock_power_w",
    "total_power_w",
]
METRIC_FIELDS = CSV_FIELDS[2:]


def _first_float(pattern: re.Pattern[str], text: str) -> Optional[float]:
    match = pattern.search(text)
    return float(match.group(1)) if match else None


def parse_report(report_path: Path) -> Dict[str, Any]:
    """Parse one OpenROAD 6_finish.rpt and its sibling synth_stat.txt, if present."""
    report_path = Path(report_path)
    text = report_path.read_text(encoding="utf-8", errors="replace")

    row: Dict[str, Any] = {
        "design": report_path.parent.name,
        "report": report_path.as_posix(),
        "wns_ns": _first_float(METRIC_PATTERNS["wns_ns"], text),
        "tns_ns": _first_float(METRIC_PATTERNS["tns_ns"], text),
        "worst_slack_ns": _first_float(METRIC_PATTERNS["worst_slack_ns"], text),
        "min_period_ns": None,
        "fmax_mhz": None,
        "synthesis_area_um2": None,
        "sequential_power_w": None,
        "combinational_power_w": None,
        "clock_power_w": None,
        "total_power_w": None,
    }

    clock_match = CLOCK_PATTERN.search(text)
    if clock_match:
        row["min_period_ns"] = float(clock_match.group(1))
        row["fmax_mhz"] = float(clock_match.group(2))

    power_totals: Dict[str, float] = {}
    for match in POWER_ROW_PATTERN.finditer(text):
        power_totals[match.group("group").lower()] = float(match.group("total"))

    for group in ("sequential", "combinational", "clock", "total"):
        row[f"{group}_power_w"] = power_totals.get(group)

    synth_stat = report_path.with_name("synth_stat.txt")
    if synth_stat.is_file():
        synth_text = synth_stat.read_text(encoding="utf-8", errors="replace")
        row["synthesis_area_um2"] = _first_float(AREA_PATTERN, synth_text)

    return row


def discover_reports(reports_dir: Path) -> List[Path]:
    """Return a stable, sorted list of final OpenROAD reports under reports_dir."""
    reports_dir = Path(reports_dir)
    if not reports_dir.is_dir():
        raise ValueError(f"reports directory does not exist: {reports_dir}")

    reports = sorted(reports_dir.rglob("6_finish.rpt"), key=lambda path: path.as_posix())
    if not reports:
        raise ValueError(f"no 6_finish.rpt files found under: {reports_dir}")
    return reports


def write_csv(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _format(value: Any) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def print_summary(rows: List[Dict[str, Any]]) -> None:
    print(
        f"{'Design':<24} {'WNS (ns)':>10} {'TNS (ns)':>10} "
        f"{'Fmax (MHz)':>12} {'Area (um^2)':>13} {'Power (W)':>12}"
    )
    print("-" * 86)
    for row in rows:
        print(
            f"{row['design']:<24} "
            f"{_format(row['wns_ns']):>10} "
            f"{_format(row['tns_ns']):>10} "
            f"{_format(row['fmax_mhz']):>12} "
            f"{_format(row['synthesis_area_um2']):>13} "
            f"{_format(row['total_power_w']):>12}"
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize timing, synthesis area, and power metrics from OpenROAD reports."
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="directory containing design subdirectories and 6_finish.rpt files (default: reports)",
    )
    parser.add_argument("--csv-out", type=Path, help="optional path for a CSV summary")
    parser.add_argument("--json-out", type=Path, help="optional path for a JSON summary")
    args = parser.parse_args(argv)

    try:
        reports = discover_reports(args.reports_dir)
        rows = [parse_report(report) for report in reports]
        if args.csv_out:
            write_csv(rows, args.csv_out)
        if args.json_out:
            write_json(rows, args.json_out)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print_summary(rows)
    for row in rows:
        missing = [field for field in METRIC_FIELDS if row[field] is None]
        if missing:
            print(
                f"warning: {row['design']}: unavailable metrics: {', '.join(missing)}",
                file=sys.stderr,
            )

    if args.csv_out:
        print(f"CSV written to {args.csv_out}")
    if args.json_out:
        print(f"JSON written to {args.json_out}")
    print(f"Parsed {len(rows)} report(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
