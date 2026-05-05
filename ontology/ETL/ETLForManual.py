#!/usr/bin/env python3
import csv
import re
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def sanitize_ttl_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s\(\)]', '', name)
    name = re.sub(r'\(', ' ', name)
    name = re.sub(r'\)', '', name)
    words = name.split()
    result = ''
    for word in words:
        if word:
            if len(word) > 1:
                result += word[0].upper() + word[1:]
            else:
                result += word.upper()
    return result

def get_unique_values(csv_file, column):
    values = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if column in row and row[column].strip():
                    values.add(row[column].strip())
    except FileNotFoundError:
        return []
    return sorted(values)

def generate_class_ttl(values, superclass):
    ttl_lines = []
    for val in values:
        ttl_name = sanitize_ttl_name(val)
        if ttl_name:
            ttl_lines.append(':{} rdf:type owl:Class ;'.format(ttl_name))
            ttl_lines.append('    rdfs:subClassOf :{} ;'.format(superclass))
            ttl_lines.append('    rdfs:label "{}" .'.format(val))
            ttl_lines.append('')
    return ttl_lines

def get_indication_values(csv_file, condition_type):
    values = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ct = row.get('Condition Type', '').strip().lower()
                if ct == condition_type.lower():
                    name = row.get('Condition Name', '').strip()
                    if name:
                        values.add(name)
    except FileNotFoundError:
        return []
    return sorted(values)

def get_ttl_names(values):
    return [sanitize_ttl_name(v) for v in values if sanitize_ttl_name(v)]

def generate_disjointness_section(class_name, subclasses):
    ttl_lines = []
    ttl_lines.append('# Disjoint {} subclasses'.format(class_name))
    ttl_names = get_ttl_names(subclasses)
    for i, name in enumerate(ttl_names):
        others = [n for j, n in enumerate(ttl_names) if j != i]
        if others:
            # Split into chunks to avoid very long lines
            chunk_size = 5
            for chunk_start in range(0, len(others), chunk_size):
                chunk = others[chunk_start:chunk_start + chunk_size]
                if chunk_start == 0:
                    ttl_lines.append(':{} owl:disjointWith :{} .'.format(name, ', :'.join(chunk)))
                else:
                    ttl_lines[-1] = ttl_lines[-1][:-1] + ', :{} .'.format(', :'.join(chunk))
    return '\n'.join(ttl_lines)

def generate_oneof_section(class_name, subclasses):
    ttl_names = get_ttl_names(subclasses)
    if not ttl_names:
        return ''
    ttl_lines = []
    ttl_lines.append(':{} rdf:type owl:Class ;'.format(class_name))
    ttl_lines.append('    owl:equivalentClass [')
    ttl_lines.append('        rdf:type owl:Class ;')
    ttl_lines.append('        owl:oneOf ( :{} )'.format(' :'.join(ttl_names)))
    ttl_lines.append('    ] .')
    return '\n'.join(ttl_lines)

def generate_differentfrom_section(class_name, subclasses):
    ttl_names = get_ttl_names(subclasses)
    if len(ttl_names) < 2:
        return ''
    ttl_lines = []
    ttl_lines.append('# {} are all different from each other'.format(class_name))
    for i, name in enumerate(ttl_names):
        others = [n for j, n in enumerate(ttl_names) if j != i]
        if others:
            # Split into chunks to avoid very long lines
            chunk_size = 5
            for chunk_start in range(0, len(others), chunk_size):
                chunk = others[chunk_start:chunk_start + chunk_size]
                if chunk_start == 0:
                    ttl_lines.append(':{} owl:differentFrom :{} .'.format(name, ', :'.join(chunk)))
                else:
                    ttl_lines[-1] = ttl_lines[-1][:-1] + ', :{} .'.format(', :'.join(chunk))
    return '\n'.join(ttl_lines)

