import copy
import json
from pathlib import Path

import streamlit as st

import casp_agent_scaffold as ce


# ----------------------------
# Helpers
# ----------------------------

def load_source_data(source_name: str):
    if source_name == "Sample data":
        return json.loads(ce.EXAMPLE_PATH.read_text(encoding="utf-8"))
    return ce.load_schema()


def parse_multiline(text: str):
    return [line.strip() for line in text.splitlines() if line.strip()]


def to_multiline(items):
    return "\n".join(items) if items else ""


def get_person_defaults(items, idx):
    if idx < len(items):
        return items[idx]
    return {
        "Role": "",
        "Rank": "",
        "Name": "",
        "Qualification": "",
        "Remarks": "",
    }


def ensure_data_shape(data):
    """Make sure all expected keys exist so the app never crashes."""
    data.setdefault("Unit", {})
    data["Unit"].setdefault("Appointment", "")
    data["Unit"].setdefault("Name", "")
    data["Unit"].setdefault("Address", {})
    data["Unit"]["Address"].setdefault("Line1", "")
    data["Unit"]["Address"].setdefault("Line2", "")
    data["Unit"]["Address"].setdefault("County", "")
    data["Unit"]["Address"].setdefault("Postcode", "")
    data["Unit"].setdefault("Phone", "")
    data["Unit"].setdefault("Email", "")
    data["Unit"].setdefault("DistributionReference", "distribution")

    data.setdefault("Activity", {})
    for k in [
        "Code", "Name", "Type", "SubUnit", "PrimaryLocation",
        "StartDate", "EndDate", "DocumentDate", "Purpose",
        "CFAVCount", "CadetCount", "ConsultedWith"
    ]:
        data["Activity"].setdefault(k, "")

    data.setdefault("RiskAssessments", {})
    data["RiskAssessments"].setdefault("CoreTrainingAtRFCAorDIO", {})
    data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"].setdefault("Title", "")
    data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"].setdefault("Date", "")
    data["RiskAssessments"].setdefault("AF5010C", {})
    data["RiskAssessments"]["AF5010C"].setdefault("Reference", "")
    data["RiskAssessments"]["AF5010C"].setdefault("Date", "")

    data.setdefault("Authority", {})
    data["Authority"].setdefault("AtCApprover", "")

    data.setdefault("Documents", [])
    data.setdefault("Aims", ce.DEFAULT_AIMS.copy())

    data.setdefault("Staff", [])
    data.setdefault("SubActivityOwners", [])
    data.setdefault("FirstAiders", [])
    data.setdefault("Drivers", [])

    data.setdefault("Locations", [])
    data.setdefault("MedicalLocations", [])

    data.setdefault("Distribution", {})

    data["Distribution"].setdefault("Distribution", [])
    data["Distribution"].setdefault("Info", [])


    data.setdefault("Signatory", {})
    data["Signatory"].setdefault("Name", "")
    data["Signatory"].setdefault("Rank", "")
    data["Signatory"].setdefault("Appointment", "")

    data.setdefault("Annexes", [])

    return data


def rebuild_medical_locations(locations, existing_medical_locations):
    """
    Ensure there is one MedicalLocations entry for each location by name,
    carrying forward existing values where names match.
    """
    existing_map = {m.get("Name", ""): m for m in existing_medical_locations}
    rebuilt = []

    for loc in locations:
        name = loc.get("Name", "")
        current = existing_map.get(name, {})

        rebuilt.append({
            "Name": name,
            "What3Words": current.get("What3Words", ""),
            "SafetyVehicle": {
                "Location": current.get("SafetyVehicle", {}).get("Location", ""),
                "Remarks": current.get("SafetyVehicle", {}).get("Remarks", ""),
            },
            "UrgentCare": {
                "Location": current.get("UrgentCare", {}).get("Location", ""),
                "Remarks": current.get("UrgentCare", {}).get("Remarks", ""),
            },
            "AandE": {
                "Location": current.get("AandE", {}).get("Location", ""),
                "Remarks": current.get("AandE", {}).get("Remarks", ""),
            },
            "AmbulanceRV": {
                "Location": current.get("AmbulanceRV", {}).get("Location", ""),
                "Remarks": current.get("AmbulanceRV", {}).get("Remarks", ""),
            },
        })

    return rebuilt


