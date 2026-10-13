# OpenROAD PPA report analyzer

`scripts/ppa_report.py` summarizes metrics already present in the repository's OpenROAD reports. It does **not** run synthesis, place-and-route, STA, or power analysis.

## Usage

From the repository root:

```bash
# Print a console summary
python scripts/ppa_report.py --reports-dir reports

# Write machine-readable summaries as well
python scripts/ppa_report.py \
  --reports-dir reports \
  --csv-out out/ppa-summary.csv \
  --json-out out/ppa-summary.json

# Run the parser's unit tests (Python standard library only)
python -m unittest discover -s tests -v
```

The analyzer searches recursively for `6_finish.rpt` files. If a report has a sibling `synth_stat.txt`, the tool also reads the synthesis area from that file. Output order is stable by report path.

## Reported fields

| Field | Source |
| --- | --- |
| `wns_ns`, `tns_ns` | `report_wns` and `report_tns` sections in the finish report |
| `worst_slack_ns` | `report_worst_slack` section |
| `min_period_ns`, `fmax_mhz` | `report_clock_min_period` section |
| `sequential_power_w`, `combinational_power_w`, `clock_power_w`, `total_power_w` | `report_power` section, when present |
| `synthesis_area_um2` | `Chip area for module` in the sibling `synth_stat.txt`, when present |

Metrics that are absent stay unavailable: CSV cells are blank and JSON values are `null`. The console also prints a warning for missing fields rather than substituting zero.

## Interpretation notes

- `synthesis_area_um2` is the area reported by synthesis statistics; do not label it as final routed area.
- Power values are the estimates in the source report and depend on the flow's libraries, constraints, and activity assumptions.
- Compare results only when design constraints, libraries, corners, and flow stages are compatible.
- Report timing units are preserved as represented by this project's OpenROAD output; the field names use nanoseconds and MHz for this repository's configured reports.
