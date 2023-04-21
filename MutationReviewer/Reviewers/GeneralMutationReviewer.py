from JupyterReviewer.ReviewerTemplate import ReviewerTemplate
from JupyterReviewer.ReviewDataApp import ReviewDataApp, AppComponent
from JupyterReviewer.DataTypes.GenericData import GenericData
from JupyterReviewer.Data import Data, DataAnnotation
from JupyterReviewer.AnnotationDisplayComponent import *
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from typing import Dict, List
import plotly.express as px
import dash_bootstrap_components as dbc
import igv_remote as ir
from typing import Union, List, Dict
from pathlib import Path

import pandas as pd
import numpy as np
from MutationReviewer.AppComponents.BamTableComponent import gen_bam_table_component
from MutationReviewer.AppComponents.IGVJSComponent import gen_igv_js_component
from MutationReviewer.AppComponents.IGVLocalComponent import gen_igv_local_component
from MutationReviewer.AppComponents.MutationTableComponent import gen_mutation_table_component
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData
        

class GeneralMutationReviewer(ReviewerTemplate):
    
    def gen_data_mut_index_name(self, value_list):
        return ':'.join(value_list)
        
        
    def gen_data(
        self,
        description: str,
        mutations_df: pd.DataFrame,
        mutation_groupby_cols: list, 
        mutations_df_bam_ref_col: str, 
        chrom_cols: Union[str, list],
        pos_cols: Union[str, list],
        bams_df: pd.DataFrame,
        bams_df_ref_col: str,
        bam_cols: Union[str, list],
        bai_cols: Union[str, list],
        annot_df: pd.DataFrame = None,
        annot_col_config_dict: Dict = None,
        history_df: pd.DataFrame = None,
        index: List = None,
    ) -> GeneralMutationData:
        """
        Parameters
        ==========
        mutations_df: pd.DataFrame
            Table of mutations to review. Each observed mutation has its own row (ie one mutation in each sample). 
            It must have columns containing information about:
                - Chromosome(s)
                - Position(s)
            
        mutation_groupby_cols: list
            Additional columns to group mutations in addition to the chromosome and position. 
            For example, you may group across a participant to view the same locus across all the samples from that participant. 
            You will need to have a column with the participant value in this table.
            
        mutations_df_bam_ref_col: str
            Column in mutations_df to reference which bam files to view in IGV from bams_df. 
            If you want to view all samples from the same participant (ie tumor and normal, or serial tumor samples), 
            the values in "mutations_df_bam_ref_col" must correspond to the values in the "bams_df_ref_col" column in bams_df.
        
        chrom_cols: Union[str, list]
            Column name(s) in mutations_df referencing the chromosome of the mutation. 
            You may have multiple loci if you are reviewing a large SV with two breakpoints ([chr1, chr2]).
            
        pos_cols: Union[str, list]
            Column name(s) in mutations_df referencing the position of the mutation. 
            You may have multiple loci if you are reviewing a large SV with two breakpoints ([chr1, chr2]).
            
        bams_df: pd.DataFrame
            Table with bam paths or urls
            
        bams_df_ref_col: str
            Column in bams_df with values to extract the relevant bams for a given mutation's mutations_df_bam_ref_col value 
            
        bam_cols: Union[str, list]
            Column(s) with bams to view
            
        bai_cols: Union[str, list]
            Column(s) with corresponding bai files to view bams. Corresponding bai columns must be in same order as the bam_cols
        """
        index = [self.gen_data_mut_index_name(list(map(str, idx))) for idx in mutations_df.groupby(mutation_groupby_cols).count().index]
        mutations_df[chrom_cols] = mutations_df[chrom_cols].astype(str)
        return GeneralMutationData(
            index=index,
            description=description,
            mutations_df=mutations_df,
            mutation_groupby_cols=mutation_groupby_cols,
            mutations_df_bam_ref_col=mutations_df_bam_ref_col,
            chrom_cols=chrom_cols,
            pos_cols=pos_cols,
            bams_df=bams_df,
            bams_df_ref_col=bams_df_ref_col,
            bam_cols=bam_cols,
            bai_cols=bai_cols,
            annot_df=annot_df,
            annot_col_config_dict=annot_col_config_dict,
            history_df=history_df,
        )
        
        
    def gen_review_app(
        self,
        mutation_table_display_cols,
        bam_table_display_cols,
        genome='hg19',
        track_height=400,
        minimumBases=200,
        init_max_bams_view=2,
        igv_mode='igv_js', # or 'igv_local' or 'both'
        bam_table_page_size=10,
        init_max_bams_view=2,
    ) -> ReviewDataApp:
        """
        Parameters
        ----------
        mutation_table_display_cols: list
            List of columns to display the mutations_df table
            
        bam_table_display_cols: list
            List of columns to display the bams_df table
            
        genome: string, default='hg19'
            Name of genome to use in IGV.js
        
        track_height: int, default=400
            Height to display each track in IGV.js mode
        
        minimumBases: int, default=200
            Minimum number of bases to display in a window in IGV.js mode
            
        init_max_bams_view: int, default=2
            Number of bams to pre-select for loading to IGV.
        
        igv_mode: str, ['igv_js', 'igv_local', 'both']:
            Indicate which version of IGV to use. 
            
            igv_js: good for casual review. 
                Requires no additional setup. Lacks other features such as blat filtering.
            
            igv_local: requires your machine has IGV running. 
                If you are reading from a google bucket, you must login first,
                If you are running in a VM, you must
                    1. Download IGV on your vm 
                    1. Set up and run VNC server
                    1. Open IGV in your VM and log in to your google account
                
            both: Have both igv_js and igv_local available to load bams
        
        """
        app = ReviewDataApp()
        
        app.add_component(
            gen_mutation_table_component(),
            mutation_table_display_cols=mutation_table_display_cols,
            gen_data_mut_index_name_func=self.gen_data_mut_index_name
        )
        
        app.add_component(
            gen_bam_table_component(bam_table_page_size=bam_table_page_size, init_max_bams_view=init_max_bams_view),
            bam_table_display_cols=bam_table_display_cols,
            gen_data_mut_index_name_func=self.gen_data_mut_index_name,
            init_max_bams_view=init_max_bams_view
        )
        
        if (igv_mode == 'igv_js') or (igv_mode == 'both'):
            app.add_component(
                gen_igv_js_component(
                    bam_table_data_state=State('bam-table', 'data'), 
                    bam_table_selected_rows_state=State('bam-table', 'selected_rows')
                ),
                genome=genome,
                track_height=track_height,
                minimumBases=minimumBases,
                gen_data_mut_index_name_func=self.gen_data_mut_index_name
            )
            
        if igv_mode == 'igv_local' or (igv_mode == 'both'):
            app.add_component(
                gen_igv_local_component(
                    bam_table_data_state=State('bam-table', 'data'), 
                    bam_table_selected_rows_state=State('bam-table', 'selected_rows')
                ),
                gen_data_mut_index_name_func=self.gen_data_mut_index_name
            )
        
        return app
        
    def set_default_review_data_annotations(self):
        
        # Calls
        self.add_review_data_annotation(
            'mutation_call', 
            DataAnnotation(
                'string',
                options=['Somatic', 'Germline', 'Ambiguous', 'Failed']
            )
        )
        
        # Read Artifact Tags
        self.add_review_data_annotation(
            'sequencing_tags',
            DataAnnotation(
                'multi',
                options=[
                    'Directional',
                    'Multiple Mismatches',
                    'High discrepancy Region',
                    'Short Insert',
                    'Short Insert Only',
                    'Same Start and End',
                    "Within 30bp of 3' end"
                ]
            )
        )
        
        # Alignment Tags
        self.add_review_data_annotation(
            'alignment_tags',
            DataAnnotation(
                'multi',
                options=[
                    'Low Mapping Quality',
                    'Adjacent Indel',
                    'Mononucleotide Repeat',
                    'Dinucleotide Repeat',
                    'Tandem Repeat'
                ]
            )
        )
        
        self.add_review_data_annotation(
            'normal_tags',
            DataAnnotation(
                'multi',
                options=[
                    'No PoN coverage',
                    'No Count Normal',
                    'Low Count Normal',
                    'Tumor in Normal',
                ]
            )
        )
        
        self.add_review_data_annotation(
            'tumor_tags',
            DataAnnotation(
                'multi',
                options=[
                    'Low Count Tumor',
                    'Low Vaf in Tumor',
                    'Multiple Variants in Tumor'
                ]
            )
        )
        
        self.add_review_data_annotation(
            'other_tag_description',
            DataAnnotation('string')
        )
        
        self.add_review_data_annotation('Notes', DataAnnotation('string'))
        
    def set_default_review_data_annotations_app_display(self):
        self.add_annotation_display_component('mutation_call', RadioitemAnnotationDisplay())
        
        # alternative
        self.add_annotation_display_component('sequencing_tags', MultiValueSelectAnnotationDisplay())
        self.add_annotation_display_component('alignment_tags', MultiValueSelectAnnotationDisplay())
        self.add_annotation_display_component('normal_tags', MultiValueSelectAnnotationDisplay())
        self.add_annotation_display_component('tumor_tags', MultiValueSelectAnnotationDisplay())
        self.add_annotation_display_component('other_tag_description', TextAnnotationDisplay())
        self.add_annotation_display_component('Notes', TextAreaAnnotationDisplay())
        
    def set_default_autofill(self):
        pass
    