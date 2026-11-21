"""Publish source-reviewed Sports Medicine systems with no real open flags."""

import csv
import datetime as dt
import hashlib
import json
import random
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports/double-medical/sports-medicine-catalogue"
PROFILE = json.loads((ROOT / "scripts/profiles/double-medical-sports-medicine.json").read_text())
SOURCE = ROOT / "catalogs-source/double-medical/sports-medicine-catalogue.pdf"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == PROFILE["sha256"]
evidence = json.loads((REPORT_DIR / "code-verification.json").read_text())
assert len(evidence) == 198
assert all(item["verification"].startswith("verified") for item in evidence)
assert len(PROFILE["systems"]) == 16 and len(PROFILE["merges"]) == 1

# The merge must remain additive. The original M-Link clinical data and source stay intact.
merge_slug = PROFILE["merges"][0]["slug"]
old_path = REPORT_DIR / "merge-backups" / PROFILE["sha256"] / (merge_slug + ".json")
original = json.loads(old_path.read_text())
merged = json.loads((ROOT / "content/products/double-medical" / (merge_slug + ".json")).read_text())
for field in ("name", "shortDescription", "description", "status", "sourcePdf", "sourcePages", "variants", "features", "hotspots", "heroImage"):
    assert original.get(field) == merged.get(field), f"M-Link {field} changed"
assert set(merged["refCodes"]) - set(original["refCodes"]) == {"114302000", "114301200"}

published_at = dt.datetime.now(dt.timezone.utc).isoformat()
systems = []
open_flags = []
sample_pool = []
for profile_system in PROFILE["systems"]:
    path = ROOT / "content/products/double-medical" / (profile_system["slug"] + ".json")
    system = json.loads(path.read_text())
    assert system["refCodes"] == profile_system["refCodes"]
    assert set(system["sourcePages"]) <= set(PROFILE["authorizedPhysicalPages"])
    flags = [flag for flag in system["review"]["flags"] if flag.get("status") not in ("resolved", "dismissed")]
    system["status"] = "draft" if flags else "published"
    if not flags:
        system["publishedAt"] = published_at
        system["review"]["publicationDecision"] = "Authorized automatic publication after source review; no open real flags."
    path.write_text(json.dumps(system, ensure_ascii=False, indent=2) + "\n")
    systems.append(system)
    for flag in flags:
        open_flags.append({"system": system["name"], "slug": system["slug"], **flag})

for system in systems + [PROFILE["merges"][0]]:
    for table in system.get("specTables", system.get("referenceTables", [])):
        for row in table.get("rows", []):
            codes = [cell for cell in row if isinstance(cell, str) and re.fullmatch(r"\d{9}S?", cell)]
            if codes:
                sample_pool.append({
                    "system": system["name"],
                    "pdfPage": table["sourcePages"][0] if table.get("sourcePages") else (table.get("rowSources") or [{}])[0].get("pdfPage"),
                    "REF": " / ".join(codes),
                    "size": row[0],
                })

sample = random.Random(20261121).sample(sample_pool, 20)
published = sum(system["status"] == "published" for system in systems)
assert published == 11 and len(systems) - published == 5
report = {
    "sourcePdf": str(SOURCE.relative_to(ROOT)),
    "sourceSha256": PROFILE["sha256"],
    "systemsNew": 16,
    "systemsMerged": 1,
    "systemsPublished": published,
    "systemsDraft": 5,
    "implantSystems": 8,
    "instrumentPages": 8,
    "instrumentSets": 6,
    "instrumentCollections": 2,
    "codesFound": len(evidence),
    "codesVerified": len(evidence),
    "distinctCodes": len({item["code"] for item in evidence}),
    "newSystems": [{"name": s["name"], "slug": s["slug"], "status": s["status"], "sourcePages": s["sourcePages"]} for s in systems],
    "mergedSystems": [{"name": merged["name"], "slug": merge_slug, "newRefCodes": ["114302000", "114301200"], "sourcePages": [10, 38]}],
    "otherOverlaps": json.loads((REPORT_DIR / "overlaps.json").read_text()),
    "openRealFlags": open_flags,
    "randomSample": sample,
    "randomSampleSeed": 20261121,
    "publicationDate": published_at,
}
(ROOT / "reports/double-medical/sports-medicine-catalogue.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
(REPORT_DIR / "random-sample-20.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n")
with (REPORT_DIR / "random-sample-20.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["System RU", "System EN", "PDF page", "REF", "Size RU", "Size EN"])
    for row in sample:
        size = row["size"]
        writer.writerow([row["system"]["ru"], row["system"]["en"], row["pdfPage"], row["REF"], size["ru"] if isinstance(size, dict) else size, size["en"] if isinstance(size, dict) else size])

lines = [
    "# Double Medical Sports Medicine Catalogue",
    "",
    f"New systems: 16; published: {published}; drafts: 5; additive M-Link merges: 1.",
    f"Printed REF occurrences found and verified: {len(evidence)}; distinct: {report['distinctCodes']}.",
    "PDF physical pages 4–38 imported; cover, about, contents, blank page 39 and back cover skipped.",
    "",
    "## M-Link merge",
    "Existing clinical content and seven original REFs preserved. Added instrument set REF 114302000 and reusable knot pusher/suture cutter REF 114301200 from PDF page 38. The p.10 implant REF and the other p.38 instruments already existed.",
    "",
    "## Other site REF overlaps",
]
for overlap in report["otherOverlaps"]:
    lines.append(f"- {overlap['REF']}: {overlap['system']} also occurs in {', '.join(overlap['existingSystems'])}.")
lines += ["", "## Open real issues"]
for flag in open_flags:
    lines.append(f"- {flag['system']['en']}, PDF p.{flag.get('pdfPage')}: {flag['message']['en']}")
lines += ["", "## Random sample of 20 REF rows", "", "| System | PDF page | REF | Size / description |", "|---|---:|---|---|"]
for row in sample:
    size = row["size"]["en"] if isinstance(row["size"], dict) else row["size"]
    lines.append(f"| {row['system']['en']} | {row['pdfPage']} | {row['REF']} | {size} |")
(REPORT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n")
print(json.dumps({key: report[key] for key in ("systemsNew", "systemsMerged", "systemsPublished", "systemsDraft", "codesFound", "codesVerified", "distinctCodes")}, ensure_ascii=False))
