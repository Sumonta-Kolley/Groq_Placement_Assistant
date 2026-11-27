import json
from pathlib import Path
from langchain_core.tools import tool
from data import OPPORTUNITIES

DATA_DIR = Path("data")
DRAFT_FILE = DATA_DIR / "application_drafts.json"


def read_drafts():
    DATA_DIR.mkdir(exist_ok=True)
    if not DRAFT_FILE.exists():
        return []
    try:
        return json.loads(DRAFT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_drafts(drafts):
    DATA_DIR.mkdir(exist_ok=True)
    DRAFT_FILE.write_text(
        json.dumps(drafts, indent=2),
        encoding="utf-8",
    )


@tool
def search_opportunities(skill_keywords: str, preferred_location: str = "Any") -> list:
    """Search internship listings by comma-separated skills and preferred location."""
    requested = {
        word.strip().lower()
        for word in skill_keywords.split(",")
        if word.strip()
    }
    location_pref = (preferred_location or "Any").strip().lower()

    matches = []
    for item in OPPORTUNITIES:
        available = {skill.lower() for skill in item["skills"]}
        skill_match = not requested or bool(requested.intersection(available))
        location_match = (
            location_pref == "any"
            or location_pref in item["location"].lower()
            or item["mode"].lower() == "remote"
        )
        if skill_match and location_match:
            matches.append(item)

    return matches


@tool
def check_eligibility(opportunity_id: str, student_year: int, student_skills: str) -> dict:
    """Check the minimum academic year and skill overlap for an internship ID."""
    opportunity = next(
        (item for item in OPPORTUNITIES if item["id"] == opportunity_id.strip().upper()),
        None,
    )
    if opportunity is None:
        return {"eligible": False, "reason": "Opportunity ID not found."}

    skills = {
        skill.strip().lower()
        for skill in student_skills.split(",")
        if skill.strip()
    }
    required = {skill.lower() for skill in opportunity["skills"]}
    matched = sorted(skills.intersection(required))
    missing = sorted(required.difference(skills))
    year_ok = int(student_year) >= opportunity["min_year"]
    skills_ok = len(matched) >= 1

    return {
        "eligible": year_ok and skills_ok,
        "year_requirement_met": year_ok,
        "matched_skills": matched,
        "missing_skills": missing,
        "reason": (
            "Meets the sample rules."
            if year_ok and skills_ok
            else "Does not meet the sample year or skill rules."
        ),
    }


@tool
def estimate_monthly_stipend(opportunity_id: str) -> dict:
    """Return the listed monthly stipend range in INR for an internship ID."""
    opportunity = next(
        (item for item in OPPORTUNITIES if item["id"] == opportunity_id.strip().upper()),
        None,
    )
    if opportunity is None:
        return {"error": "Opportunity ID not found."}

    return {
        "currency": "INR",
        "minimum_per_month": opportunity["stipend_min"],
        "maximum_per_month": opportunity["stipend_max"],
        "note": "Sample listing range, not a guaranteed offer.",
    }


@tool
def save_application_draft(
    student_name: str,
    student_email: str,
    opportunity_id: str,
    motivation: str,
) -> dict:
    """Save an application draft locally for human review; do not submit it."""
    if "@" not in student_email or "." not in student_email:
        return {"saved": False, "reason": "Please provide a valid email address."}

    opportunity = next(
        (item for item in OPPORTUNITIES if item["id"] == opportunity_id.strip().upper()),
        None,
    )
    if opportunity is None:
        return {"saved": False, "reason": "Opportunity ID not found."}

    drafts = read_drafts()
    draft = {
        "student_name": student_name.strip(),
        "student_email": student_email.strip(),
        "opportunity_id": opportunity_id.strip().upper(),
        "company": opportunity["company"],
        "role": opportunity["role"],
        "motivation": motivation.strip(),
        "status": "DRAFT - HUMAN REVIEW REQUIRED",
    }
    drafts.append(draft)
    write_drafts(drafts)

    return {
        "saved": True,
        "status": draft["status"],
        "message": "Draft saved locally. It has NOT been submitted.",
    }


@tool
def list_application_drafts() -> list:
    """List locally saved application drafts."""
    return read_drafts()


ALL_TOOLS = [
    search_opportunities,
    check_eligibility,
    estimate_monthly_stipend,
    save_application_draft,
    list_application_drafts,
]