# ----------------------------
# App state initialisation
# ----------------------------

st.set_page_config(page_title="CASP Generator", layout="wide")
st.title("CASP Generator")

if "source_name" not in st.session_state:
    st.session_state.source_name = "Schema defaults"

if "base_data" not in st.session_state:
    st.session_state.base_data = ensure_data_shape(load_source_data("Schema defaults"))


# ----------------------------
# Load source data controls
# ----------------------------

st.subheader("Starting data")

source_name = st.radio(
    "Choose starting data",
    ["Schema defaults", "Sample data"],
    index=0 if st.session_state.source_name == "Schema defaults" else 1,
    horizontal=True,
)

col_load_1, col_load_2 = st.columns([1, 3])

with col_load_1:
    if st.button("Load selected source into form"):
        st.session_state.source_name = source_name
        st.session_state.base_data = ensure_data_shape(load_source_data(source_name))
        st.rerun()

with col_load_2:
    st.write(
        "Use **Schema defaults** to start with your normal template values, "
        "or **Sample data** to generate a populated test document."
    )

data = copy.deepcopy(st.session_state.base_data)
data = ensure_data_shape(data)


# ----------------------------
# Unit
# ----------------------------

st.header("Unit")

col1, col2 = st.columns(2)

with col1:
    data["Unit"]["Appointment"] = st.text_input(
        "Appointment",
        value=data["Unit"]["Appointment"],
        key="unit_appointment",
    )
    data["Unit"]["Name"] = st.text_input(
        "Unit Name",
        value=data["Unit"]["Name"],
        key="unit_name",
    )
    data["Unit"]["Phone"] = st.text_input(
        "Phone",
        value=data["Unit"]["Phone"],
        key="unit_phone",
    )
    data["Unit"]["Email"] = st.text_input(
        "Email",
        value=data["Unit"]["Email"],
        key="unit_email",
    )

with col2:
    data["Unit"]["Address"]["Line1"] = st.text_input(
        "Address Line 1",
        value=data["Unit"]["Address"]["Line1"],
        key="unit_addr1",
    )
    data["Unit"]["Address"]["Line2"] = st.text_input(
        "Address Line 2",
        value=data["Unit"]["Address"]["Line2"],
        key="unit_addr2",
    )
    data["Unit"]["Address"]["County"] = st.text_input(
        "County",
        value=data["Unit"]["Address"]["County"],
        key="unit_county",
    )
    data["Unit"]["Address"]["Postcode"] = st.text_input(
        "Postcode",
        value=data["Unit"]["Address"]["Postcode"],
        key="unit_postcode",
    )


# ----------------------------
# Activity
# ----------------------------

st.header("Activity")

col1, col2 = st.columns(2)

with col1:
    data["Activity"]["Code"] = st.text_input("Code", value=data["Activity"]["Code"], key="act_code")
    data["Activity"]["Name"] = st.text_input("Name", value=data["Activity"]["Name"], key="act_name")
    data["Activity"]["Type"] = st.text_input("Type", value=data["Activity"]["Type"], key="act_type")
    data["Activity"]["SubUnit"] = st.text_input("Sub-unit", value=data["Activity"]["SubUnit"], key="act_subunit")
    data["Activity"]["PrimaryLocation"] = st.text_input(
        "Primary Location",
        value=data["Activity"]["PrimaryLocation"],
        key="act_primary_location",
    )
    data["Activity"]["ConsultedWith"] = st.text_input(
        "Consulted With",
        value=data["Activity"]["ConsultedWith"],
        key="act_consulted",
    )

