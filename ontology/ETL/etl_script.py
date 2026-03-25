from neo4j import GraphDatabase
import pandas as pd
import os
import re

# ------------------ Neo4j AuraDB connection ------------------
uri = "neo4j+s://6f10cfbb.databases.neo4j.io"
user = "6f10cfbb"
password = "zgXErY0jkGjqEzoeNweM_B9NefxpZZFiZtKHW0EusRM"

driver = GraphDatabase.driver(uri, auth=(user, password))


# ------------------ Helper Functions ------------------
def clean_value(val):
    if pd.isnull(val):
        return None
    val = str(val).strip()
    return val if val != "" else None


def split_multi_values(val):
    if not val:
        return []
    return [v.strip() for v in re.split(r'[\n,]+', val) if v.strip() != ""]


# ------------------ Generic Loader ------------------
def load_csv_to_neo4j(tx, df, label, id_col, relationships=None):
    for idx, row in df.iterrows():

        cleaned_row = {col: clean_value(row[col]) for col in df.columns}

        if not cleaned_row.get(id_col):
            print(f"[WARNING] Skipping {label} row {idx} (missing ID)")
            continue

        node_id = cleaned_row[id_col]

        props = {k: v for k, v in cleaned_row.items() if v is not None}

        query = f"""
        MERGE (n:{label} {{{id_col}: $id}})
        SET n += $props
        """
        tx.run(query, id=node_id, props=props)

        # Generic relationships (Reference, Validator, etc.)
        if relationships:
            for rel in relationships:
                raw_value = cleaned_row.get(rel['target_col'])
                if not raw_value:
                    continue

                targets = split_multi_values(raw_value)

                for target_id in targets:
                    tx.run(f"""
                        MATCH (a:{label} {{{id_col}: $source_id}})
                        MATCH (b:{rel['target_label']} {{{rel['target_id_col']}: $target_id}})
                        MERGE (a)-[:{rel['rel_type']}]->(b)
                    """, source_id=node_id, target_id=target_id)


# ------------------ Relationship Builders ------------------

def create_warning_rel(tx, df):
    for _, row in df.iterrows():
        wid = clean_value(row["warningID"])
        aid = clean_value(row["antibioticID"])

        if wid and aid:
            tx.run("""
                MATCH (a:Antibiotic {antibioticID: $aid})
                MATCH (w:Warning {warningID: $wid})
                MERGE (a)-[:hasWarning]->(w)
            """, aid=aid, wid=wid)


def create_se_rel(tx, df):
    for _, row in df.iterrows():
        sid = clean_value(row["seID"])
        aid = clean_value(row["antibioticID"])

        if sid and aid:
            tx.run("""
                MATCH (a:Antibiotic {antibioticID: $aid})
                MATCH (s:AdverseReaction {seID: $sid})
                MERGE (a)-[:hasAdverseReaction]->(s)
            """, aid=aid, sid=sid)


def create_sp_rel(tx, df):
    for _, row in df.iterrows():
        sid = clean_value(row["stewardshipID"])
        aid = clean_value(row["antibioticID"])

        if sid and aid:
            tx.run("""
                MATCH (a:Antibiotic {antibioticID: $aid})
                MATCH (s:StewardshipPrinciple {stewardshipID: $sid})
                MERGE (a)-[:hasStewardship]->(s)
            """, aid=aid, sid=sid)


def create_interaction_rel(tx, df):
    for _, row in df.iterrows():
        iid = clean_value(row["interactionID"])
        aid = clean_value(row["antibioticID"])

        if iid and aid:
            tx.run("""
                MATCH (a:Antibiotic {antibioticID: $aid})
                MATCH (i:Interaction {interactionID: $iid})
                MERGE (a)-[:hasInteraction]->(i)
            """, aid=aid, iid=iid)


# ------------------ Load Data ------------------
base_path = os.path.join(os.path.dirname(__file__), "data")

with driver.session() as session:

    # 1. Validator
    df = pd.read_csv(os.path.join(base_path, "Validator.csv"))
    session.write_transaction(load_csv_to_neo4j, df, "Validator", "validatorID")

    # 2. Reference
    df = pd.read_csv(os.path.join(base_path, "Reference.csv"))
    session.write_transaction(load_csv_to_neo4j, df, "Reference", "referenceID",
        relationships=[{
            'rel_type': 'validatedBy',
            'target_label': 'Validator',
            'target_col': 'validatorID',
            'target_id_col': 'validatorID'
        }]
    )

    # 3. Antibiotic
    df = pd.read_csv(os.path.join(base_path, "Antibiotic.csv"))
    session.write_transaction(load_csv_to_neo4j, df, "Antibiotic", "antibioticID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )

    # 4. Indication
    df = pd.read_csv(os.path.join(base_path, "Indication.csv"))
    session.write_transaction(load_csv_to_neo4j, df, "Indication", "indicationID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )

    # 5. Warning
    df_warning = pd.read_csv(os.path.join(base_path, "Warning.csv"))
    session.write_transaction(load_csv_to_neo4j, df_warning, "Warning", "warningID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )
    session.write_transaction(create_warning_rel, df_warning)

    # 6. Adverse Reaction
    df_se = pd.read_csv(os.path.join(base_path, "AdverseReaction.csv"))
    session.write_transaction(load_csv_to_neo4j, df_se, "AdverseReaction", "seID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )
    session.write_transaction(create_se_rel, df_se)

    # 7. Stewardship
    df_sp = pd.read_csv(os.path.join(base_path, "StewardshipPrinciple.csv"))
    session.write_transaction(load_csv_to_neo4j, df_sp, "StewardshipPrinciple", "stewardshipID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )
    session.write_transaction(create_sp_rel, df_sp)

    # 8. Substance
    df = pd.read_csv(os.path.join(base_path, "Substance.csv"))
    session.write_transaction(load_csv_to_neo4j, df, "Substance", "substanceID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'}
        ]
    )

    # 9. Interaction
    df_inter = pd.read_csv(os.path.join(base_path, "Interaction.csv"))
    session.write_transaction(load_csv_to_neo4j, df_inter, "Interaction", "interactionID",
        relationships=[
            {'rel_type':'hasReference','target_label':'Reference','target_col':'referenceID','target_id_col':'referenceID'},
            {'rel_type':'validatedBy','target_label':'Validator','target_col':'validatorID','target_id_col':'validatorID'},
            {'rel_type':'interactsWith','target_label':'Substance','target_col':'substanceID','target_id_col':'substanceID'}
        ]
    )
    session.write_transaction(create_interaction_rel, df_inter)

driver.close()