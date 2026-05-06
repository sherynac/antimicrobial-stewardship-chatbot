import os
import re
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD, OWL

# ------------------ Setup ------------------
g = Graph()
EX = Namespace("http://example.org/ontology#")
g.bind(":", EX)
g.bind("xsd", XSD)

# ------------------ Paths ------------------
base_path = os.path.join(os.path.dirname(__file__), "data")
output_path = os.path.join(os.path.dirname(__file__), "..", "FinalOntology.ttl")
csv_files = {
    "Antibiotic": os.path.join(base_path, "Antibiotic.csv"),
    "Presentation": os.path.join(base_path, "Presentation.csv"),
    "Indication": os.path.join(base_path, "Indication.csv"),
    "Warning": os.path.join(base_path, "Warning.csv"),
    "SideEffect": os.path.join(base_path, "SideEffect.csv"),
    "StewardshipPrinciple": os.path.join(base_path, "StewardshipPrinciple.csv"),
    "Substance": os.path.join(base_path, "Substance.csv"),
    "Interaction": os.path.join(base_path, "Interaction.csv"),
    "Reference": os.path.join(base_path, "Reference.csv"),
    "Severity": os.path.join(base_path, "Severity.csv"),
}

# ------------------ Helper Functions ------------------
def clean_string(val):
    """Escape characters that would break TTL parsing (for output only)."""
    if val is None:
        return ""
    s = str(val)
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n').replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return s.strip()

def split_multivalue(val):
    """Split multi-value cells (newline-separated) and clean."""
    if pd.isna(val) or str(val).strip().lower() == "nan":
        return []
    return [v.strip().strip('"').strip("'") for v in str(val).replace("\r", "").split("\n") if v.strip()]

def make_uri_id(id_str):
    """Create a safe URI local name from an ID."""
    if not id_str or str(id_str).strip().lower() == "nan":
        return None
    id_str = str(id_str).strip().replace("\n", "").replace("\r", "").replace('"', '').replace("'", "")
    return id_str

def make_safe_uri_label(label_str):
    """Create a safe URI local name from a label (replace spaces with underscores)."""
    if not label_str or str(label_str).strip().lower() == "nan":
        return None
    label_str = str(label_str).strip()
    label_str = re.sub(r"[^\w\-]", "_", label_str)
    return label_str

def sanitize_ttl_name(name):
    """Create a safe URI local name from a label (CamelCase)."""
    if not name or str(name).strip().lower() == "nan":
        return None
    name = re.sub(r"[^a-zA-Z0-9\s\(\)]", "", str(name))
    name = re.sub(r"\(", " ", name)
    name = re.sub(r"\)", "", name)
    words = name.split()
    result = ''
    for word in words:
        if word:
            if len(word) > 1:
                result += word[0].upper() + word[1:]
            else:
                result += word.upper()
    return result

