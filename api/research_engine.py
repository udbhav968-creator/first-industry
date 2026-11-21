import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

EOL_DATABASE: Dict[str, Dict[str, str]] = {
    "node": {
        "14": "2023-04-30",
        "16": "2023-09-11",
        "18": "2025-04-30",
        "20": "2026-04-30",
    },
    "python": {
        "2.7": "2020-01-01",
        "3.6": "2021-12-23",
        "3.7": "2023-06-27",
        "3.8": "2024-10-07",
        "3.9": "2025-10-31",
    },
    "postgres": {
        "11": "2023-11-09",
        "12": "2024-11-14",
        "13": "2025-11-13",
        "14": "2026-11-12",
    },
    "react": {
        "16": "2022-06-14",
        "17": "2024-04-25",
    },
    "django": {
        "3.2": "2024-04-01",
        "4.0": "2023-04-01",
        "4.1": "2023-12-01",
    }
}

KNOWN_ADVISORIES: List[Dict] = [
    {
        "id": "CVE-2023-32002",
        "component": "node",
        "affected_range": ">= 16.0.0, < 16.20.1",
        "severity": "high",
        "fixed_in": "16.20.1",
        "description": "Permissions policies can be bypassed via Module._load in Node.js.",
    },
    {
        "id": "CVE-2023-32006",
        "component": "node",
        "affected_range": ">= 18.0.0, < 18.16.1",
        "severity": "high",
        "fixed_in": "18.16.1",
        "description": "Permissions policy bypass through process.binding() in Node.js 18.x.",
    },
    {
        "id": "CVE-2023-45853",
        "component": "node",
        "affected_range": ">= 20.0.0, < 20.8.1",
        "severity": "critical",
        "fixed_in": "20.8.1",
        "description": "High memory consumption and DoS vulnerability in Node.js 20 HTTP parser.",
    },
    {
        "id": "CVE-2020-5260",
        "component": "git",
        "affected_range": "< 2.26.1",
        "severity": "critical",
        "fixed_in": "2.26.1",
        "description": "Credential helper credential leak in git URLs containing newlines.",
    },
    {
        "id": "CVE-2024-21626",
        "component": "docker",
        "affected_range": "< 25.0.2",
        "severity": "high",
        "fixed_in": "25.0.2",
        "description": "runc container breakout through leaked file descriptors.",
    },
    {
        "id": "CVE-2022-24765",
        "component": "git",
        "affected_range": ">= 2.30.0, < 2.35.2",
        "severity": "medium",
        "fixed_in": "2.35.2",
        "description": "Git on multi-user systems may execute untrusted repository configs.",
    },
    {
        "id": "CVE-2022-21703",
        "component": "react",
        "affected_range": ">= 17.0.0, < 17.0.3",
        "severity": "medium",
        "fixed_in": "17.0.3",
        "description": "Potential Cross-Site Scripting (XSS) in server-side rendered React applications.",
    },
    {
        "id": "CVE-2024-24762",
        "component": "fastapi",
        "affected_range": ">= 0.100.0, < 0.109.1",
        "severity": "high",
        "fixed_in": "0.109.1",
        "description": "ReDoS vulnerability in python-multipart via FormData boundary parameter.",
    }
]

def parse_stack_input(entry: str) -> Tuple[str, str]:
    entry = entry.strip()
    match = re.split(r'[@\s:]+', entry, maxsplit=1)
    if len(match) == 2:
        component, version = match[0].lower(), match[1].strip()
        if version.startswith('v'):
            version = version[1:]
        return component, version
    raise ValueError(f"Invalid stack entry format: '{entry}'")

def parse_semver(v: str) -> Tuple[int, int, int]:
    parts = re.findall(r'\d+', v)
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0
    return major, minor, patch

def compare_versions(v1: str, v2: str) -> int:
    t1 = parse_semver(v1)
    t2 = parse_semver(v2)
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0

def is_version_affected(current_version: str, affected_range: str) -> bool:
    clauses = [c.strip() for c in affected_range.split(',') if c.strip()]
    for clause in clauses:
        match = re.match(r'^(<=|>=|<|>|==|=)?\s*([0-9\.]+.*)$', clause)
        if not match:
            continue
        op, target_v = match.group(1), match.group(2)
        if not op or op == '=':
            op = '=='

        cmp = compare_versions(current_version, target_v)
        if op == '<' and not (cmp < 0):
            return False
        elif op == '<=' and not (cmp <= 0):
            return False
        elif op == '>' and not (cmp > 0):
            return False
        elif op == '>=' and not (cmp >= 0):
            return False
        elif op == '==' and not (cmp == 0):
            return False

    return True