def generate_owl_restrictions(presentation_values, sideeffect_values, urinary_values, respiratory_values, severity_values):
    ttl_lines = []
    ttl_lines.append('# Presentation must have at least one Brand')
    ttl_lines.append(':Presentation rdfs:subClassOf [')
    ttl_lines.append('    rdf:type owl:Restriction ;')
    ttl_lines.append('    owl:onProperty :isPresentationOf ;')
    ttl_lines.append('    owl:minQualifiedCardinality 1 ;')
    ttl_lines.append('    owl:onClass :Brand')
    ttl_lines.append('] .')
    ttl_lines.append('')
    ttl_lines.append('# SideEffect must have at least one source (Brand, Presentation, or Antibiotic)')
    ttl_lines.append(':SideEffect rdfs:subClassOf [')
    ttl_lines.append('    rdf:type owl:Restriction ;')
    ttl_lines.append('    owl:onProperty :sideEffectOf ;')
    ttl_lines.append('    owl:minCardinality 1')
    ttl_lines.append('] .')
    ttl_lines.append('')
    ttl_lines.append('# SideEffect must have a description')
    ttl_lines.append(':SideEffect rdfs:subClassOf [')
    ttl_lines.append('    rdf:type owl:Restriction ;')
    ttl_lines.append('    owl:onProperty :hasSideEffectDescription ;')
    ttl_lines.append('    owl:minCardinality 1')
    ttl_lines.append('] .')
    ttl_lines.append('')
    ttl_lines.append('# SideEffect must have a duration')
    ttl_lines.append(':SideEffect rdfs:subClassOf [')
    ttl_lines.append('    rdf:type owl:Restriction ;')
    ttl_lines.append('    owl:onProperty :hasDurationOf ;')
    ttl_lines.append('    owl:minCardinality 1')
    ttl_lines.append('] .')
    ttl_lines.append('')
    ttl_lines.append('# SideEffect must have a pattern')
    ttl_lines.append(':SideEffect rdfs:subClassOf [')
    ttl_lines.append('    rdf:type owl:Restriction ;')
    ttl_lines.append('    owl:onProperty :hasPattern ;')
    ttl_lines.append('    owl:minQualifiedCardinality 1 ;')
    ttl_lines.append('    owl:onClass :Pattern')
    ttl_lines.append('] .')
    return '\n'.join(ttl_lines)

