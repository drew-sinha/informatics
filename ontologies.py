import pathlib
import csv
import collections

### Initialization code
ICD_phecode_file = pathlib.Path("resources/ICD_phecode_map.csv")
HPO_phecode_file = pathlib.Path("resources/HPO_phecode_map.csv")
HPO_gene_file = pathlib.Path("resources/phenotype_to_genes.txt") #Note, this is actually a tsv file
SNOMED_ICD_file = pathlib.Path("resources").glob("tls_Icd10cmHumanReadableMap*.tsv")

gene_HPO_file = pathlib.Path("resources/genes_to_phenotype.txt") #also a tsv file mapping genes to HPO

snomed_icd_map = collections.defaultdict(list) #one-to-many map of icd codes associated with a snomed
snomed_naming = {} #the naming for a snomed id remains one-to-one

"""
NB: the set of icd codes mappable to a phecode is less than the total number of icd codes bundled snomed.
This code keeps the "phecode-icd" codes as a common denominator since SNOMED is licensed.
"""
icd_phecode_map = {}    
icd_naming = {}
phecode_naming = {}


phecode_hpo_map = collections.defaultdict(list) #one-to-many map of hpo terms associated with a phecode
hpo_naming = {}

hpo_gene_map = collections.defaultdict(list) #one-to-many map of genes associated with an HPO term

try:
    SNOMED_ICD_file = list(SNOMED_ICD_file)[0] #this will be empty if not found
except IndexError:
    print("SNOMED-ICD mapping file not found. This file is not provided by default due to licensing restrictions. You may find this file by obtaining a UMLS license and downloading the file from the US National Library of Medicine or SNOMED International.")
else:
    with SNOMED_ICD_file.open('r', encoding='utf-8') as open_file:
        file_reader = csv.reader(open_file, delimiter='\t')
        file_reader.__next__()
        empty_counter, ambiguous_counter = 0, 0
        for row in file_reader:
            snomed_id, snomed_name, icd_code = row[5], row[6], row[11]
            if icd_code == '':
                #some terms with legitimate icd codes have another entry with empty icd
                empty_counter += 1
                continue
            elif icd_code[-1] == '?': 
                #some also have the noted character; notation for entry conveys some ambiguity
                icd_code = icd_code[:-1]
                ambiguous_counter += 1
            snomed_icd_map[snomed_id].append(icd_code)
            snomed_naming[snomed_id] = snomed_name
        print(f"SNOMED-ICD map - empty entries: {empty_counter}; ambiguous entries: {ambiguous_counter}")

gene_hpo_map = collections.defaultdict(list)


with ICD_phecode_file.open('r') as open_file:
    file_reader = csv.reader(open_file)
    file_reader.__next__() # skip header
    for row in file_reader:
        icd, _, icd_name, phecode, phecode_name = row
        icd_phecode_map[icd] = phecode
        icd_naming[icd] = icd_name
        phecode_naming[phecode] = phecode_name

with HPO_phecode_file.open('r') as open_file:
    file_reader = csv.reader(open_file)
    file_reader.__next__()
    for row in file_reader:
        hpo_id, hpo_name, phecode, _ = row
        phecode_hpo_map[phecode].append(hpo_id)
        hpo_naming[hpo_id] = hpo_name
        
with HPO_gene_file.open('r') as open_file:
    file_reader = csv.reader(open_file, delimiter='\t')
    file_reader.__next__()
    for row in file_reader:
        hpo_id, _, _, gene, _ = row
        hpo_gene_map[hpo_id].append(gene)

with gene_HPO_file.open('r') as open_file:
    file_reader = csv.reader(open_file, delimiter='\t')
    file_reader.__next__()
    for row in file_reader:
        _, gene_id, _, hpo_id, _, _ = row
        gene_hpo_map[gene_id].append(hpo_id)

###
def make_snomed_gene_list(snomed_code):
    icd_codes = snomed_icd_map[snomed_code]
    return set([gene for icd in icd_codes for gene in make_icd_gene_list[icd]])
    
def make_icd_gene_list(icd_code):
    hpo_codes = phecode_hpo_map[icd_phecode_map[icd_code]]
    genes = set([gene for hpo in hpo_codes for gene in hpo_gene_map[hpo]])
    return genes

def make_hpo_gene_list(hpo_code):
    return set(hpo_gene_map[hpo_code])

def make_icd_hpo_list(icd_code):
    return set(phecode_hpo_map[icd_phecode_map[icd_code]])
    
def make_hpo_gene_list(hpo_code):
    return set(hpo_gene_map[hpo_code])

def make_gene_hpo_list(gene_id):
    return set(gene_hpo_map[gene_id])