def check_eol_status(component: str, version: str) -> Optional[Dict[str, str]]:
    comp_lower = component.lower()
    if comp_lower not in EOL_DATABASE:
        return None

    major, minor, _ = parse_semver(version)
    candidates = [f"{major}.{minor}", str(major)]

    for series in candidates:
        if series in EOL_DATABASE[comp_lower]:
            eol_date_str = EOL_DATABASE[comp_lower][series]
            eol_date = datetime.strptime(eol_date_str, "%Y-%m-%d").date()
            is_expired = datetime.now().date() >= eol_date
            return {
                "eol_date": eol_date_str,
                "is_expired": is_expired,
                "series": series
            }
    return None

def calculate_effort_and_impact(severity: str, current_v: str, target_v: Optional[str]) -> Tuple[int, int]:
    severity_map = {
        "critical": 5,
        "high": 4,
        "medium": 3,
        "low": 2,
        "info": 1,
    }
    impact = severity_map.get(severity.lower(), 2)

    if not target_v:
        return impact, 3

    cur_major, cur_minor, _ = parse_semver(current_v)
    tgt_major, tgt_minor, _ = parse_semver(target_v)

    if tgt_major > cur_major:
        effort = 5
    elif tgt_minor > cur_minor:
        effort = 3
    else:
        effort = 1

    return impact, effort

def sanitize_advisory_text(raw_text: str) -> str:
    dangerous_patterns = [
        r"(?i)curl\s+.*?\|\s*(?:bash|sh)",
        r"(?i)rm\s+-rf\s+/",
        r"(?i)nc\s+-[e|c]\s+.*",
        r"(?i)exploit\s+code\s*:",
        r"(?i)proof\s+of\s+concept\s*\(poc\)\s*:",
    ]
    sanitized = raw_text
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "[redacted]", sanitized)
    return sanitized

def analyze_tech_stack(stack: List[Dict[str, str]]) -> Dict:
    findings = []
    upgrade_paths = []
    sources = set()
    severity_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

    for item in stack:
        comp_name = item.get("name", "").strip().lower()
        version = item.get("version", "").strip()

        sources.add(f"https://nvd.nist.gov/vuln/search/results?query={comp_name}")
        sources.add(f"https://endoflife.date/{comp_name}")

        eol_info = check_eol_status(comp_name, version)
        eol_date = eol_info["eol_date"] if eol_info else None

        matched_advisories = [
            adv for adv in KNOWN_ADVISORIES
            if adv["component"] == comp_name and is_version_affected(version, adv["affected_range"])
        ]

        for adv in matched_advisories:
            sev = adv["severity"].lower()
            if sev in severity_distribution:
                severity_distribution[sev] += 1

            impact, effort = calculate_effort_and_impact(sev, version, adv.get("fixed_in"))
            clean_desc = sanitize_advisory_text(adv["description"])

            findings.append({
                "id": adv["id"],
                "component": comp_name,
                "severity": sev,
                "affected_versions": adv["affected_range"],
                "fixed_in": adv.get("fixed_in"),
                "end_of_life_date": eol_date,
                "description": clean_desc,
                "impact_score": impact,
                "effort_score": effort,
            })

            if adv.get("fixed_in"):
                upgrade_paths.append({
                    "component": comp_name,
                    "current_version": version,
                    "target_version": adv["fixed_in"],
                    "breaking_changes_note": f"Upgrade fixes {adv['id']}. Effort: {effort}/5.",
                })

        if eol_info and eol_info["is_expired"] and not matched_advisories:
            severity_distribution["medium"] += 1
            findings.append({
                "id": f"EOL-{comp_name.upper()}-{eol_info['series']}",
                "component": comp_name,
                "severity": "medium",
                "affected_versions": f"<= {eol_info['series']}.x",
                "fixed_in": None,
                "end_of_life_date": eol_info["eol_date"],
                "description": f"{comp_name} {eol_info['series']} reached end-of-life on {eol_info['eol_date']}.",
                "impact_score": 3,
                "effort_score": 4,
            })

    return {
        "findings": findings,
        "severity_distribution": severity_distribution,
        "upgrade_paths": upgrade_paths,
        "sources": sorted(list(sources)),
    }