def main():
    base_path = os.path.join(SCRIPT_DIR, "data")
    ONTOLOGY_DIR = os.path.dirname(SCRIPT_DIR)
    manual_ttl_path = os.path.join(ONTOLOGY_DIR, 'manual.ttl')
    
    try:
        with open(manual_ttl_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("manual.ttl not found in", ONTOLOGY_DIR, file=sys.stderr)
        sys.exit(1)
    
    print("Generating classes from CSV data...", file=sys.stderr)
    
    presentation_values = get_unique_values(base_path + '/Presentation.csv', "Packing Type")
    sideeffect_values = get_unique_values(base_path + '/SideEffect.csv', "SE Name")
    urinary_values = get_indication_values(base_path + '/Indication.csv', "urinary")
    respiratory_values = get_indication_values(base_path + '/Indication.csv', "respiratory")
    severity_values = get_unique_values(base_path + '/Severity.csv', "Severity Type")
    
    print("Generated", len(presentation_values), "Presentation classes", file=sys.stderr)
    print("Generated", len(sideeffect_values), "SideEffect classes", file=sys.stderr)
    print("Generated", len(urinary_values), "Urinary Disease classes", file=sys.stderr)
    print("Generated", len(respiratory_values), "Respiratory Disease classes", file=sys.stderr)
    print("Generated", len(severity_values), "Severity classes", file=sys.stderr)
    
    # Generate all class definitions with disjointness
    print("Generating Disjointness Properties...", file=sys.stderr)
    
    # Presentation section
    pres_section = '# Presentation subclasses\n# Generated from CSV\n'
    pres_section += '\n'.join(generate_class_ttl(presentation_values, "Presentation")) + '\n'
    pres_section += generate_disjointness_section("Presentation", presentation_values)
    pres_section += '\n# End of Disjoint Presentation subclasses'  # Add end marker
    
    # SideEffect section
    se_section = '# SideEffect subclasses\n# Generated from CSV\n'
    se_section += '\n'.join(generate_class_ttl(sideeffect_values, "SideEffect")) + '\n'
    se_section += generate_disjointness_section("SideEffect", sideeffect_values)
    se_section += '\n# End of Disjoint SideEffect subclasses'  # Add end marker
    
    # Urinary Disease section (add matching end marker to manual.ttl too)
    urin_section = '# Urinary Disease subclasses\n# Generated from CSV\n'
    urin_section += '\n'.join(generate_class_ttl(urinary_values, "UrinaryDisease")) + '\n'
    urin_section += generate_disjointness_section("UrinaryDisease", urinary_values)
    urin_section += '\n# End of Disjoint UrinaryDisease subclasses'  # Add end marker
    
    # Respiratory Disease section
    resp_section = '# Respiratory Disease subclasses\n# Generated from CSV\n'
    resp_section += '\n'.join(generate_class_ttl(respiratory_values, "RespiratoryDisease")) + '\n'
    resp_section += generate_disjointness_section("RespiratoryDisease", respiratory_values)
    resp_section += '\n# End of Disjoint RespiratoryDisease subclasses'  # Add end marker
    
    # Severity section
    sev_section = '# Severity concepts\n# Generated from CSV\n'
    sev_section += '\n'.join(generate_class_ttl(severity_values, "Severity")) + '\n'
    sev_section += generate_disjointness_section("Severity", severity_values)
    sev_section += '\n# End of Disjoint Severity subclasses'  # Add end marker
    # Replacement logic (same pattern for all sections)
    
    # Presentation
    start_marker = "# Presentation subclasses"
    end_marker = "# End of Disjoint Presentation subclasses"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        end_of_end_marker = end_idx + len(end_marker)
        content = content[:start_idx] + pres_section + content[end_of_end_marker:]
    
    # SideEffect
    start_marker = "# SideEffect subclasses"
    end_marker = "# End of Disjoint SideEffect subclasses"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        end_of_end_marker = end_idx + len(end_marker)
        content = content[:start_idx] + se_section + content[end_of_end_marker:]
   
    # Urinary Disease 
    start_marker = "# Urinary Disease subclasses"
    end_marker = "# End of Disjoint UrinaryDisease subclasses"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        end_of_end_marker = end_idx + len(end_marker)
        content = content[:start_idx] + urin_section + content[end_of_end_marker:]
    
    # Respiratory Disease
    start_marker = "# Respiratory Disease subclasses"
    end_marker = "# End of Disjoint RespiratoryDisease subclasses"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        end_of_end_marker = end_idx + len(end_marker)
        content = content[:start_idx] + resp_section + content[end_of_end_marker:]
    
    # Severity
    start_marker = "# Severity concepts"
    end_marker = "# End of Disjoint Severity subclasses"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        end_of_end_marker = end_idx + len(end_marker)
        content = content[:start_idx] + sev_section + content[end_of_end_marker:]

    
    # Generate Closed World Enumerations (oneOf)
    print("Generating Closed World Enumerations...", file=sys.stderr)
    oneof_section = '# Closed World Enumerations (oneOf)\n##############################################################\n\n'
    oneof_section += generate_oneof_section("Presentation", presentation_values) + '\n\n'
    oneof_section += generate_oneof_section("SideEffect", sideeffect_values) + '\n\n'
    oneof_section += generate_oneof_section("UrinaryDisease", urinary_values) + '\n\n'
    oneof_section += generate_oneof_section("RespiratoryDisease", respiratory_values) + '\n\n'
    oneof_section += generate_oneof_section("Severity", severity_values)
    
    start_marker = "# Closed World Enumerations (oneOf)"
    end_marker = "# End of Closed World Enumerations (oneOf)"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + oneof_section + '\n\n' + content[end_idx:]
    
    # Generate differentFrom Assertions
    print("Generating differentFrom Assertions...", file=sys.stderr)
    diff_section = '# differentFrom Assertions for Key Instances\n##############################################################\n\n'
    diff_section += generate_differentfrom_section("Presentation", presentation_values) + '\n\n'
    diff_section += generate_differentfrom_section("SideEffect", sideeffect_values) + '\n\n'
    diff_section += generate_differentfrom_section("UrinaryDisease", urinary_values) + '\n\n'
    diff_section += generate_differentfrom_section("RespiratoryDisease", respiratory_values) + '\n\n'
    diff_section += generate_differentfrom_section("Severity", severity_values)
    
    start_marker = "# differentFrom Assertions for Key Instances"
    end_marker = "# End of differentFrom Assertions for Key Instances"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + diff_section + '\n\n' + content[end_idx:]
    
    # Generate OWL Restrictions
    print("Generating OWL Restrictions...", file=sys.stderr)
    owl_restrictions = '# OWL Restrictions (Cardinality and Value Constraints)\n##############################################################\n\n'
    owl_restrictions += generate_owl_restrictions(presentation_values, sideeffect_values, urinary_values, respiratory_values, severity_values)
    
    start_marker = "# OWL Restrictions (Cardinality and Value Constraints)"
    end_marker = "# End of OWL Restrictions (Cardinality and Value Constraints)"
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + owl_restrictions + '\n\n' + content[end_idx:]
    
    output_path = os.path.join(SCRIPT_DIR, "..", "manual.ttl")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated {}".format(output_path), file=sys.stderr)

if __name__ == "__main__":
    main()
