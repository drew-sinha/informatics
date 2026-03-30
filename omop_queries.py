from airms_connect.connection import airms_connection

# Establish connection
airms = airms_connection()
airms.connect()

def _is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False
        
def get_lab_concepts(lab_name):
    domain = "Measurement"
    concept_class = "Lab Test"
    
    query = f"""
        SELECT concept_id, concept_name, vocabulary_id, domain_id, concept_class_id
        FROM cdmdeid.concept
        WHERE 
            standard_concept = 'S'
            AND LOWER(domain_id) = LOWER('{domain}')
            AND LOWER(concept_name) LIKE LOWER('%{lab_name}%')
            AND LOWER(concept_class_id) = LOWER('{concept_class}')
            AND invalid_reason IS NULL
        """
    return airms.conn.sql(query).collect()
    
def get_condition_concepts(condition_name):
    """
        Obtain sets of SNOMED concepts similar to a specified condition name

        Parameters:
            condition_name: String describing the diagnosis of interest

        Returns:
            Pandas dataframe of SNOMED concepts matching the condition of interest
    """
    
    domain = "Condition"
    concept_class = 'Disorder'
    
    query = f"""
        SELECT concept_id, concept_name, vocabulary_id, domain_id, concept_class_id
        FROM cdmdeid.concept
        WHERE 
            standard_concept = 'S'
            AND LOWER(domain_id) = LOWER('{domain}')
            AND LOWER(concept_name) LIKE LOWER('%{condition_name}%')
            AND LOWER(concept_class_id) = LOWER('{concept_class}')
            AND invalid_reason IS NULL
        """
    return airms.conn.sql(query).collect()
    
def get_lab_value(lab_concept_id):
    query = f"""
        SELECT
            m.person_id, m.measurement_concept_id, m.value_as_number, m.range_low, m.range_high, m.value_as_concept_id
        FROM cdmdeid.measurement m
        WHERE m.measurement_concept_id = {lab_concept_id}
            AND m.value_as_number IS NOT NULL
        """
    return airms.conn.sql(query).collect()

def get_diagnosed_subjects(diag_concept_ids):
    """
        Identify a subset of patients with a given diagnosis code

        Parameters:
            diag_concept_ids: int or String format OMOP table condition concept id, or an Iterable of these for multiple conditions

        Returns:
            Pandas dataframe containing the patients diagnosed with these conditions
    """
    
    if (type(diag_concept_ids) is str) or (not _is_iterable(diag_concept_ids)):
        diag_concept_ids = [diag_concept_ids]
    query = f"""
        SELECT DISTINCT
            c.person_id, c.condition_concept_id
        FROM cdmdeid.condition_occurrence c
        WHERE c.condition_concept_id IN ({','.join(diag_concept_ids)})
        """
    return airms.conn.sql(query).collect()

def get_encounter_diags(p_ids):
    """
        Identify encounter diagnoses for a subset of participants

        Parameters:
            p_ids: int or str OMOP table identifier, or an Iterable of these for multiple participants

        Returns:
            Pandas dataframe containing the specified diagnoses for the patients
    """
    
    if (type(p_ids) is str) or (not _is_iterable(p_ids)):
        p_ids = [p_ids]
        
    query = f"""
        SELECT DISTINCT
            c.person_id, c.condition_concept_id, ct.concept_name, ct.concept_class_id
        FROM cdmdeid.condition_occurrence c
        INNER JOIN cdmdeid.concept ct
            ON c.condition_concept_id = ct.concept_id
        WHERE c.person_id IN ({','.join(map(lambda s: f'\'{s}\'', p_ids))})
        """

    
    return airms.conn.sql(query).collect()
    
def get_EHR_problems():
    query = f"""
        SELECT c.person_id, c.condition_concept_id, ct.concept_name
        FROM cdmdeid.condition_occurrence c
        INNER JOIN cdmdeid.concept ct
            ON c.condition_concept_id = ct.concept_id
        WHERE c.condition_type_concept_id = 32840
        ORDER BY person_id
    """
    return airms.conn.sql(query).collect()
