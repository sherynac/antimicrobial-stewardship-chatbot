from neo4j import GraphDatabase
import pandas as pd
import os

# ------------------ Neo4j AuraDB connection ------------------
uri = "neo4j+s://1685b254.databases.neo4j.io"
user = "1685b254"
password = "WIkS9shvx4tj4hPh-gThK6YeJjMjRGVWi7Olb2gwzJg"

driver = GraphDatabase.driver(uri, auth=(user, password))

# ------------------ Helper function ------------------
def load_csv_to_neo4j(tx, df, label, id_col, relationships=None):
    for idx, row in df.iterrows():
        # Skip rows with missing ID
        if pd.isnull(row[id_col]) or str(row[id_col]).strip() == "":
            print(f"[WARNING] Skipping {label} row {idx} because '{id_col}' is empty")
            continue

        # Only include non-empty, non-NaN values
        props = {col: row[col] for col in df.columns if pd.notnull(row[col]) and str(row[col]).strip() != ""}
        merge_props = f"{id_col}: '{row[id_col]}'"

        if props:  # Make sure there’s at least one property to SET
            set_props = ", ".join([f"n.{k} = ${k}" for k in props if k != id_col])
            query = f"MERGE (n:{label} {{{merge_props}}})"
            if set_props:
                query += f" SET {set_props}"
            tx.run(query, **props)
        else:
            # Only MERGE without setting extra properties
            query = f"MERGE (n:{label} {{{merge_props}}})"
            tx.run(query)

        # Relationships (skip if target column is empty)
        if relationships:
            for rel in relationships:
                target_label = rel['target_label']
                target_col = rel['target_col']
                target_id_col = rel['target_id_col']
                rel_type = rel['rel_type']

                if target_col in row and pd.notnull(row[target_col]) and str(row[target_col]).strip() != "":
                    query_rel = f"""
                    MATCH (a:{label} {{{id_col}: $source_id}})
                    MATCH (b:{target_label} {{{target_id_col}: $target_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    """
                    tx.run(query_rel, source_id=row[id_col], target_id=row[target_col])

# ------------------ Base path to CSVs ------------------
base_path = os.path.join(os.path.dirname(__file__), "data")

# ------------------ Load all CSVs ------------------
with driver.session() as session:
    # 1. Validator
    df_validator = pd.read_csv(os.path.join(base_path, "Validator.csv"))
    session.write_transaction(load_csv_to_neo4j, df_validator, "Validator", "validatorID")

    # 2. Reference
    df_reference = pd.read_csv(os.path.join(base_path, "Reference.csv"))
    session.write_transaction(load_csv_to_neo4j, df_reference, "Reference", "referenceID",
                              relationships=[{'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'}])

    # 3. Antibiotic
    df_antibiotic = pd.read_csv(os.path.join(base_path, "Antibiotic.csv"))
    session.write_transaction(load_csv_to_neo4j, df_antibiotic, "Antibiotic", "antibioticID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'}
                              ])

    # 4. Indication
    df_indication = pd.read_csv(os.path.join(base_path, "Indication.csv"))
    session.write_transaction(load_csv_to_neo4j, df_indication, "Indication", "indicationID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'}
                              ])

    # 5. Warning
    df_warning = pd.read_csv(os.path.join(base_path, "Warning.csv"))
    session.write_transaction(load_csv_to_neo4j, df_warning, "Warning", "warningID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'},
                                  {'rel_type':'relatedTo', 'target_label':'Antibiotic', 'target_col':'antibioticID', 'target_id_col':'antibioticID'}
                              ])

    # 6. AdverseReaction
    df_se = pd.read_csv(os.path.join(base_path, "AdverseReaction.csv"))
    session.write_transaction(load_csv_to_neo4j, df_se, "AdverseReaction", "seID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'},
                                  {'rel_type':'relatedTo', 'target_label':'Antibiotic', 'target_col':'antibioticID', 'target_id_col':'antibioticID'}
                              ])

    # 7. StewardshipPrinciple
    df_sp = pd.read_csv(os.path.join(base_path, "StewardshipPrinciple.csv"))
    session.write_transaction(load_csv_to_neo4j, df_sp, "StewardshipPrinciple", "stewardshipID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'},
                                  {'rel_type':'relatedTo', 'target_label':'Antibiotic', 'target_col':'antibioticID', 'target_id_col':'antibioticID'}
                              ])

    # 8. Substance
    df_substance = pd.read_csv(os.path.join(base_path, "Substance.csv"))
    session.write_transaction(load_csv_to_neo4j, df_substance, "Substance", "substanceID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'}
                              ])

    # 9. Interaction
    df_interaction = pd.read_csv(os.path.join(base_path, "Interaction.csv"))
    session.write_transaction(load_csv_to_neo4j, df_interaction, "Interaction", "interactionID",
                              relationships=[
                                  {'rel_type':'hasReference', 'target_label':'Reference', 'target_col':'referenceID', 'target_id_col':'referenceID'},
                                  {'rel_type':'validatedBy', 'target_label':'Validator', 'target_col':'validatorID', 'target_id_col':'validatorID'},
                                  {'rel_type':'relatedTo', 'target_label':'Antibiotic', 'target_col':'antibioticID', 'target_id_col':'antibioticID'},
                                  {'rel_type':'interactsWith', 'target_label':'Substance', 'target_col':'substanceID', 'target_id_col':'substanceID'}
                              ])

driver.close()