def safe_str(val):
    """Safely convert value to string, handling NaN/None."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()

def severity_to_class(severity_str):
    """Map severity string to ontology class URI using dynamic naming."""
    if not severity_str:
        return None
    return sanitize_ttl_name(severity_str)

def condition_type_to_class(condition_type):
    """Map condition type to ontology class URI."""
    ct = condition_type.strip().lower()
    if ct == "respiratory":
        return "RespiratoryDisease"
    elif ct == "urinary":
        return "UrinaryDisease"
    return None

def presentation_to_class(presentation_str):
    """Map presentation string to ontology class by converting CSV value to URI-safe name."""
    if not presentation_str:
        return None
    return sanitize_ttl_name(presentation_str)

def format_presentation_label(brand_name, dosage, packing_type):
    """Format presentation label: '<brand> <dosage> <form>' using CSV values directly."""
    parts = []
    if brand_name:
        parts.append(brand_name)
    if dosage and dosage != "Not Specified":
        parts.append(dosage)
    if packing_type:
        parts.append(packing_type)
    return " ".join(parts)

def warning_type_to_class(type_str, headline="", description=""):
    """Map CSV Warning Type column directly to ontology class."""
    type_map = {
        "Pregnancy & Lactation": "PregnancyAndLactation",
        "Age Restriction": "AgeRestriction",
        "Overdosage": "Overdosage",
        "Contraindication": "Contraindication",
        "Patient Condition": "PatientCondition"
    }
    return type_map.get(type_str.strip(), "PatientCondition")

def side_effect_to_class(se_name):
    """Map side effect name to ontology class URI using dynamic naming."""
    if not se_name:
        return "SideEffect"
    name = se_name.strip()
    return sanitize_ttl_name(name)

def stewardship_type_to_class(type_str):
    """Map stewardship principle type to ontology class URI."""
    t = type_str.strip().lower()
    if "storage" in t:
        return "Storage"
    elif "administration" in t or "preparation" in t:
        return "AdministrationAndAdherence"
    elif "food" in t or "timing" in t:
        return "FoodAndTiming"
    elif "adherence" in t:
        return "AdministrationAndAdherence"
    elif "monitoring" in t:
        return "TherapeuticUseAndMonitoring"
    elif "proper use" in t:
        return "AdministrationAndAdherence"
    return "StewardshipPrinciple"

# ------------------ Load DataFrames ------------------
dfs = {}
for name, path in csv_files.items():
    try:
        dfs[name] = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        print(f"Warning: {path} not found")
        dfs[name] = pd.DataFrame()

# Build a set of indication condition names to avoid duplicate SideEffect subclasses
indication_condition_names = set()
if "Indication" in dfs and not dfs["Indication"].empty:
    for _, row in dfs["Indication"].iterrows():
        condition_name = safe_str(row.get("Condition Name"))
        if condition_name:
            indication_condition_names.add(condition_name.strip().lower())

# ------------------ Create Individuals & Relationships ------------------
created_uris = set()
def add_individual(uri, rdf_type, label=None):
    """Add an individual if not already created."""
    if uri not in created_uris:
        g.add((uri, RDF.type, rdf_type))
        created_uris.add(uri)
    if label:
        g.add((uri, RDFS.label, Literal(str(label))))

def add_literal(uri, prop, value):
    """Add a literal property if value is valid."""
    if value and str(value).strip().lower() not in ["nan", "none", ""]:
        g.add((uri, prop, Literal(str(value).strip())))

# ========== REFERENCES ==========
for _, row in dfs["Reference"].iterrows():
    ref_id = make_uri_id(row.get("ReferenceID"))
    if not ref_id:
        continue
    uri = URIRef(EX[ref_id])
    add_individual(uri, EX.Reference, ref_id)
    add_literal(uri, EX.hasReferenceTitle, row.get("Title"))
    add_literal(uri, EX.hasAuthor, row.get("Author"))
    try:
        year = str(row.get("Date", "")).strip()
        if year and year.isdigit():
            g.add((uri, EX.publishedIn, Literal(int(year), datatype=XSD.integer)))
    except:
        pass
    add_literal(uri, EX.retrievedFrom, row.get("URL"))

# ========== ANTIBIOTICS & BRANDS & PRESENTATIONS ==========
antibiotics = {}
brands = {}
presentations = {}
for _, row in dfs["Antibiotic"].iterrows():
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    generic_name = safe_str(row.get("Generic Name"))
    brand_name = safe_str(row.get("Brand Name"))
    drug_class = safe_str(row.get("Drug Class"))
    contents = safe_str(row.get("Contents"))
    manufacturers = safe_str(row.get("Manufacturers"))
    distributors = safe_str(row.get("Distributors"))
    ref_ids = split_multivalue(row.get("Reference ID"))
    if not ab_id:
        continue
    # Create Antibiotic individual (unique by generic name)
    if generic_name not in antibiotics:
        antibiotics[generic_name] = ab_id
        ab_uri = URIRef(EX[generic_name])
        add_individual(ab_uri, EX.Antibiotic, generic_name)
        if drug_class:
            add_literal(ab_uri, EX.hasDrugClass, drug_class)
    
    # Create Brand individual (unique by brand name)
    brand_key = f"{generic_name}_{brand_name}"
    if brand_key not in brands:
        brands[brand_key] = {"name": brand_name, "antibiotic_id": generic_name, "ab_uri": URIRef(EX[generic_name])}
        brand_uri_id = make_safe_uri_label(brand_name)
        brand_uri = URIRef(EX[brand_uri_id])
        add_individual(brand_uri, EX.Brand, brand_name)
        g.add((URIRef(EX[generic_name]), EX.hasBrandName, brand_uri))
        
        # hasContents: exact CSV value as literal (moved to Brand, no URI creation)
        if contents and contents != "Not Specified":
            g.add((brand_uri, EX.hasContents, Literal(contents)))
        # hasManufacturers: exact CSV value as literal (moved to Brand, no URI creation)
        if manufacturers and manufacturers != "Not Specified":
            g.add((brand_uri, EX.hasManufacturers, Literal(manufacturers)))
        # hasDistributors: exact CSV value as literal (moved to Brand, no URI creation)
        if distributors and distributors != "Not Specified":
            g.add((brand_uri, EX.hasDistributors, Literal(distributors)))
        
        # FIX: Add hasReference to brand from Antibiotic.csv Reference ID
        for ref_id in ref_ids:
            ref_uri_id = make_uri_id(ref_id)
            if ref_uri_id:
                g.add((brand_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

# Build Antibiotic ID → Brand Names mapping
ab_id_to_brands = {}
ab_id_to_generic = {}
for _, row in dfs["Antibiotic"].iterrows():
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    brand_name = safe_str(row.get("Brand Name"))
    generic_name = safe_str(row.get("Generic Name"))
    if ab_id and brand_name:
        if ab_id not in ab_id_to_brands:
            ab_id_to_brands[ab_id] = []
        if brand_name not in ab_id_to_brands[ab_id]:
            ab_id_to_brands[ab_id].append(brand_name)
    if ab_id and generic_name:
        ab_id_to_generic[ab_id] = generic_name

# Process Presentations
if "Presentation" in dfs and not dfs["Presentation"].empty:
    for _, row in dfs["Presentation"].iterrows():
        pres_id = make_uri_id(row.get("Presentation ID"))
        ab_id = make_uri_id(row.get("Antibiotic ID"))
        packing_type = safe_str(row.get("Packing Type"))
        dosage = safe_str(row.get("Dosage"))
        unit_price = safe_str(row.get("Unit Price"))
        ref_ids = split_multivalue(row.get("Reference ID"))
        if not pres_id:
            continue
        presentation_class = presentation_to_class(packing_type) if packing_type else "Presentation"
        pres_uri = URIRef(EX[pres_id])
        
        brand_name_for_label = ""
        if ab_id and ab_id in ab_id_to_brands:
            brand_name_for_label = ab_id_to_brands[ab_id][0] if ab_id_to_brands[ab_id] else ""
        elif ab_id and ab_id in ab_id_to_generic:
            brand_name_for_label = ab_id_to_generic[ab_id]
        
        pres_label = format_presentation_label(brand_name_for_label, dosage, packing_type)
        if not pres_label:
            pres_label = pres_id
        
        add_individual(pres_uri, EX[presentation_class], pres_label)
        
        if dosage and dosage != "Not Specified":
            add_literal(pres_uri, EX.hasDosage, dosage)
        
        if unit_price:
            if unit_price == "Not Specified":
                g.add((pres_uri, EX.hasUnitPrice, Literal("Not Specified")))
            else:
                price_clean = str(unit_price).replace("₱", "").replace(",", "").strip()
                try:
                    price_float = float(price_clean)
                    g.add((pres_uri, EX.hasUnitPrice, Literal(price_float, datatype=XSD.double)))
                except:
                    if price_clean:
                        g.add((pres_uri, EX.hasUnitPrice, Literal(price_clean)))
        
        for ref_id in ref_ids:
            ref_uri_id = make_uri_id(ref_id)
            if ref_uri_id:
                g.add((pres_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
        if ab_id and ab_id in ab_id_to_brands:
            for brand_name in ab_id_to_brands[ab_id]:
                brand_uri_id = make_safe_uri_label(brand_name)
                brand_uri = URIRef(EX[brand_uri_id])
                g.add((brand_uri, EX.hasPresentation, pres_uri))

# ========== INDICATIONS ==========
indication_to_ab_ids = {}
if "Severity" in dfs and not dfs["Severity"].empty:
    for _, row in dfs["Severity"].iterrows():
        ind_id = make_uri_id(row.get("Indication ID"))
        ab_id = make_uri_id(row.get("Antibiotic ID"))
        if ind_id and ab_id:
            if ind_id not in indication_to_ab_ids:
                indication_to_ab_ids[ind_id] = []
            if ab_id not in indication_to_ab_ids[ind_id]:
                indication_to_ab_ids[ind_id].append(ab_id)
indication_to_symptoms = {}

if "Indication" in dfs and not dfs["Indication"].empty:
    for _, row in dfs["Indication"].iterrows():
        ind_id = make_uri_id(row.get("Indication ID"))
        symptoms = safe_str(row.get("Symptoms"))
        if ind_id and symptoms:
            indication_to_symptoms[ind_id] = symptoms

for _, row in dfs["Indication"].iterrows():
    ind_id = make_uri_id(row.get("Indication ID"))
    condition_name = safe_str(row.get("Condition Name"))
    condition_type = safe_str(row.get("Condition Type"))
    ref_ids = split_multivalue(row.get("Reference ID"))
    if not ind_id:
        continue
    cond_class = None
    if condition_name:
        cond_class = sanitize_ttl_name(condition_name)
    if not cond_class and condition_type:
        ct = condition_type.strip().lower()
        if ct == "respiratory":
            cond_class = "RespiratoryDisease"
        elif ct == "urinary":
            cond_class = "UrinaryDisease"
    if not cond_class:
        cond_class = "Indication"
    ind_uri = URIRef(EX[ind_id])
    add_individual(ind_uri, EX[cond_class], condition_name if condition_name else ind_id)
    if ind_id in indication_to_symptoms:
        add_literal(ind_uri, EX.hasSymptoms, indication_to_symptoms[ind_id])
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((ind_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
    # Link Brand → treats → Indication (uses Severity.csv + Antibiotic.csv mappings)
    if ind_id in indication_to_ab_ids:
        for ab_id in indication_to_ab_ids[ind_id]:
            if ab_id in ab_id_to_brands:
                for brand_name in ab_id_to_brands[ab_id]:
                    brand_uri_id = make_safe_uri_label(brand_name)
                    brand_uri = URIRef(EX[brand_uri_id])
                    g.add((brand_uri, EX.treats, ind_uri))

# ========== SEVERITY ==========
severity_individuals = set()
if "Severity" in dfs and not dfs["Severity"].empty:
    for _, row in dfs["Severity"].iterrows():
        ind_id = make_uri_id(row.get("Indication ID"))
        severity_type = safe_str(row.get("Severity Type"))
        symptoms = safe_str(row.get("Symptoms"))
        ref_ids = split_multivalue(row.get("Reference ID"))
        if not ind_id or not severity_type:
            continue
        sev_uri_id = sanitize_ttl_name(severity_type)
        if not sev_uri_id:
            continue
        sev_uri = URIRef(EX[sev_uri_id])
        if sev_uri_id not in severity_individuals:
            severity_individuals.add(sev_uri_id)
            add_individual(sev_uri, EX.Severity, severity_type)
        ind_uri = URIRef(EX[ind_id])
        g.add((ind_uri, EX.hasSeverityType, sev_uri))
        if symptoms and symptoms != "Not Specified":
            add_literal(ind_uri, EX.hasSymptoms, symptoms)
        for ref_id in ref_ids:
            ref_uri_id = make_uri_id(ref_id)
            if ref_uri_id:
                g.add((ind_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

# ========== WARNINGS ==========
for _, row in dfs["Warning"].iterrows():
    w_id = make_uri_id(row.get("Warning ID"))
    brand_name = None
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    
    if ab_id and ab_id in ab_id_to_brands:
        brand_name = ab_id_to_brands[ab_id][0]
    
    type_str = safe_str(row.get("Warning Type"))
    headline = safe_str(row.get("Headline"))
    description = safe_str(row.get("Warning Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))
    
    if not w_id:
        continue
    
    # Fixed: pass headline + description to warning_type_to_class
    w_class = warning_type_to_class(type_str, headline, description)
    w_uri = URIRef(EX[w_id])
    # Optional: use headline as label instead of ID
    label = headline if headline else w_id
    add_individual(w_uri, EX[w_class], label)
    
    if headline:
        add_literal(w_uri, EX.hasWarningHeadline, headline)
    if description:
        add_literal(w_uri, EX.hasWarningText, description)
    
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((w_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
    
    if brand_name:
        brand_uri_id = make_safe_uri_label(brand_name)
        brand_uri = URIRef(EX[brand_uri_id])
        g.add((brand_uri, EX.hasWarning, w_uri))

# ========== SIDE EFFECTS ==========
pattern_individuals = set()
for _, row in dfs["SideEffect"].iterrows():
    se_id = make_uri_id(row.get("SideEffect ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    se_name = safe_str(row.get("SE Name"))
    pattern = safe_str(row.get("Pattern"))
    description = safe_str(row.get("SE Description "))
    ref_ids = split_multivalue(row.get("Reference ID"))
    if not se_id:
        continue
    se_class = side_effect_to_class(se_name) if se_name else "SideEffect"
    se_uri = URIRef(EX[se_id])
    add_individual(se_uri, EX[se_class], se_name if se_name else se_id)
    if description and description != "Not Specified":
        add_literal(se_uri, EX.hasSideEffectDescription, description)
   
    if pattern and str(pattern).strip().lower() != "nan":
        pattern_uri_id = sanitize_ttl_name(pattern)
        if pattern_uri_id:
            pattern_uri = URIRef(EX[pattern_uri_id])
            if pattern_uri_id not in pattern_individuals:
                pattern_individuals.add(pattern_uri_id)
                add_individual(pattern_uri, EX.Pattern, pattern)
            g.add((se_uri, EX.hasPattern, pattern_uri))

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((se_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
    if ab_id and ab_id in ab_id_to_brands:
        for brand_name in ab_id_to_brands[ab_id]:
            brand_uri_id = make_safe_uri_label(brand_name)
            brand_uri = URIRef(EX[brand_uri_id])
            g.add((brand_uri, EX.hasSideEffect, se_uri))

# ========== INTERACTIONS ==========
substances_by_id = {}
if "Substance" in dfs and not dfs["Substance"].empty:
    for _, row in dfs["Substance"].iterrows():
        sub_id = make_uri_id(row.get("Substance ID"))
        substance_name = safe_str(row.get("Substance Name"))
        substance_type = safe_str(row.get("Type"))
        substance_desc = safe_str(row.get("Substance Description"))
        ref_ids = split_multivalue(row.get("Reference ID"))
        if not sub_id or not substance_name:
            continue
        substance_uri_id = make_safe_uri_label(substance_name)
        if substance_uri_id:
            substances_by_id[sub_id] = {
                "uri_id": substance_uri_id,
                "name": substance_name,
                "type": substance_type,
                "desc": substance_desc,
                "ref_ids": ref_ids
            }

for _, row in dfs["Interaction"].iterrows():
    itn_id = make_uri_id(row.get("Interaction ID"))
    sub_id = make_uri_id(row.get("Substance ID"))  # NEW: Get Substance ID
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    description = safe_str(row.get("Interaction Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))
    
    if not itn_id:
        continue
    
    itn_uri = URIRef(EX[itn_id])
    add_individual(itn_uri, EX.Interaction, itn_id)
    
    if description and description != "Not Specified":
        add_literal(itn_uri, EX.hasInteractionDescription, description)
    
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((itn_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
    
    # NEW: Link to substance using substances_by_id dict
    if sub_id and sub_id in substances_by_id:
        sub = substances_by_id[sub_id]
        sub_uri_id = sub["uri_id"]
        sub_name = sub["name"]
        sub_type = sub["type"]
        sub_desc = sub["desc"]
        sub_refs = sub["ref_ids"]
        
        sub_uri = URIRef(EX[sub_uri_id])
        if sub_uri_id not in created_uris:
            if sub_type.lower() == "drug":
                add_individual(sub_uri, EX.Drug, sub_name)
            elif sub_type.lower() == "food":
                add_individual(sub_uri, EX.Food, sub_name)
            elif sub_type.lower() == "beverage":
                add_individual(sub_uri, EX.Beverage, sub_name)
            else:
                add_individual(sub_uri, EX.Substance, sub_name)
            if sub_desc and sub_desc != "Not Specified":
                add_literal(sub_uri, EX.hasSubstanceDescription, sub_desc)
            for ref_id in sub_refs:
                ref_uri_id = make_uri_id(ref_id)
                if ref_uri_id:
                    g.add((sub_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
        
        g.add((itn_uri, EX.interactsWith, sub_uri))
    
    # Link to brand (existing code stays the same)
    if ab_id and ab_id in ab_id_to_brands:
        for brand_name in ab_id_to_brands[ab_id]:
            brand_uri_id = make_safe_uri_label(brand_name)
            brand_uri = URIRef(EX[brand_uri_id])
            g.add((brand_uri, EX.hasInteraction, itn_uri))

# ========== STEWARDSHIP PRINCIPLES ==========
for _, row in dfs["StewardshipPrinciple"].iterrows():
    sp_id = make_uri_id(row.get("Stewardship ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    principle_type = safe_str(row.get("Principle Type (Therapeutic Use & Monitoring, Administration & Adherence, Food & Timing, Storage)"))
    if not principle_type:
        principle_type = safe_str(row.get("Principle Type (Therapeutic Use & Monitoring, Administration & Adherence, Food & Timing, Storage)"))
    description = safe_str(row.get("Principle Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))
    if not sp_id:
        continue
    sp_class = stewardship_type_to_class(principle_type) if principle_type else "StewardshipPrinciple"
    sp_uri = URIRef(EX[sp_id])
    add_individual(sp_uri, EX[sp_class], sp_id)
    if description and description != "Not Specified":
        add_literal(sp_uri, EX.hasStewardshipDescription, description)
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((sp_uri, EX.hasReference, URIRef(EX[ref_uri_id])))
    if ab_id and ab_id in ab_id_to_brands:
        for brand_name in ab_id_to_brands[ab_id]:
            brand_uri_id = make_safe_uri_label(brand_name)
            brand_uri = URIRef(EX[brand_uri_id])
            if sp_class == "Storage":
                g.add((brand_uri, EX.hasStorageRule, sp_uri))
            elif sp_class == "FoodAndTiming":
                g.add((brand_uri, EX.hasFoodAndTimingRule, sp_uri))
            elif sp_class == "AdministrationAndAdherence":
                g.add((brand_uri, EX.hasAdministrationAndAdherenceRule, sp_uri))
            elif sp_class == "TherapeuticUseAndMonitoring":
                g.add((brand_uri, EX.hasTherapeuticUseAndMonitoringRule, sp_uri))
            else:
                g.add((brand_uri, EX.managedBy, sp_uri))

# ------------------ Generate Turtle Output ------------------
def generate_ttl_output():
    """Generate a clean Turtle file matching ontology_ETL.ttl format."""
    lines = []
    
    # Read OntologyManual.ttl contents
    manual_ttl_path = os.path.join(os.path.dirname(__file__), "..", "OntologyManual.ttl")
    if os.path.exists(manual_ttl_path):
        with open(manual_ttl_path, "r") as f:
            manual_contents = f.read().splitlines()  # Split into lines without newlines
        lines.extend(manual_contents)  # Add all lines from OntologyManual.ttl
        lines.append("")  # Add a newline separator after OntologyManual.ttl contents
    else:
        print(f"Warning: OntologyManual.ttl not found at {manual_ttl_path}")
    #TO DO: now add code inhere which will print or place the contents of the OntologyManual.ttl
    lines.append("")
    lines.append("##############################################################")
    lines.append("# Individuals")
    lines.append("###############################################################")
    lines.append("")
    # Updated types_order to include warning subclasses
    types_order = [
        "Antibiotic", "Brand", "Presentation",
        "Indication", "Severity",
        "Warning", "Contraindication", "PregnancyAndLactation", "AgeRestriction", "Overdosage", "PatientCondition",
        "SideEffect", "Pattern",
        "Interaction", "Drug", "Food", "Beverage", "Substance",
        "StewardshipPrinciple", "Storage", "AdministrationAndAdherence", "FoodAndTiming", "TherapeuticUseAndMonitoring",
        "Reference"
    ]
    subjects_by_type = {}
    for s, p, o in g:
        if p == RDF.type and isinstance(o, URIRef):
            type_name = str(o).replace("http://example.org/ontology#", "")
            if type_name not in subjects_by_type:
                subjects_by_type[type_name] = []
            subjects_by_type[type_name].append(s)
    for type_name in types_order:
        if type_name in subjects_by_type:
            lines.append(f"# {type_name}")
            if type_name == "Presentation":
                lines.append("# label: <brand name> <dosage> <form>")
            for subj in sorted(set(subjects_by_type[type_name]), key=lambda x: str(x)):
                label = ""
                for s, p, o in g:
                    if s == subj and p == RDFS.label:
                        label = str(o)
                        break
                subj_name = str(subj).replace("http://example.org/ontology#", "")
                if label:
                    escaped_label = clean_string(label)
                    lines.append(f":{subj_name} rdf:type :{type_name};")
                    lines.append(f'    rdfs:label "{escaped_label}".')
                else:
                    lines.append(f":{subj_name} rdf:type :{type_name}.")
            lines.append("")
    printed_types = set(types_order)
    for type_name, subjects in sorted(subjects_by_type.items()):
        if type_name not in printed_types:
            lines.append(f"# {type_name}")
            for subj in sorted(set(subjects), key=lambda x: str(x)):
                label = ""
                for s, p, o in g:
                    if s == subj and p == RDFS.label:
                        label = str(o)
                        break
                subj_name = str(subj).replace("http://example.org/ontology#", "")
                if label:
                    escaped_label = clean_string(label)
                    lines.append(f":{subj_name} rdf:type :{type_name};")
                    lines.append(f'    rdfs:label "{escaped_label}".')
                else:
                    lines.append(f":{subj_name} rdf:type :{type_name}.")
            lines.append("")
    lines.append("")
    lines.append("##############################################################")
    lines.append("# Relationships")
    lines.append("###############################################################")
    lines.append("")
    rel_triples = []
    for s, p, o in g:
        if p not in [RDF.type, RDFS.label]:
            rel_triples.append((s, p, o))
    rel_triples.sort(key=lambda x: str(x[0]))
    current_subject = None
    for s, p, o in rel_triples:
        subj_name = str(s).replace("http://example.org/ontology#", "")
        pred_name = str(p).replace("http://example.org/ontology#", "")
        if s != current_subject:
            if current_subject is not None:
                lines.append("")
            current_subject = s
            if isinstance(o, URIRef):
                obj_name = str(o).replace("http://example.org/ontology#", "")
                lines.append(f":{subj_name} :{pred_name} :{obj_name} .")
            else:
                if isinstance(o, Literal) and o.datatype and "integer" in str(o.datatype):
                    lines.append(f":{subj_name} :{pred_name} {int(o)} .")
                elif isinstance(o, Literal) and o.datatype and "double" in str(o.datatype):
                    lines.append(f':{subj_name} :{pred_name} "{o}"^^xsd:double .')
                else:
                    lit_value = clean_string(str(o))
                    lines.append(f':{subj_name} :{pred_name} "{lit_value}" .')
        else:
            if isinstance(o, URIRef):
                obj_name = str(o).replace("http://example.org/ontology#", "")
                lines.append(f":{subj_name} :{pred_name} :{obj_name} .")
            else:
                if isinstance(o, Literal) and o.datatype and "integer" in str(o.datatype):
                    lines.append(f":{subj_name} :{pred_name} {int(o)} .")
                elif isinstance(o, Literal) and o.datatype and "double" in str(o.datatype):
                    lines.append(f':{subj_name} :{pred_name} "{o}"^^xsd:double .')
                else:
                    lit_value = clean_string(str(o))
                    lines.append(f':{subj_name} :{pred_name} "{lit_value}" .')
    return "\n".join(lines)

ttl_content = generate_ttl_output()
with open(output_path, "w") as f:
    f.write(ttl_content)

print(f"Turtle file generated: {output_path}")
print(f"   Total triples: {len(g)}")
print(f"   Unique subjects: {len(created_uris)}")