with col2:
    data["Activity"]["StartDate"] = st.text_input("Start Date/Time", value=data["Activity"]["StartDate"], key="act_start")
    data["Activity"]["EndDate"] = st.text_input("End Date/Time", value=data["Activity"]["EndDate"], key="act_end")
    data["Activity"]["DocumentDate"] = st.text_input(
        "Document Date",
        value=data["Activity"]["DocumentDate"],
        key="act_doc_date",
    )
    data["Activity"]["CFAVCount"] = st.text_input(
        "Approx CFAV Count",
        value=str(data["Activity"]["CFAVCount"]),
        key="act_cfav",
    )
    data["Activity"]["CadetCount"] = st.text_input(
        "Approx Cadet Count",
        value=str(data["Activity"]["CadetCount"]),
        key="act_cadet",
    )

data["Activity"]["Purpose"] = st.text_area(
    "Purpose / Reason for activity",
    value=data["Activity"]["Purpose"],
    key="act_purpose",
    height=120,
)


# ----------------------------
# Risk Assessments and Authority
# ----------------------------

st.header("Risk Assessments and Authority")

col1, col2 = st.columns(2)

with col1:
    data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"]["Title"] = st.text_input(
        "Core Training RA Title",
        value=data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"]["Title"],
        key="ra_core_title",
    )
    data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"]["Date"] = st.text_input(
        "Core Training RA Date",
        value=data["RiskAssessments"]["CoreTrainingAtRFCAorDIO"]["Date"],
        key="ra_core_date",
    )

with col2:
    data["RiskAssessments"]["AF5010C"]["Reference"] = st.text_input(
        "AF5010C Reference",
        value=data["RiskAssessments"]["AF5010C"]["Reference"],
        key="ra_af_ref",
    )
    data["RiskAssessments"]["AF5010C"]["Date"] = st.text_input(
        "AF5010C Date",
        value=data["RiskAssessments"]["AF5010C"]["Date"],
        key="ra_af_date",
    )

data["Authority"]["AtCApprover"] = st.text_input(
    "Authority to Conduct Approver",
    value=data["Authority"]["AtCApprover"],
    key="authority_atc",
)


# ----------------------------
# Documents and Aims
# ----------------------------

st.header("Documents and Aims")

col1, col2 = st.columns(2)

with col1:
    documents_text = st.text_area(
        "Supporting Documents (one per line)",
        value=to_multiline(data["Documents"]),
        key="documents_text",
        height=150,
    )
    data["Documents"] = parse_multiline(documents_text)

with col2:
    aims_text = st.text_area(
        "Aims (one per line)",
        value=to_multiline(data["Aims"]),
        key="aims_text",
        height=150,
    )
    data["Aims"] = parse_multiline(aims_text)


# ----------------------------
# Staff - core roles
# ----------------------------

st.header("Core Staff")

core_roles = [
    "Senior Activity Owner",
    "Activity Owner",
    "Activity Planner",
    "Personnel Owner",
]

existing_staff_by_role = {entry.get("Role", ""): entry for entry in data["Staff"]}
updated_staff = []

for role in core_roles:
    default_person = existing_staff_by_role.get(role, {
        "Role": role,
        "Rank": "",
        "Name": "",
        "Qualification": "",
        "Remarks": "",
    })

    st.subheader(role)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rank = st.text_input(f"{role} - Rank", value=default_person.get("Rank", ""), key=f"{role}_rank")
    with col2:
        name = st.text_input(f"{role} - Name", value=default_person.get("Name", ""), key=f"{role}_name")
    with col3:
        qualification = st.text_input(
            f"{role} - Qualification",
            value=default_person.get("Qualification", ""),
            key=f"{role}_qualification",
        )
    with col4:
        remarks = st.text_input(
            f"{role} - Remarks",
            value=default_person.get("Remarks", ""),
            key=f"{role}_remarks",
        )

    updated_staff.append({
        "Role": role,
        "Rank": rank,
        "Name": name,
        "Qualification": qualification,
        "Remarks": remarks,
    })

data["Staff"] = updated_staff


# ----------------------------
# Repeating people sections
# ----------------------------

