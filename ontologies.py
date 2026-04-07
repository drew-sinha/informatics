import pathlib
import csv
import collections

### Initialization code
ICD_phecode_file = pathlib.Path("resources/ICD_phecode_map.csv")
HPO_phecode_file = pathlib.Path("resources/HPO_phecode_map.csv")
HPO_gene_file = pathlib.Path("resources/phenotype_to_genes.txt") #Note, this is actually a tsv file
gene_HPO_file = pathlib.Path("resources/genes_to_phenotype.txt") #also a tsv file mapping genes to HPO

icd_phecode_map = {}
icd_naming = {}
phecode_naming = {}

phecode_hpo_map = collections.defaultdict(list) #one-to-many map of hpo terms associated with a phecode
hpo_naming = {}

hpo_gene_map = collections.defaultdict(list) #one-to-many map of genes associated with an HPO term

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

def make_icd_gene_list(icd_code):
    hpo_codes = phecode_hpo_map[icd_phecode_map[icd_code]]
    genes = set([gene for hpo in hpo_codes for gene in hpo_gene_map[hpo]])
    return genes

def make_icd_hpo_list(icd_code):
    return set(phecode_hpo_map[icd_phecode_map[icd_code]])
    
def make_hpo_gene_list(hpo_code):
    return set(hpo_gene_map[hpo_code])

def make_gene_hpo_list(gene_id):
    return set(gene_hpo_map[gene_id])
