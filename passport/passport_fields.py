"""
TruthLens Border Intelligence — Passport Fields
Structured dataclass for passport document fields.
SIH 2026 · PS 26188 · PROTOTYPE — NOT FOR OPERATIONAL USE
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PassportFields:
    """
    Structured representation of a passport document.
    Fields are extracted from both OCR (visual zone) and MRZ.
    """
    # Visual zone fields (extracted by OCR)
    name_visual: str = ""
    surname_visual: str = ""
    given_names_visual: str = ""
    passport_number_visual: str = ""
    nationality_visual: str = ""
    dob_visual: str = ""           # YYYY-MM-DD or raw
    expiry_visual: str = ""        # YYYY-MM-DD or raw
    gender_visual: str = ""        # M / F / X
    place_of_birth: str = ""
    place_of_issue: str = ""
    issue_date_visual: str = ""

    # MRZ zone fields (extracted by MRZ engine)
    mrz_line1: str = ""
    mrz_line2: str = ""
    document_type_mrz: str = ""    # P, PX, etc.
    country_code_mrz: str = ""     # ISO 3166-1 alpha-3
    surname_mrz: str = ""
    given_names_mrz: str = ""
    passport_number_mrz: str = ""
    nationality_mrz: str = ""
    dob_mrz: str = ""              # YYMMDD raw from MRZ
    dob_mrz_parsed: str = ""       # YYYY-MM-DD
    gender_mrz: str = ""
    expiry_mrz: str = ""           # YYMMDD raw from MRZ
    expiry_mrz_parsed: str = ""    # YYYY-MM-DD
    personal_number_mrz: str = ""

    # MRZ check-digit results
    check_passport_number: bool = False
    check_dob: bool = False
    check_expiry: bool = False
    check_personal_number: bool = False
    check_composite: bool = False
    mrz_checks_passed: int = 0
    mrz_checks_total: int = 5

    # Extraction metadata
    ocr_raw_text: str = ""
    ocr_confidence: float = 0.0     # estimated 0–1
    mrz_detected: bool = False
    mrz_confidence: float = 0.0     # estimated 0–1
    extraction_warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @property
    def full_name_visual(self) -> str:
        parts = [self.surname_visual, self.given_names_visual]
        return " ".join(p for p in parts if p).strip() or self.name_visual

    @property
    def full_name_mrz(self) -> str:
        parts = [self.surname_mrz, self.given_names_mrz]
        return " ".join(p for p in parts if p).strip()