def edit_people_section(section_title, data_key, role_name, minimum_count=0):
    st.header(section_title)

    existing_items = data.get(data_key, [])
    default_count = max(minimum_count, len(existing_items))

    count = st.number_input(
        f"How many {section_title}?",
        min_value=minimum_count,
        value=default_count,
        step=1,
        key=f"{data_key}_count",
    )

    updated_items = []

    for idx in range(count):
        person_default = get_person_defaults(existing_items, idx)
        st.subheader(f"{role_name} {idx + 1}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            rank = st.text_input(
                f"{role_name} {idx + 1} - Rank",
                value=person_default.get("Rank", ""),
                key=f"{data_key}_{idx}_rank",
            )
        with col2:
            name = st.text_input(
                f"{role_name} {idx + 1} - Name",
                value=person_default.get("Name", ""),
                key=f"{data_key}_{idx}_name",
            )
        with col3:
            qualification = st.text_input(
                f"{role_name} {idx + 1} - Qualification",
                value=person_default.get("Qualification", ""),
                key=f"{data_key}_{idx}_qualification",
            )
        with col4:
            remarks = st.text_input(
                f"{role_name} {idx + 1} - Remarks",
                value=person_default.get("Remarks", ""),
                key=f"{data_key}_{idx}_remarks",
            )

        updated_items.append({
            "Role": role_name,
            "Rank": rank,
            "Name": name,
            "Qualification": qualification,
            "Remarks": remarks,
        })

    data[data_key] = updated_items


edit_people_section("Sub-Activity Owners", "SubActivityOwners", "Sub-Activity Owner", minimum_count=0)
edit_people_section("First Aiders", "FirstAiders", "First Aider", minimum_count=1)
edit_people_section("Drivers", "Drivers", "Driver", minimum_count=1)


# ----------------------------
# Locations
# ----------------------------

st.header("Locations")

existing_locations = data["Locations"]
locations_count = st.number_input(
    "How many Locations?",
    min_value=0,
    value=len(existing_locations),
    step=1,
    key="locations_count",
)

updated_locations = []

for idx in range(locations_count):
    default_loc = existing_locations[idx] if idx < len(existing_locations) else {"Name": "", "RiskControls": ""}
    st.subheader(f"Location {idx + 1}")

    col1, col2 = st.columns(2)
    with col1:
        loc_name = st.text_input(
            f"Location {idx + 1} - Name",
            value=default_loc.get("Name", ""),
            key=f"location_{idx}_name",
        )
    with col2:
        loc_controls = st.text_input(
            f"Location {idx + 1} - Risk Controls",
            value=default_loc.get("RiskControls", ""),
            key=f"location_{idx}_controls",
        )

    updated_locations.append({
        "Name": loc_name,
        "RiskControls": loc_controls,
    })

data["Locations"] = updated_locations


# ----------------------------
# Medical Locations
# ----------------------------

st.header("Medical Locations")

data["MedicalLocations"] = rebuild_medical_locations(data["Locations"], data["MedicalLocations"])

updated_medical_locations = []

