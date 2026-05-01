import os
import re
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, XSD, OWL

# ------------------ Setup ------------------
g = Graph()
EX = Namespace("http://example.org/ontology#")
g.bind(":", EX)

# ------------------ Paths ------------------
base_path = os.path.join(os.path.dirname(__file__), "data")
output_path = os.path.join(os.path.dirname(__file__), "..", "ontology_ETL.ttl")

csv_files = {
    "Antibiotic": os.path.join(base_path, "Antibiotic.csv"),
    "Indication": os.path.join(base_path, "Indication.csv"),
    "Warning": os.path.join(base_path, "Warning.csv"),
    "SideEffect": os.path.join(base_path, "SideEffect.csv"),
    "StewardshipPrinciple": os.path.join(base_path, "StewardshipPrinciple.csv"),
    "Substance": os.path.join(base_path, "Substance.csv"),
    "Interaction": os.path.join(base_path, "Interaction.csv"),
    "Reference": os.path.join(base_path, "Reference.csv"),
}

# ------------------ Helper Functions ------------------
def clean_string(val):
    """Escape characters that would break TTL parsing (for output only)."""
    if val is None:
        return ""
    s = str(val)
    # Escape backslashes first, then other characters
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

def safe_str(val):
    """Safely convert value to string, handling NaN/None."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()

def severity_to_class(severity_str):
    """Map severity string to ontology class URI."""
    mapping = {
        "Not Specified": "NotSpecified",
        "Mild": "Mild",
        "Mild to moderate": "MildToModerate",
        "Mild to Moderate": "MildToModerate",
        "Mild to severe": "MildToSevere",
        "Mild to Severe": "MildToSevere",
        "Moderate to severe": "ModerateToSevere",
        "Moderate to Severe": "ModerateToSevere",
        "Severe": "Severe",
        "Initial therapy": "InitialTherapy",
        "Mild to moderate (can worsen if untreated)": "MildToModerateCanWorsenIfUntreated",
    }
    return mapping.get(severity_str.strip(), None)

def condition_type_to_class(condition_type):
    """Map condition type to ontology class URI."""
    ct = condition_type.strip().lower()
    if ct == "respiratory":
        return "RespiratoryDisease"
    elif ct == "urinary":
        return "UrinaryDisease"
    return None

def map_presentation_to_ontology_class(presentation_str):
    """Map CSV presentation string to ontology class URI."""
    p = presentation_str.strip().lower()
    if p == "capsule":
        return "Capsule"
    elif p == "tablet":
        return "Tablet"
    elif p in ["film coated tablet", "film-coated tablet", "fc tablet"]:
        return "FilmCoatedTablet"
    elif p in ["iv injection", "im injection", "injection", "solution for injection"]:
        return "IMInjection"
    elif p == "powder for injection":
        return "PowderForInjection"
    elif p == "injection concentrate":
        return "InjectionConcentrate"
    elif p in ["iv infusion", "infusion"]:
        return "IVInfusion"
    elif p == "solution for infusion":
        return "SolutionForInfusion"
    elif p == "powder for iv infusion":
        return "PowderForIVInfusion"
    elif p == "syrup":
        return "Syrup"
    elif p == "oral suspension":
        return "OralSuspension"
    elif p == "oral drops":
        return "OralDrops"
    elif p == "powder for suspension":
        return "PowderForSuspension"
    elif p == "powder for oral suspension":
        return "PowderForOralSuspension"
    elif p == "granules for oral suspension":
        return "GranulesForOralSuspension"
    elif p in ["ointment", "cream"]:
        return "Ointment"
    return "PresentationOrPacking"

def warning_type_to_class(type_str):
    """Map warning type to ontology class URI."""
    t = type_str.strip().lower()
    if "hypersensitivity" in t or "allergy" in t or "contraindication" in t:
        return "Contraindication"
    elif "pregnancy" in t or "lactation" in t or "breastfeeding" in t:
        return "PregnancyAndLactation"
    elif "age" in t or "pediatric" in t or "geriatric" in t or "children" in t or "newborn" in t or "infant" in t:
        return "AgeRestriction"
    elif "condition" in t or "patient" in t or "renal" in t or "hepatic" in t or "cardiac" in t:
        return "PatientCondition"
    elif "overdosage" in t:
        return "Overdosage"
    elif "contraindication" in t:
        return "Contraindication"
    return "PatientCondition"

def side_effect_to_class(se_name):
    """Map side effect name to ontology class URI."""
    name = se_name.strip().lower().replace('\n', ' ').replace('\r', ' ')
    # Normalize multiple spaces
    import re
    name = re.sub(r'\s+', ' ', name).strip()
    # Skip mapping if this name is also an indication condition (to avoid disjointness violation)
    if name in indication_condition_names:
        return "SideEffect"
    mapping = {
        "diarrhea": "Diarrhea",
        "nausea": "Nausea",
        "vomiting": "Vomiting",
        "headache": "Headache",
        "dizziness": "Dizziness",
        "rash": "Rash",
        "abdominal pain": "AbdominalPain",
        "stomach pain": "StomachPain",
        "back pain": "BackPain",
        "menstrual pain": "MenstrualPain",
        "sore throat / stuffy nose": "SoreThroatOrStuffyNose",
        "vaginitis": "Vaginitis",
        "asthenia": "Asthenia",
        "dyspepsia": "Dyspepsia",
        "vertigo": "Vertigo",
        "somnolence": "Somnolence",
        "fatigue": "Fatigue",
        "photosensitivity": "Photosensitivity",
        "angioedema": "Angioedema",
        "palpitations": "Palpitations",
        "chest pain": "ChestPain",
        "flatulence": "Flatulence",
        "melena": "Melena",
        "cholestatic jaundice": "CholestaticJaundice",
        "nephritis": "Nephritis",
        "candidiasis": "Candidiasis",
        "fungal infections": "FungalInfections",
        "gastroenteritis": "Gastroenteritis",
        "rhinitis": "Rhinitis",
        "oral candidiasis": "OralCandidiasis",
        "leukopenia": "Leukopenia",
        "eosinophilia": "Eosinophilia",
        "insomnia": "Insomnia",
        "agitation": "Agitation",
        "hot flush": "HotFlush",
        "stevens-johnson syndrome": "StevensJohnsonSyndrome",
        "toxic epidermal necrolysis": "ToxicEpidermalNecrolysis",
        "anaphylaxis": "Anaphylaxis",
        "c. difficile-associated diarrhea": "CDifficileAssociatedDiarrhea",
        "tinnitus": "Tinnitus",
        "uveitis": "Uveitis",
        "cough": "Cough",
        "dyspnea": "Dyspnea",
        "glossitis": "Glossitis",
        "stomatitis": "Stomatitis",
        "pancreatitis": "Pancreatitis",
        "urticaria": "Urticaria",
        "pruritus": "Pruritus",
        "anemia": "Anemia",
        "thrombocytopenia": "Thrombocytopenia",
        "neutropenia": "Neutropenia",
        "hypersensitivity reactions": "HypersensitivityReactions",
        "hearing loss": "HearingLoss",
        "peripheral neuropathy": "PeripheralNeuropathy",
        "seizure": "Seizure",
        "seizures": "Seizures",
        "arrhythmias": "Arrhythmias",
        "constipation": "Constipation",
        "dyspnoea": "Dyspnoea",
        "dysgeusia": "Dysgeusia",
        "vaginal itching": "VaginalItching",
        "vaginal itching or discharge": "VaginalItchingOrDischarge",
        "runny nose": "RunnyNose",
        "unexplained weakness": "UnexplainedWeakness",
        "severe allergic reaction": "SevereAllergicReaction",
        "skin rash": "SkinRash",
        "superficial tooth discoloration": "SuperficialToothDiscoloration",
        "tooth discoloration": "ToothDiscoloration",
        "hypokalemia": "Hypokalemia",
        "hypernatremia": "Hypernatremia",
        "hypocalcemia": "Hypocalcemia",
        "hypophosphatemia": "Hypophosphatemia",
        "transaminase elevations": "TransaminaseElevations",
        "injection site reaction": "InjectionSiteReaction",
        "peripheral edema": "PeripheralEdema",
        "torsade de pointes": "TorsadeDePointes",
        "visual impairment": "VisualImpairment",
        "heartburn": "Heartburn",
        "meningitis aseptic": "MeningitisAseptic",
        "ataxia": "Ataxia",
        "hepatotoxicity": "Hepatotoxicity",
        "esophagitis": "Esophagitis",
        "esophageal ulcerations": "EsophagealUlcerations",
        "angioneurotic edema": "AngioneuroticEdema",
        "hemolytic anemia": "HemolyticAnemia",
        "intracranial hypertension": "IntracranialHypertension",
        "bulging fontanels": "BulgingFontanels",
        "skin hyperpigmentation": "SkinHyperpigmentation",
        "pericarditis": "Pericarditis",
        "jarisch-herxheimer reaction": "JarischHerxheimerReaction",
        "phototoxicity": "Phototoxicity",
        "aortic aneurysm and dissection": "AorticAneurysmAndDissection",
        "tendinitis and tendon rupture": "TendinitisAndTendonRupture",
        "exacerbation of myasthenia gravis": "ExacerbationOfMyastheniaGravis",
        "qt interval prolongation": "QTIntervalProlongation",
        "convulsions": "Convulsions",
        "toxic psychosis": "ToxicPsychosis",
        "restlessness": "Restlessness",
        "vasculitis": "Vasculitis",
        "tremor": "Tremor",
        "drowsiness": "Drowsiness",
        "dysesthesia": "Dysesthesia",
        "catatonia": "Catatonia",
        "pseudomembranous colitis": "PseudomembranousColitis",
        "thrombophlebitis": "Thrombophlebitis",
        "pain": "Pain",
        "prothrombin time": "ProthrombinTime",
        "loss of appetite": "LossOfAppetite",
        "urine color change": "UrineColorChange",
        "lung reaction": "LungReaction",
        "rust-colored urine": "RustColoredUrine",
        "pulmonary hypersensitivity reaction": "PulmonaryHypersensitivityReaction",
        "lupus-like syndrome": "LupusLikeSyndrome",
        "megaloblastosis": "Megaloblastosis",
        "recurrent fever": "RecurrentFever",
        "edema": "Edema",
        "genital moniliasis": "GenitalMoniliasis",
        "granulocytopenia": "Granulocytopenia",
        "allergic reaction": "AllergicReaction",
        "hyperglycemia": "Hyperglycemia",
        "hyperkalemia": "Hyperkalemia",
        "anxiety": "Anxiety",
        "confusion": "Confusion",
        "abnormal dreaming": "AbnormalDreaming",
        "paresthesia": "Paresthesia",
        "abnormal gait": "AbnormalGait",
        "syncope": "Syncope",
        "epistaxis": "Epistaxis",
        "cardiac arrest": "CardiacArrest",
        "palpitation": "Palpitation",
        "ventricular tachycardia": "VentricularTachycardia",
        "ventricular arrhythmia": "VentricularArrhythmia",
        "gastritis": "Gastritis",
        "tendonitis": "Tendonitis",
        "skeletal pain": "SkeletalPain",
        "abnormal renal function": "AbnormalRenalFunction",
        "acute renal failure": "AcuteRenalFailure",
        "rhabdomyolysis": "Rhabdomyolysis",
        "hypoglycaemia": "Hypoglycaemia",
        "decreased appetite": "DecreasedAppetite",
        "metabolic acidosis": "MetabolicAcidosis",
        "depression": "Depression",
        "hallucinations": "Hallucinations",
        "psychotic disorder": "PsychoticDisorder",
        "neuropathy peripheral": "NeuropathyPeripheral",
        "angioedema and cholestatic jaundice": "AngioedemaAndCholestaticJaundice",
        "palpitations and chest pain": "PalpitationsAndChestPain",
        "haemolysis in g6pd deficiency": "HaemolysisInG6PDDeficiency",
        "anaphylactic reaction": "AnaphylacticReaction",
        "hypersensitivity vasculitis henoch schonlein purpura": "HypersensitivityVasculitisHenochSchonleinPurpura",
        "lung infiltration": "LungInfiltration",
        "jaundice cholestatic": "JaundiceCholestatic",
        "hepatic necrosis": "HepaticNecrosis",
        "transaminases increased": "TransaminasesIncreased",
        "blood bilirubin increased": "BloodBilirubinIncreased",
        "photosensitivity reaction": "PhotosensitivityReaction",
        "dermatitis exfoliative": "DermatitisExfoliative",
        "fixed drug eruption": "FixedDrugEruption",
        "erythema multiforme": "ErythemaMultiforme",
        "acute generalised exanthematous pustulosis": "AcuteGeneralisedExanthematousPustulosis",
        "acute febrile neutrophilic dermatosis": "AcuteFebrileNeutrophilicDermatosis",
        "drug reaction with eosinophilia and systemic symptoms": "DrugReactionWithEosinophiliaAndSystemicSymptoms",
        "arthralgia": "Arthralgia",
        "myalgia": "Myalgia",
        "renal impairment": "RenalImpairment",
        "tubulointerstitial nephritis and uveitis syndrome": "TubulointerstitialNephritisAndUveitisSyndrome",
        "renal tubular acidosis": "RenalTubularAcidosis",
        "hematologic and lymphatic systems": "HematologicAndLymphaticSystems",
        "central nervous system effects": "CentralNervousSystemEffects",
        "gastrointestinal effects": "GastrointestinalEffects",
        "hepatic": "Hepatic",
        "vaginal yeast infection": "VaginalYeastInfection",
        "oral thrush": "OralThrush",
        "nervous system effects": "NervousSystemEffects",
        "hemic and lymphatic": "HemicAndLymphatic",
        "hypersensitivity": "Hypersensitivity",
        "gastrointestinal": "Gastrointestinal",
        "neurologic": "Neurologic",
        "injection site": "InjectionSite",
        "systemic (rare)": "SystemicRare",
        "liver enzyme elevation": "LiverEnzymeElevation",
        "stomatitis or glossitis": "StomatitisOrGlossitis",
        "anorexia": "Anorexia",
        "cardiac arrhythmias": "CardiacArrhythmias",
        "dysphagia": "Dysphagia",
        "enterocolitis": "Enterocolitis",
        "maculopapular": "Maculopapular",
        "erythematous rashes": "ErythematousRashes",
        "rise in bun": "RiseInBUN",
        "anaphylactoid purpura": "AnaphylactoidPurpura",
        "exacerbation of systemic lupus erythematosus": "ExacerbationOfSystemicLupusErythematosus",
        "skin rash or hives": "RashOrHives",
        "emesis": "Emesis",
        "hypokalemia ": "Hypokalemia",
        "dysmenorrhea": "Dysmenorrhea",
        "vestibular loss": "VestibularLoss",
        "impaired hearing": "ImpairedHearing",
        "metallic taste": "MetallicTaste",
        "taste changes": "TasteChanges",
        "sodium overload": "SodiumOverload",
        "elevated liver enzymes": "ElevatedLiverEnzymes",
        "transient reductions in neutrophil counts": "TransientReductionsInNeutrophilCounts",
        "infusion site reaction": "InfusionSiteReaction",
        "symptoms of bowel inflammation": "SymptomsOfBowelInflammation",
        "decreased lymphocyte count and blood bicarbonate": "DecreasedLymphocyteCountAndBloodBicarbonate",
        "increased eosinophil count, basophils, monocytes and neutrophils": "IncreasedEosinophilCountBasophilsMonocytesAndNeutrophils",
        "overgrowth fungal / c. difficile": "OvergrowthFungalOrCDifficile",
        "agranulocytosis": "Agranulocytosis",
        "megaloblastic anaemia": "MegaloblasticAnaemia",
        "aplastic anaemia": "AplasticAnaemia",
        "haemolytic anaemia": "HaemolyticAnaemia",
        "methaemoglobinaemia": "Methaemoglobinaemia",
        "purpura": "Purpura",
        "serum sickness": "SerumSickness",
        "allergic myocarditis": "AllergicMyocarditis",
        "periarteritis nodosa": "PeriarteritisNodosa",
        "systemic lupus erythematosus": "SystemicLupusErythematosus",
        "haemophagocytic lymphohistiocytosis": "HaemophagocyticLymphohistiocytosis",
        "hyperkalaemia": "Hyperkalaemia",
        "hyponatraemia": "Hyponatraemia",
        "severe hypersensitivity reactions associated with pneumocystis jirovecii pneumonia": "SevereHypersensitivityWithPneumocystisJiroveciiPneumonia",
        "gastrointestinal disturbances": "GastrointestinalDisturbances",
        "pseudomembranous / c. difficile colitis": "PseudomembranousOrCDifficileColitis",
        "increased hepatic enzymes": "IncreasedHepaticEnzymes",
        "increased alkaline phosphatase": "IncreasedAlkalinePhosphatase",
        "severe cutaneous adverse reactions": "SevereCutaneousAdverseReactions",
        "fall in prothrombin activity": "FallInProthrombinActivity",
        "symptomatic hyper and hypoglycemia": "SymptomaticHyperAndHypoglycemia",
        "drop in blood pressure": "DropInBloodPressure",
        "tendon effects": "TendonEffects",
        "blood glucose disturbances": "BloodGlucoseDisturbances",
        "vision disorder": "VisionDisorder",
        "c. difficile associated diarrhea": "CDifficileAssociatedDiarrhea",
        "nausea / vomiting": "NauseaOrVomiting",
        "rash / hives": "RashOrHives",
        "hepatobiliary disorder": "HepatobiliaryDisorder",
        "other serious and sometimes fatal reactions": "OtherSeriousAndSometimesFatalReactions",
        "photosensitivity / phototoxicity": "PhotosensitivityOrPhototoxicity",
        "mental alertness": "MentalAlertness",
        "peripheral neuropathies": "PeripheralNeuropathies",
        "ability to drive or operate machinery": "AbilityToDriveOrOperateMachinery",
        "liver damage": "LiverDamage",
        "pulmonary problems": "PulmonaryProblems",
        "upset stomach": "UpsetStomach",
        "serious pulmonary reaction": "SeriousPulmonaryReaction",
        "liver problems": "LiverProblems",
        "renal": "Renal",
        "cardiac effects": "CardiacEffects",
        "neurological effects": "NeurologicalEffects",
        "allergic reactions": "AllergicReactions",
        "skin & systemic reactions": "SkinAndSystemicReactions",
        "exfoliative dermatitis": "ExfoliativeDermatitis",
        "clostridium difficile-associated diarrhea": "CDifficileAssociatedDiarrhea",
        "inflammatory lesions (with monilial overgrowth)": "InflammatoryLesionsWithMonilialOvergrowth",
        "reduction in neutrophil count": "ReductionInNeutrophilCount",
        "haemolysis in certain susceptible g-6-pd deficient patients": "HaemolysisInG6PDDeficiency",
        "hypersensitivity vasculitis resembling henoch-schönlein purpura": "HypersensitivityVasculitisHenochSchonleinPurpura",
        "stomatitis / glossitis": "StomatitisOrGlossitis",
        "prolongation of the qt interval": "QTIntervalProlongation",
        # Additional mappings for CSV variations and typos
        "aoric aneurysm and dissection": "AorticAneurysmAndDissection",
        "risk of aortic aneurysm and dissection": "AorticAneurysmAndDissection",
        "hypoglycemia": "Hypoglycaemia",
        "urine color": "UrineColorChange",
        "liver enzyme values": "LiverEnzymeElevation",
        "convulsion": "Convulsions",
    }
    if name in mapping:
        return mapping[name]
    for key, val in mapping.items():
        if key in name:
            return val
    return "SideEffect"

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
    elif "prevention" in t:
        return "TherapeuticUseAndMonitoring"
    return "StewardshipPrinciple"

# ------------------ Load DataFrames ------------------
dfs = {}
for name, path in csv_files.items():
    dfs[name] = pd.read_csv(path, dtype=str)

# Build a set of indication condition names to avoid creating SideEffect subclasses with the same names
indication_condition_names = set()
if "Indication" in dfs:
    for _, row in dfs["Indication"].iterrows():
        condition_name = safe_str(row.get("Condition Name"))
        if condition_name:
            indication_condition_names.add(condition_name.strip().lower())

# ------------------ Create Individuals & Relationships ------------------

# Track created URIs to avoid duplicates
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
    ref_id = make_uri_id(row.get("Reference ID"))
    if not ref_id:
        continue
    uri = URIRef(EX[ref_id])
    add_individual(uri, EX.Reference, ref_id)
    add_literal(uri, EX.hasReferenceTitle, row.get("Title"))
    add_literal(uri, EX.hasAuthor, row.get("Author/Source"))
    try:
        year = row.get("Date", "").strip()
        if year and year.isdigit():
            g.add((uri, EX.publishedIn, Literal(int(year), datatype=XSD.integer)))
    except:
        pass
    add_literal(uri, EX.retrievedFrom, row.get("URL"))

# ========== ANTIBIOTICS & BRANDS ==========
# Track unique antibiotics and brands
antibiotics = {}  # generic_name -> antibiotic_id
brands = {}  # brand_name -> list of (antibiotic_id, brand_id, drug_class)
presentations = {}  # presentation_id -> {brand_id, presentation_class, dosage, unit_price}

for _, row in dfs["Antibiotic"].iterrows():
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    generic_name = safe_str(row.get("Generic Name"))
    brand_name = safe_str(row.get("Brand Name"))
    drug_class = safe_str(row.get("Drug Class"))
    presentation = safe_str(row.get("Presentation/Packing"))
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
    brand_uri_id = make_safe_uri_label(brand_name)
    brand_uri = URIRef(EX[brand_uri_id])
    if brand_key not in brands:
        brands[brand_key] = {"name": brand_name, "antibiotic_id": generic_name, "ab_uri": URIRef(EX[generic_name])}
        add_individual(brand_uri, EX.Brand, brand_name)
        g.add((URIRef(EX[generic_name]), EX.hasBrandName, brand_uri))

    # Process presentation for EVERY row (brands can have multiple presentations)
    if presentation and ab_id:
        # Create presentation individual using Antibiotic ID
        pres_uri = URIRef(EX[ab_id])
        # Map CSV presentation to ontology class
        pres_class = map_presentation_to_ontology_class(presentation)
        if pres_class:
            add_individual(pres_uri, EX[pres_class], presentation)
        else:
            add_individual(pres_uri, EX.PresentationOrPacking, presentation)
        g.add((brand_uri, EX.hasPresentation, pres_uri))

    # Link references to brand
    brand_uri_id = make_safe_uri_label(brand_name)
    brand_uri = URIRef(EX[brand_uri_id])
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((brand_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

# ========== INDICATIONS ==========
for _, row in dfs["Indication"].iterrows():
    ind_id = make_uri_id(row.get("Indication ID"))
    antibiotic_ids = split_multivalue(row.get("Antibiotic ID"))
    condition_name = safe_str(row.get("Condition Name"))
    condition_type = safe_str(row.get("Condition Type"))
    symptoms = safe_str(row.get("Symptoms"))
    severity_str = safe_str(row.get("Condition Severity"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not ind_id:
        continue

    # Determine condition class
    cond_class = None
    if condition_type:
        cond_type_class = condition_type_to_class(condition_type)
        if cond_type_class:
            cond_class = cond_type_class

    # Try to map condition name to specific class
    for name_key in ["Condition Name"]:
        val = row.get(name_key, "").strip()
        if val:
            specific_class = None
            cn = val.lower()
            # Map common condition names to ontology classes
            class_map = {
                "atypical pneumonia": "AtypicalPneumonia",
                "sinus infection (sinusitis)": "SinusInfectionSinusitis",
                "sinus infection": "SinusInfectionSinusitis",
                "genitourinary tract infection": "GenitourinaryTractInfection",
                "respiratory tract infection": "RespiratoryTractInfection",
                "acute bacterial exacerbations of copd": "AcuteBacterialExacerbationsOfCOPD",
                "acute bacterial sinusitis": "AcuteBacterialSinusitis",
                "acute maxillary sinusitis": "AcuteMaxillarySinusitis",
                "community-acquired pneumonia (cap)": "CommunityAcquiredPneumoniaCAP",
                "community acquired pneumonia (cap)": "CommunityAcquiredPneumoniaCAP",
                "tonsillitis": "Tonsillitis",
                "pharyngitis": "Pharyngitis",
                "disseminated mycobacterium avium complex (mac) disease": "DisseminatedMycobacteriumAviumComplexMACDisease",
                "hospital-acquired pneumonia (hap)": "HospitalAcquiredPneumoniaHAP",
                "ventilator-associated pneumonia (vap)": "VentilatorAssociatedPneumoniaVAP",
                "chronic bronchitis": "ChronicBronchitis",
                "lower respiratory tract infection": "LowerRespiratoryTractInfection",
                "upper respiratory tract infection": "UpperRespiratoryTractInfection",
                "acute bronchitis": "AcuteBronchitis",
                "lung abscess": "LungAbscess",
                "bronchitis": "Bronchitis",
                "bronchiectasis": "Bronchiectasis",
                "tracheobronchitis": "Tracheobronchitis",
                "pneumonia": "Pneumonia",
                "community acquired respiratory infections": "CommunityAcquiredRespiratoryInfections",
                "inhalation anthrax": "InhalationAnthrax",
                "legionnaire's disease": "LegionnairesDisease",
                "q fever": "QFever",
                "tuberculosis": "Tuberculosis",
                "non-gonococcal urethritis": "NonGonococcalUrethritis",
                "urethritis": "Urethritis",
                "genital ulcer disease for men": "GenitalUlcerDiseaseForMen",
                "acute cystitis": "AcuteCystitis",
                "complicated urinary tract infection (cuti)": "ComplicatedUrinaryTractInfectionCUTI",
                "uncomplicated urinary tract infection (uti)": "UncomplicatedUrinaryTractInfectionUTI",
                "acute uncomplicated urinary tract infection (uti)": "AcuteUncomplicatedUrinaryTractInfectionUTI",
                "acute pyelonephritis": "AcutePyelonephritis",
                "upper urinary tract infection": "UpperUrinaryTractInfection",
                "lower urinary tract infection": "LowerUrinaryTractInfection",
                "genital infections": "GenitalInfections",
                "chronic bacterial prostatitis": "ChronicBacterialProstatitis",
                "urinary tract infections": "UrinaryTractInfections",
                "pyelonephritis": "Pyelonephritis",
                "uncomplicated gonorrhea": "UncomplicatedGonorrhea",
                "gonorrhea": "Gonorrhea",
                "recurrent urinary tract infection": "RecurrentUrinaryTractInfection",
                "bladder infection": "BladderInfection",
                "single pneumonia": "SinglePneumonia",
                "lobar pneumonia": "LobarPneumonia",
                "bronchopneumonia": "Bronchopneumonia",
                "secondary infections in chronic respiratory diseases": "SecondaryInfectionsInChronicRespiratoryDiseases",
                "acute bacterial exacerbation of chronic bronchitis": "AcuteBacterialExacerbationOfChronicBronchitis",
            }
            for key, cls in class_map.items():
                if cn == key or cn.startswith(key):
                    specific_class = cls
                    break
            if specific_class:
                cond_class = specific_class

    if not cond_class:
        cond_class = "Indication"

    # Create indication individual
    ind_uri = URIRef(EX[ind_id])
    label = f"{severity_str} {condition_name}" if severity_str and severity_str.lower() != "not specified" else condition_name
    add_individual(ind_uri, EX[cond_class], label if label else ind_id)

    # Add severity
    if severity_str:
        sev_class = severity_to_class(severity_str)
        if sev_class:
            sev_uri = URIRef(EX[sev_class])
            add_individual(sev_uri, EX.Severity, sev_class)
            g.add((ind_uri, EX.hasSeverityType, sev_uri))

    # Add symptoms
    symptoms = safe_str(row.get("Symptoms"))
    if symptoms:
        add_literal(ind_uri, EX.hasSymptoms, symptoms)

    # Add references
    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((ind_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

    # Link to brands (treats relationship)
    for ab_id_str in antibiotic_ids:
        ab_id_clean = make_uri_id(ab_id_str)
        if ab_id_clean:
            # Find which brand this antibiotic ID corresponds to
            for brand_key, brand_info in brands.items():
                # Check if this brand is associated with this antibiotic ID
                # We need to match by the Antibiotic ID from the CSV
                pass

# Re-process indications with proper antibiotic-to-brand mapping
# First, build a mapping from Antibiotic ID to brand names
ab_id_to_brands = {}
for _, row in dfs["Antibiotic"].iterrows():
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    brand_name = safe_str(row.get("Brand Name"))
    if ab_id and brand_name:
        if ab_id not in ab_id_to_brands:
            ab_id_to_brands[ab_id] = []
        if brand_name not in ab_id_to_brands[ab_id]:
            ab_id_to_brands[ab_id].append(brand_name)

# Now add treats relationships
for _, row in dfs["Indication"].iterrows():
    ind_id = make_uri_id(row.get("Indication ID"))
    antibiotic_ids = split_multivalue(row.get("Antibiotic ID"))

    if not ind_id:
        continue

    ind_uri = URIRef(EX[ind_id])

    for ab_id_str in antibiotic_ids:
        ab_id_clean = make_uri_id(ab_id_str)
        if ab_id_clean:
            g.add((URIRef(EX[ab_id_clean]), EX.treats, ind_uri))

# ========== WARNINGS ==========
for _, row in dfs["Warning"].iterrows():
    w_id = make_uri_id(row.get("Warning ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))

    type_str = safe_str(row.get("Type"))
    headline = safe_str(row.get("Headline"))
    description = safe_str(row.get("Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not w_id:
        continue

    w_class = warning_type_to_class(type_str) if type_str else "Warning"
    w_uri = URIRef(EX[w_id])
    add_individual(w_uri, EX[w_class], w_id)

    if headline:
        add_literal(w_uri, EX.hasWarningHeadline, headline)
    if description:
        add_literal(w_uri, EX.hasWarningText, description)

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((w_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

    if ab_id:
        g.add((URIRef(EX[ab_id]), EX.hasWarning, w_uri))

# ========== SIDE EFFECTS ==========
for _, row in dfs["SideEffect"].iterrows():
    se_id = make_uri_id(row.get("SE ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    se_name = safe_str(row.get("SE Name"))
    duration = safe_str(row.get("Duration (How long it might last (approximate, general))"))
    pattern = safe_str(row.get("Occurrence Pattern (How often or when it appears during use)"))
    description = safe_str(row.get("SE Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not se_id:
        continue

    se_class = side_effect_to_class(se_name) if se_name else "SideEffect"
    se_uri = URIRef(EX[se_id])
    add_individual(se_uri, EX[se_class], se_name)

    if description:
        add_literal(se_uri, EX.hasSideEffectDescription, description)
    if duration:
        add_literal(se_uri, EX.hasDurationOf, duration)
    if pattern:
        # Use raw pattern value from CSV as the class URI (normalized)
        import re
        pattern_class = re.sub(r"[^\w\-]", "_", pattern.strip())
        pattern_uri = URIRef(EX[pattern_class])
        add_individual(pattern_uri, EX.Pattern, pattern)
        g.add((se_uri, EX.hasPattern, pattern_uri))

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((se_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

    if ab_id:
        g.add((URIRef(EX[ab_id]), EX.hasSideEffect, se_uri))

# ========== SUBSTANCES ==========
for _, row in dfs["Substance"].iterrows():
    s_id = make_uri_id(row.get("Substance ID"))
    s_name = safe_str(row.get("Substance Name"))
    s_type = safe_str(row.get("Type"))
    description = safe_str(row.get("Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not s_id:
        continue

    type_class = "Substance"
    if s_type:
        st = s_type.lower()
        if st == "drug":
            type_class = "Drug"
        elif st == "food":
            type_class = "Food"
        elif st == "beverage":
            type_class = "Beverage"

    s_uri = URIRef(EX[s_id])
    add_individual(s_uri, EX[type_class], s_name if s_name else s_id)

    if description:
        add_literal(s_uri, EX.hasSubstanceDescription, description)

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((s_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

# ========== INTERACTIONS ==========
for _, row in dfs["Interaction"].iterrows():
    itn_id = make_uri_id(row.get("Interaction ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    s_id = make_uri_id(row.get("Substance ID"))
    description = safe_str(row.get("Interaction Description"))
    clinical_effects = safe_str(row.get("Clinical Effects"))
    management = safe_str(row.get("Management Advice"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not itn_id:
        continue

    itn_uri = URIRef(EX[itn_id])
    add_individual(itn_uri, EX.Interaction, itn_id)

    if description:
        add_literal(itn_uri, EX.hasInteractionDescription, description)
    if clinical_effects:
        add_literal(itn_uri, EX.hasClinicalEffects, clinical_effects)
    if management:
        add_literal(itn_uri, EX.hasManagementAdvice, management)

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((itn_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

    if s_id:
        # Handle multi-value substance IDs
        for sub_id in split_multivalue(s_id):
            sub_uri_id = make_uri_id(sub_id)
            if sub_uri_id:
                g.add((itn_uri, EX.interactsWith, URIRef(EX[sub_uri_id])))

    if ab_id:
        g.add((URIRef(EX[ab_id]), EX.hasInteraction, itn_uri))

# ========== STEWARDSHIP PRINCIPLES ==========
for _, row in dfs["StewardshipPrinciple"].iterrows():
    sp_id = make_uri_id(row.get("Stewardship ID"))
    ab_id = make_uri_id(row.get("Antibiotic ID"))
    principle_type = safe_str(row.get("Principle Type\n(Proper Use- Administration, Proper Use - Food & Timing, Proper Use - Preparation, Adherence, Monitoring,Storage)"))
    description = safe_str(row.get("Principle Description"))
    ref_ids = split_multivalue(row.get("Reference ID"))

    if not sp_id:
        continue

    sp_class = stewardship_type_to_class(principle_type) if principle_type else "StewardshipPrinciple"
    sp_uri = URIRef(EX[sp_id])
    add_individual(sp_uri, EX[sp_class], sp_id)

    if description:
        add_literal(sp_uri, EX.hasStewardshipDescription, description)

    for ref_id in ref_ids:
        ref_uri_id = make_uri_id(ref_id)
        if ref_uri_id:
            g.add((sp_uri, EX.hasReference, URIRef(EX[ref_uri_id])))

    if ab_id:
        if sp_class == "Storage":
            g.add((URIRef(EX[ab_id]), EX.hasStorageRule, sp_uri))
        elif sp_class == "AdministrationAndAdherence":
            g.add((URIRef(EX[ab_id]), EX.hasAdministrationAndAdherenceRule, sp_uri))
        elif sp_class == "FoodAndTiming":
            g.add((URIRef(EX[ab_id]), EX.hasFoodAndTimingRule, sp_uri))
        elif sp_class == "TherapeuticUseAndMonitoring":
            g.add((URIRef(EX[ab_id]), EX.hasTherapeuticUseAndMonitoringRule, sp_uri))

# ------------------ Generate Turtle Output ------------------
def generate_ttl_output():
    """Generate a clean Turtle file matching ontology3.ttl format."""
    lines = []
    lines.append("@prefix : <http://example.org/ontology#> .")
    lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    lines.append("@prefix owl: <http://www.w3.org/2002/07/owl#> .")
    lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
    lines.append("")
    lines.append("##############################################################")
    lines.append("# Individuals")
    lines.append("###############################################################")
    lines.append("")

    # Group by type
    types_order = [
        "Antibiotic", "Brand", "Capsule", "Tablet", "IVInjection", "Syrup", "Suspension", "Ointment",
        "Indication", "Severity", "Warning", "SideEffect", "Pattern",
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
            for subj in sorted(set(subjects_by_type[type_name]), key=lambda x: str(x)):
                label = ""
                for s, p, o in g:
                    if s == subj and p == RDFS.label:
                        label = str(o)
                        break
                if label:
                    escaped_label = clean_string(label)
                    lines.append(f":{str(subj).replace('http://example.org/ontology#', '')} rdf:type :{type_name};")
                    lines.append(f'    rdfs:label "{escaped_label}".')
                else:
                    lines.append(f":{str(subj).replace('http://example.org/ontology#', '')} rdf:type :{type_name}.")
            lines.append("")

    # Print any types not in the predefined order (e.g., specific subclasses like Diarrhea, Nausea, etc.)
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
                if label:
                    escaped_label = clean_string(label)
                    lines.append(f":{str(subj).replace('http://example.org/ontology#', '')} rdf:type :{type_name};")
                    lines.append(f'    rdfs:label "{escaped_label}".')
                else:
                    lines.append(f":{str(subj).replace('http://example.org/ontology#', '')} rdf:type :{type_name}.")
            lines.append("")

    # Relationships
    lines.append("##############################################################")
    lines.append("# Relationships")
    lines.append("###############################################################")
    lines.append("")

    # Collect all non-type, non-label triples
    rel_triples = []
    for s, p, o in g:
        if p not in [RDF.type, RDFS.label]:
            rel_triples.append((s, p, o))

    # Sort by subject
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

# Generate and write
ttl_content = generate_ttl_output()
with open(output_path, "w") as f:
    f.write(ttl_content)

print(f"✅ Turtle file generated: {output_path}")
print(f"   Total triples: {len(g)}")
print(f"   Unique subjects: {len(created_uris)}")
