"""Owner-authorized publication of Sports Medicine source-limited systems.

Keep the source limitations internally. Do not turn incomplete printed values into
clinical claims or expose editorial review language on product pages.
"""

import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports/double-medical/sports-medicine-catalogue.json"
REPORT_DIR = REPORT_PATH.parent / "sports-medicine-catalogue"
REPORT = json.loads(REPORT_PATH.read_text())
TARGETS = {
    "metal-suture-anchor",
    "peek-suture-anchor",
    "peek-suture-anchor-instruments",
    "knee-repair-and-reconstruction-instrument-set",
    "tibiofibular-syndesmosis-instrument-set",
}
assert {entry["slug"] for entry in REPORT["newSystems"] if entry["status"] == "draft"} == TARGETS
evidence = json.loads((REPORT_DIR / "code-verification.json").read_text())
assert len(evidence) == 198 and all(record["verification"].startswith("verified") for record in evidence)

accepted = []
now = dt.datetime.now(dt.timezone.utc).isoformat()
for slug in sorted(TARGETS):
    path = ROOT / "content/products/double-medical" / f"{slug}.json"
    system = json.loads(path.read_text())
    assert system["status"] == "draft" and system["review"]["flags"]
    assert system["review"]["sourceSha256"] == REPORT["sourceSha256"]
    accepted.extend({"system": system["name"], "slug": slug, **flag} for flag in system["review"]["flags"])

    # The catalog literally prints '/ #' without the numbers. Show the exact
    # known anchor size and REF; omit the unusable specification column.
    if slug in {"metal-suture-anchor", "peek-suture-anchor"}:
        incomplete = {"/ #", "/ # × мм", "/ # × mm"}
        for table in system["specTables"]:
            if len(table["columns"]) == 3 and table["rows"] and all(
                isinstance(row[2], dict) and row[2]["en"] in incomplete for row in table["rows"]
            ):
                table["columns"] = table["columns"][:2]
                table["rows"] = [row[:2] for row in table["rows"]]

    # These two REFs are legible, but their printed names are not. They stay
    # in the internal evidence and out of ordering until a name is available.
    if slug == "peek-suture-anchor-instruments":
        excluded = {"111036700", "111036800"}
        for table in system["specTables"]:
            indexes = [i for i, row in enumerate(table["rows"]) if row[1] not in excluded]
            for key in ("rows", "rowSources", "rowImages"):
                if key in table:
                    table[key] = [table[key][i] for i in indexes]
        system["refCodes"] = [code for code in system["refCodes"] if code not in excluded]
        system["review"]["excludedUnnamedRefCodes"] = sorted(excluded)
        assert all(row[0]["en"] != "—" for table in system["specTables"] for row in table["rows"])

    # The source's English word 'open' is known and can be translated without
    # changing the printed REF or adding a measurement.
    if slug == "tibiofibular-syndesmosis-instrument-set":
        for table in system["specTables"]:
            for row in table["rows"]:
                if row[1] == "115260200":
                    assert row[0]["ru"] == "Сверлящая спица, open"
                    row[0]["ru"] = "Сверлящая спица с открытым концом"
        for image in system.get("gallery", []):
            if image.get("imageCaption", {}).get("ru") == "Сверлящая спица, open":
                image["imageCaption"]["ru"] = "Сверлящая спица с открытым концом"

    system["review"]["sourceLimitations"] = system["review"].pop("flags")
    system["review"]["flags"] = []
    system["review"]["status"] = "owner-accepted-source-limitations"
    system["review"]["publicationDecision"] = "Owner authorized publication with verified REFs and incomplete source-only specifications omitted from public tables."
    system["review"]["ownerPublicationOverride"] = True
    system["status"] = "published"
    system["publishedAt"] = now
    path.write_text(json.dumps(system, ensure_ascii=False, indent=2) + "\n")

REPORT["systemsPublished"] = 16
REPORT["systemsDraft"] = 0
REPORT["openRealFlags"] = []
REPORT["acceptedSourceLimitations"] = accepted
REPORT["publicationDate"] = now
for entry in REPORT["newSystems"]:
    if entry["slug"] in TARGETS:
        entry["status"] = "published"
REPORT_PATH.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + "\n")

lines = (REPORT_DIR / "REPORT.md").read_text().splitlines()
lines = [line.replace("published: 11; drafts: 5", "published: 16; drafts: 0") for line in lines]
start = lines.index("## Open real issues")
end = lines.index("## Random sample of 20 REF rows")
lines[start:end] = [
    "## Source limitations accepted for publication",
    "",
    "All five formerly held systems are published under the owner's instruction. Missing values were omitted from public tables; source evidence remains in the product review metadata. Two verified but unnamed instrument REFs (111036700, 111036800) remain internal and cannot be ordered from the site.",
    "",
]
(REPORT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"published": 16, "drafts": 0, "acceptedSourceLimitations": len(accepted), "withheldUnnamedRefCodes": 2}))