for idx, med in enumerate(data["MedicalLocations"]):
    st.subheader(f"Medical Details for {med['Name']}")

    med["What3Words"] = st.text_input(
        f"{med['Name']} - What3Words",
        value=med.get("What3Words", ""),
        key=f"med_{idx}_w3w",
    )

    st.markdown("**Safety Vehicle**")
    col1, col2 = st.columns(2)
    with col1:
        med["SafetyVehicle"]["Location"] = st.text_input(
            f"{med['Name']} - Safety Vehicle Location",
            value=med["SafetyVehicle"].get("Location", ""),
            key=f"med_{idx}_sv_loc",
        )
    with col2:
        med["SafetyVehicle"]["Remarks"] = st.text_input(
            f"{med['Name']} - Safety Vehicle Remarks",
            value=med["SafetyVehicle"].get("Remarks", ""),
            key=f"med_{idx}_sv_rem",
        )

    st.markdown("**Urgent Care / Walk-in**")
    col1, col2 = st.columns(2)
    with col1:
        med["UrgentCare"]["Location"] = st.text_input(
            f"{med['Name']} - Urgent Care Location",
            value=med["UrgentCare"].get("Location", ""),
            key=f"med_{idx}_uc_loc",
        )
    with col2:
        med["UrgentCare"]["Remarks"] = st.text_input(
            f"{med['Name']} - Urgent Care Remarks",
            value=med["UrgentCare"].get("Remarks", ""),
            key=f"med_{idx}_uc_rem",
        )

    st.markdown("**A&E**")
    col1, col2 = st.columns(2)
    with col1:
        med["AandE"]["Location"] = st.text_input(
            f"{med['Name']} - A&E Location",
            value=med["AandE"].get("Location", ""),
            key=f"med_{idx}_ae_loc",
        )
    with col2:
        med["AandE"]["Remarks"] = st.text_input(
            f"{med['Name']} - A&E Remarks",
            value=med["AandE"].get("Remarks", ""),
            key=f"med_{idx}_ae_rem",
        )

    st.markdown("**Ambulance RV**")
    col1, col2 = st.columns(2)
    with col1:
        med["AmbulanceRV"]["Location"] = st.text_input(
            f"{med['Name']} - Ambulance RV Location",
            value=med["AmbulanceRV"].get("Location", ""),
            key=f"med_{idx}_arv_loc",
        )
    with col2:
        med["AmbulanceRV"]["Remarks"] = st.text_input(
            f"{med['Name']} - Ambulance RV Remarks",
            value=med["AmbulanceRV"].get("Remarks", ""),
            key=f"med_{idx}_arv_rem",
        )

    updated_medical_locations.append(med)

data["MedicalLocations"] = updated_medical_locations


# ----------------------------
# Distribution
# ----------------------------

st.header("Distribution")


col1, col2 = st.columns(2)

with col1:
    distribution_text = st.text_area(
        "Distribution (one per line)",
        value=to_multiline(data["Distribution"].get("Distribution", [])),
        key="dist_distribution",
        height=150,
    )
    data["Distribution"]["Distribution"] = parse_multiline(distribution_text)

with col2:
    info_text = st.text_area(
        "Info (one per line)",
        value=to_multiline(data["Distribution"].get("Info", [])),
        key="dist_info",
        height=150,
    )


    data["Distribution"]["Info"] = parse_multiline(info_text)


# ----------------------------
# Signatory
# ----------------------------

st.header("Signatory")

col1, col2, col3 = st.columns(3)
with col1:
    data["Signatory"]["Name"] = st.text_input(
        "Signatory Name",
        value=data["Signatory"]["Name"],
        key="sign_name",
    )
with col2:
    data["Signatory"]["Rank"] = st.text_input(
        "Signatory Rank",
        value=data["Signatory"]["Rank"],
        key="sign_rank",
    )
with col3:
    data["Signatory"]["Appointment"] = st.text_input(
        "Signatory Appointment",
        value=data["Signatory"]["Appointment"],
        key="sign_app",
    )


# ----------------------------
# Annexes
# ----------------------------

st.header("Annexes")

annexes_text = st.text_area(
    "Annexes (one per line)",
    value=to_multiline(data["Annexes"]),
    key="annexes_text",
    height=150,
)
data["Annexes"] = parse_multiline(annexes_text)


# ----------------------------
# Output controls
# ----------------------------

st.header("Generate Output")

col1, col2 = st.columns(2)
with col1:
    json_output_path = st.text_input(
        "JSON output path",
        value=str(ce.BASE_DIR / "casp_session.json"),
        key="json_out",
    )
with col2:
    docx_output_path = st.text_input(
        "DOCX output path",
        value=str(ce.DEFAULT_OUTPUT),
        key="docx_out",
    )

generate = st.button("Generate CASP Document")

if generate:
    json_output = Path(json_output_path).expanduser().resolve()
    ce.save_json(json_output, data)

    docx_output = Path(docx_output_path).expanduser().resolve()
    ce.render_docx(data, docx_output)

    st.success(f"Generated CASP DOCX: {docx_output}")

    with open(docx_output, "rb") as f:
        st.download_button(
            "Download CASP DOCX",
            f,
            file_name=docx_output.name,
        )