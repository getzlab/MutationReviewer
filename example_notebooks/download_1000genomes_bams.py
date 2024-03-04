import os
import argparse
from ftplib import FTP 
import pandas as pd
import tqdm

def download_genomes(
    patient_ids, # list of patient ids
    output_dir,
    onek_genomes_ftp="ftp.1000genomes.ebi.ac.uk",
    patient_path_str_format="/vol1/ftp/phase3/data/REPLACE/exome_alignment/REPLACE.mapped.ILLUMINA.bwa.GBR.exome.*.bam",
    region_str="17:7571739-7590808",
    replace_str='REPLACE',
    overwrite=False
):
    if not os.path.exists(output_dir):
        print(f"Making output directory: {output_dir}")
        os.mkdir(output_dir)
    
    ftp = FTP(onek_genomes_ftp) 
    ftp.login() 

    region_str_formatted = region_str.replace(':', '_').replace('-', '_')
    paths_df = pd.DataFrame(index=patient_ids)
    for patient_id in tqdm.tqdm(patient_ids, total=len(patient_ids)):
        bam_path = ftp.nlst(patient_path_str_format.replace(replace_str, patient_id))[0]
        full_bam_path = f"https://{onek_genomes_ftp}/{bam_path}"
        
        output_bam_path = f"{output_dir}/{patient_id}.{region_str_formatted}.bam"
        output_bai_path = f"{output_bam_path.strip('.bam')}.bai"
        if (not os.path.exists(output_bam_path)) or overwrite:
        
            bam_cmd = f'samtools view -bh "{full_bam_path}" "{region_str}" > {output_bam_path}'
            os.system(bam_cmd)

            make_new_bai_cmd = f"samtools index {output_bam_path} {output_bai_path}"
            os.system(make_new_bai_cmd)

            rm_tmp_bai_cmd = f'rm {bam_path.split("/")[-1]}.bai'
            os.system(rm_tmp_bai_cmd)

        paths_df.loc[patient_id, 'original_ftp_path'] = full_bam_path
        paths_df.loc[patient_id, 'original_ftp_path_bai'] = f'{full_bam_path}.bai'
        paths_df.loc[patient_id, 'local_bam_path'] = output_bam_path
        paths_df.loc[patient_id, 'local_bai_path'] = output_bai_path

    paths_fn = f'{output_dir}/1k_genomes_bam_paths.txt'
    paths_df.to_csv(paths_fn, sep='\t')
    return paths_fn
    
def download_vcf(
    output_vcf,
    onek_chr_ftp_path="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr17.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
    region_str="17:7571739-7590808"
):
    cmd = f'bcftools view -r "{region_str}" "{onek_chr_ftp_path}" > {output_vcf}'
    os.system(cmd)

    header_fn = f"{output_vcf}.header.txt"
    get_header_cmd = f'cat {output_vcf} | grep -v "^##" | head -n1 > {header_fn}'
    os.system(get_header_cmd)

def format_vcf(vcf_path):
    header_vcf_path = f'{vcf_path}.header.txt'
    header = pd.read_csv(header_vcf_path, sep='\t')

    vcf_df = pd.read_csv(vcf_path, sep='\t', comment='#', header=None)
    vcf_df.columns = header.columns.tolist()
    vcf_df = vcf_df.rename(columns={'#CHROM': 'CHROM'})

    all_patients = vcf_df.columns[9:]
    return vcf_df, all_patients

def subset_patients_vcf(vcf_df, patients):
    def _get_patient(patient):
        filtered_vcf_df = vcf_df[vcf_df[patient].str.contains('1')][vcf_df.columns.tolist()[:9]]
        filtered_vcf_df['patient_id'] = patient
        return filtered_vcf_df
    
    reformat_patient_vcf_df = pd.concat([_get_patient(p) for p in patients])
    return reformat_patient_vcf_df

