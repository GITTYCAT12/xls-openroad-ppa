"""Unit tests for scripts.ppa_report; no OpenROAD installation is required."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ppa_report import discover_reports, parse_report, write_csv, write_json  # noqa: E402


REPORT_TEXT = """\
==========================================================================
finish report_tns
--------------------------------------------------------------------------
tns max -0.73

==========================================================================
finish report_wns
--------------------------------------------------------------------------
wns max -0.05

==========================================================================
finish report_worst_slack
--------------------------------------------------------------------------
worst slack max 3.55

==========================================================================
finish report_clock_min_period
--------------------------------------------------------------------------
clk period_min = 1.45 fmax = 689.79

==========================================================================
finish report_power
--------------------------------------------------------------------------
Group                  Internal  Switching    Leakage      Total
                           Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential             6.72e-04   1.22e-04   1.65e-05   8.10e-04   5.8%
Combinational          6.79e-03   5.99e-03   1.59e-04   1.29e-02  93.1%
Clock                  5.20e-05   9.86e-05   1.09e-06   1.52e-04   1.1%
Total                  7.51e-03   6.21e-03   1.76e-04   1.39e-02 100.0%
"""


class PpaReportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "reports"
        self.design_dir = self.root / "matmul_systolic"
        self.design_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parses_timing_power_and_synthesis_area(self):
        report = self.design_dir / "6_finish.rpt"
        report.write_text(REPORT_TEXT, encoding="utf-8")
        (self.design_dir / "synth_stat.txt").write_text(
            "Chip area for module '\\matmul_systolic': 8694.476000\n",
            encoding="utf-8",
        )

        result = parse_report(report)

        self.assertEqual(result["design"], "matmul_systolic")
        self.assertAlmostEqual(result["wns_ns"], -0.05)
        self.assertAlmostEqual(result["tns_ns"], -0.73)
        self.assertAlmostEqual(result["worst_slack_ns"], 3.55)
        self.assertAlmostEqual(result["min_period_ns"], 1.45)
        self.assertAlmostEqual(result["fmax_mhz"], 689.79)
        self.assertAlmostEqual(result["synthesis_area_um2"], 8694.476)
        self.assertAlmostEqual(result["sequential_power_w"], 8.10e-04)
        self.assertAlmostEqual(result["combinational_power_w"], 1.29e-02)
        self.assertAlmostEqual(result["clock_power_w"], 1.52e-04)
        self.assertAlmostEqual(result["total_power_w"], 1.39e-02)

    def test_missing_metrics_are_not_reported_as_zero(self):
        report = self.design_dir / "6_finish.rpt"
        report.write_text("OpenROAD report with no recognized metric sections\n", encoding="utf-8")

        result = parse_report(report)

        self.assertIsNone(result["wns_ns"])
        self.assertIsNone(result["fmax_mhz"])
        self.assertIsNone(result["synthesis_area_um2"])
        self.assertIsNone(result["total_power_w"])

    def test_discovery_is_sorted_and_fails_for_empty_directory(self):
        (self.design_dir / "6_finish.rpt").write_text("wns max 0.00\n", encoding="utf-8")
        other_dir = self.root / "matmul_unrolled"
        other_dir.mkdir()
        (other_dir / "6_finish.rpt").write_text("wns max 0.00\n", encoding="utf-8")

        reports = discover_reports(self.root)

        self.assertEqual([path.parent.name for path in reports], ["matmul_systolic", "matmul_unrolled"])
        empty_dir = Path(self.temp_dir.name) / "empty"
        empty_dir.mkdir()
        with self.assertRaisesRegex(ValueError, "no 6_finish.rpt"):
            discover_reports(empty_dir)

    def test_csv_and_json_export(self):
        report = self.design_dir / "6_finish.rpt"
        report.write_text(REPORT_TEXT, encoding="utf-8")
        result = parse_report(report)
        csv_path = Path(self.temp_dir.name) / "out" / "summary.csv"
        json_path = Path(self.temp_dir.name) / "out" / "summary.json"

        write_csv([result], csv_path)
        write_json([result], json_path)

        with csv_path.open(newline="", encoding="utf-8") as handle:
            csv_rows = list(csv.DictReader(handle))
        json_rows = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(csv_rows), 1)
        self.assertEqual(csv_rows[0]["design"], "matmul_systolic")
        self.assertEqual(json_rows[0]["design"], "matmul_systolic")
        self.assertEqual(json_rows[0]["wns_ns"], -0.05)


if __name__ == "__main__":
    unittest.main()
