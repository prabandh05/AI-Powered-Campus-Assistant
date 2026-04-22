"""
Pre-process the raw scraped campus data to remove navigation noise,
duplicate lines, and boilerplate before feeding to the RAG engine.
"""
import re
from pathlib import Path

RAW_PATH = "data/campus_knowledge.txt"
CLEAN_PATH = "data/campus_clean.txt"

# Lines that appear in navigation menus — remove them
NAV_NOISE = {
    "Faculty", "Alumni", "Careers", "Home", "About", "About DSCE", "History",
    "Leadership", "Chairman Message", "Vice Chairman Message", "Secretary Message",
    "Principal Message", "Governing Body", "Meeting Proceedings", "Statutory Committee",
    "Committees and Members", "Administrative Offices", "Institute Industry Interaction Cell",
    "E-Governance", "INTERNAL QUALITY ASSURANCE CELL (IQAC)", "PEO, PSO & CO's",
    "Minutes of Meeting", "Annual Reports (Finance)", "Academics", "UG Programs",
    "PG Programs", "Basic science and humanities", "Physics", "Chemistry",
    "Mathematics", "Humanities", "Admissions", "Brochure", "Course & Eligibility",
    "Fee Structure", "Pay Fee", "Examination", "Placements", "Placement Training",
    "Campus Hiring", "Testimonials", "Placements Contact", "Research", "About R & D",
    "Dean R&D Desk", "R & D Committee", "Research Center Approval", "Research Centers",
    "Various Funded Projects", "List of Ph.D Awarded", "Core Research Faculty",
    "Journal Publications", "Patents Filed", "IRINS Portal", "Documents",
    "Academic Council", "Organogram", "Accreditation & Other approvals", "NIRF",
    "NISP", "Accreditation by NAAC", "Accreditation by NBA", "IIC",
    "Govt. of Karnataka Approval for Autonomy", "VTU Autonomous Approval Letter",
    "UGC Approval Letter", "AICTE Extension of Approval",
    "ISO Certificate Quality Management System", "ISO Certificate Environmental Management System",
    "Green Policy & Audit", "ISO Certificate Food Safety Management System",
    "Approval Under UGC Section 2(f)", "VTU Affiliation", "Rules and Regulations",
    "Prevention and Prohibition of Ragging", "AICTE Mandatory Disclosure",
    "Code Of Conduct", "Service Rules", "Policies", "Institutional Distinctiveness",
    "Student list", "UG", "First Year", "Second Year", "Third Year", "Fourth Year", "PG",
    "Professional Bodies", "Innovation", "IEDC", "DERBI", "STC", "CIL",
    "KSTA Institutional Membership", "Skill Labs", "CS-IOT", "Mechanical", "CS-CYBER",
    "FACILITIES", "Hospital", "Library", "Kindle E - book", "National Archives of India",
    "Hostel", "Data Center", "Sports & Fitness", "Counselling Center",
    "Yoga & Meditation", "Center for Performing Arts", "Scholarships", "SSP", "NSP",
    "Life Skills", "Activities", "Student Activities", "Dean Student Affairs Desk",
    "Dean's Profile", "Curricular Activities", "Graduation Day", "DSCE Clubs",
    "Photography club", "Nature club", "Aeronautical Society of India", "Team Arcis",
    "National Service Scheme (NSS)", "Social Responsibility Cell", "DSCE Newsletters",
    "Blog", "Media Presence", "First Year  Coordinator's Desk", "Student Handbook",
    "Induction", "Syllabus 2025-26", "Syllabus 2022-23", "Students List",
    "Class Time Table", "Exam Time Tables", "Senior Student Connect", "Hostels",
    "Calendar of Events", "Notifications", "Activity Points", "FAQs", "ERP Login",
    "Contact Us", "Menu", "Admission Enquiry", "Hide Main content block",
    "read more", ">>", ">", "»", "Share:", "About Us", "DSCE History",
    "Photo Album", "Useful Links", "Campus Life", "Contact Info",
    "Quick Links", "ARIIA",
}

# Patterns to strip
FOOTER_RE = re.compile(
    r"An Autonomous Institute Affiliated to VTU.*?(?=\n[A-Z])",
    re.DOTALL
)


def clean_campus_data():
    raw = Path(RAW_PATH).read_text(encoding="utf-8")
    lines = raw.splitlines()

    cleaned = []
    seen = set()
    prev_line = ""

    for line in lines:
        line = line.strip()

        # Skip empty
        if not line:
            continue

        # Skip nav items
        if line in NAV_NOISE:
            continue

        # Skip short lines that are probably menu fragments
        if len(line) < 10 and not any(c.isdigit() for c in line):
            continue

        # Skip footer boilerplate
        if "Mahatma Gandhi Vidya Peetha Trust" in line:
            continue
        if "Autonomous Institute Affiliated to VTU" in line:
            continue
        if "Accredited by NBA & NAAC" in line:
            continue
        if "This email address is being protected from spambots" in line:
            continue
        if line.startswith("CET Code:") or line.startswith("Comed-K Code:"):
            continue
        if line.startswith("PGCET"):
            continue
        if line.startswith("M.Tech:"):
            continue

        # Skip repeated URLs
        if line.startswith("http") and len(line) > 30:
            continue

        # Deduplicate exact lines
        if line in seen:
            continue

        # Skip lines that are just department codes like "E007 |" 
        if re.match(r'^[A-Z]\d{3}\s*\|?$', line):
            continue
        if re.match(r'^[A-Z]\d{3}$', line):
            continue

        # Skip very short "code" lines
        if line in ("'A'", "grade."):
            continue

        seen.add(line)
        cleaned.append(line)
        prev_line = line

    output = "\n".join(cleaned)
    Path(CLEAN_PATH).write_text(output, encoding="utf-8")

    raw_lines = len(lines)
    clean_lines = len(cleaned)
    print(f"Cleaning complete:")
    print(f"  Raw lines:   {raw_lines}")
    print(f"  Clean lines: {clean_lines}")
    print(f"  Removed:     {raw_lines - clean_lines} noise lines ({100*(raw_lines-clean_lines)//raw_lines}%)")
    print(f"  Saved to:    {CLEAN_PATH}")


if __name__ == "__main__":
    clean_campus_data()
