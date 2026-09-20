"""
TruthLens Border Intelligence — Mock Registry Adapter
Adapter interface for government registry checks.

CRITICAL NOTICES:
1. ALL data here is SYNTHETIC/DEMO data — NOT real government records
2. System is clearly labelled as SIH 2026 PROTOTYPE
3. Architecture uses adapter pattern for future real API plug-in
4. Returns is_demo: True on every response

SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""

# ─── Synthetic Demo Data ─────────────────────────────────────
# Clearly marked synthetic demo data sets.
# In a real authorized system, these would be replaced by API calls
# to authorised government registries (e.g., Passport Seva, FRRO).

_DEMO_PASSPORT_REGISTRY = {
    # Format: passport_number → {status, name, nationality, note}
    # "FLAGGED" entries are demo cases for testing
    "Z9999999": {
        "status": "FLAGGED",
        "name":   "DEMO FLAGGED PERSON",
        "nationality": "IND",
        "note":   "[DEMO] This passport number is flagged in the demo watchlist",
    },
    "X0000001": {
        "status": "ACTIVE",
        "name":   "CLEAN DEMO PERSON",
        "nationality": "IND",
        "note":   "[DEMO] Valid active passport",
    },
    "A1234567": {
        "status": "REVOKED",
        "name":   "REVOKED DEMO PERSON",
        "nationality": "IND",
        "note":   "[DEMO] This passport has been revoked",
    },
}

_DEMO_WATCHLIST = [
    {
        "entry_id":  "WL-DEMO-001",
        "name":      "DEMO FLAGGED PERSON",
        "passport":  "Z9999999",
        "reason":    "[DEMO] Synthetic watchlist entry for testing",
        "added":     "2026-01-01",
    },
]

_DEMO_VISA_REGISTRY = {
    # format: passport_number → {visa_type, valid_from, valid_until, status}
    "X0000001": {
        "visa_type":   "TOURIST",
        "valid_from":  "2026-01-01",
        "valid_until": "2026-12-31",
        "status":      "ACTIVE",
        "note":        "[DEMO] Active tourist visa",
    },
}


# ─── Adapter Interface ────────────────────────────────────────

def check_passport_registry(passport_number: str,
                             name: str = "",
                             nationality: str = "") -> dict:
    """
    Check passport against registry.
    Returns status, source, note, is_demo.

    Architecture: Replace body of this function with authorized API call
    when integrating with real Passport Seva system.
    """
    pn = str(passport_number).strip().upper()
    entry = _DEMO_PASSPORT_REGISTRY.get(pn)

    if entry:
        return {
            "passport_number": pn,
            "status":          entry["status"],
            "registry_name":   entry.get("name", ""),
            "source":          "SYNTHETIC_DEMO_DATA",
            "note":            entry["note"],
            "is_demo":         True,
        }

    return {
        "passport_number": pn,
        "status":          "NOT_FOUND",
        "registry_name":   "",
        "source":          "SYNTHETIC_DEMO_DATA",
        "note":            "[DEMO] Passport number not in demo registry — would require real registry query",
        "is_demo":         True,
    }


def check_watchlist(name: str, passport_number: str = "") -> dict:
    """
    Check name/passport against watchlist.
    Returns match_found, matched_entry, source, is_demo.

    Architecture: Replace with authorized lookout notice / LOC system call.
    """
    pn   = str(passport_number).strip().upper()
    name_upper = str(name).strip().upper()

    for entry in _DEMO_WATCHLIST:
        if (entry.get("passport") == pn and pn) or \
           (entry.get("name", "").upper() == name_upper and name_upper):
            return {
                "match_found":   True,
                "matched_entry": {
                    "entry_id": entry["entry_id"],
                    "name":     entry["name"],
                    "reason":   entry["reason"],
                },
                "source":     "SYNTHETIC_DEMO_DATA",
                "note":       f"[DEMO] Watchlist match: {entry['reason']}",
                "is_demo":    True,
            }

    return {
        "match_found":   False,
        "matched_entry": None,
        "source":        "SYNTHETIC_DEMO_DATA",
        "note":          "[DEMO] No watchlist match",
        "is_demo":       True,
    }


def check_visa_registry(passport_number: str) -> dict:
    """
    Check visa status for a passport holder.
    Returns visa details, source, is_demo.

    Architecture: Replace with authorized FRRO/e-Visa system call.
    """
    pn = str(passport_number).strip().upper()
    entry = _DEMO_VISA_REGISTRY.get(pn)

    if entry:
        return {
            "passport_number": pn,
            "visa_found":      True,
            "visa_type":       entry["visa_type"],
            "valid_from":      entry["valid_from"],
            "valid_until":     entry["valid_until"],
            "status":          entry["status"],
            "source":          "SYNTHETIC_DEMO_DATA",
            "note":            entry["note"],
            "is_demo":         True,
        }

    return {
        "passport_number": pn,
        "visa_found":      False,
        "visa_type":       None,
        "source":          "SYNTHETIC_DEMO_DATA",
        "note":            "[DEMO] No visa record — would require real FRRO query",
        "is_demo":         True,
    }


def run_all_registry_checks(passport_number: str, name: str = "",
                              nationality: str = "") -> dict:
    """
    Run all registry checks and return combined result.
    """
    passport = check_passport_registry(passport_number, name, nationality)
    watchlist = check_watchlist(name, passport_number)
    visa = check_visa_registry(passport_number)

    return {
        "passport":  passport,
        "watchlist": watchlist,
        "visa":      visa,
        "is_demo":   True,
        "disclaimer": (
            "ALL registry data shown is SYNTHETIC DEMO DATA. "
            "This system has NO connection to real government databases (Passport Seva, FRRO, MHA, SSB). "
            "SIH 2026 PROTOTYPE — NOT FOR OPERATIONAL USE."
        ),
    }
