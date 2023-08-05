"""
Table of bam files. Each row corresponds to a different bam file, and includes a custom field to reference by sample/patient or other feature. Rows are selectable.
"""
import pandas as pd
import numpy as np
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pickle

from JupyterReviewer.Data import Data, DataAnnotation
from JupyterReviewer.ReviewDataApp import ReviewDataApp, AppComponent
from JupyterReviewer.DataTypes.GenericData import GenericData

import os
import pickle
import sys

# import igv_remote as ir

# from .utils import load_bams_igv, load_bam_igv
from MutationReviewer.DataTypes.GeneralMutationData import GeneralMutationData


def gen_bam_table_component(
    bam_table_page_size=10,
    init_max_bams_view=3
):
    '''
    Generate component with a selectable bam table
    
    Parameters
    ----------
    bam_table_page_size: int
        Max number of rows displayed in the table per page
        
    init_max_bams_view:
        Number of bams to pre-select for loading to IGV.
        
    '''
    
    return AppComponent(
        name='Sample Bam table',
        layout=gen_mutation_table_igv_layout(bam_table_page_size, init_max_bams_view),
        callback_input=[Input('bam-table', 'selected_rows')],
        callback_output=[Output('bam-table', 'selected_rows'), Output('bam-table', 'data'), Output('bam-table', 'columns')],
        new_data_callback=new_update_bam_table,
        internal_callback=update_bam_table,
    )

def gen_mutation_table_igv_layout(
    bam_table_page_size,
    init_max_bams_view
):
    return html.Div(
        children=[
            # dbc.Table.from_dataframe(df=pd.DataFrame())
            dash_table.DataTable(
                id='bam-table',
                data=pd.DataFrame().to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                selected_rows=list(range(init_max_bams_view)),
                page_action="native",
                page_current= 0,
                page_size=bam_table_page_size,
            )
        ],
    )

def new_update_bam_table(
    data: GeneralMutationData, 
    idx, 
    selected_rows,
    bam_table_display_cols,
    gen_data_mut_index_name_func,
    init_max_bams_view
):
    '''
    Parameters
    ----------
    selected_rows: State list
        List passed by a component State reference that indicates which bam rows are selected.
        For updates, this list is overrided by init_max_bams_view
        
    bam_table_display_cols: list
        List of columns to display the bams_df table
        
    gen_data_mut_index_name_func: func
        Function used to parse the index to filter the mutation table
        
    init_max_bams_view:
        Number of bams to pre-select for loading to IGV.
    '''
    
    # reset selected rows
    selected_rows = list(range(init_max_bams_view))
    return update_bam_table(
        data=data, 
        idx=idx, 
        selected_rows=selected_rows,
        bam_table_display_cols=bam_table_display_cols,
        gen_data_mut_index_name_func=gen_data_mut_index_name_func,
        init_max_bams_view=init_max_bams_view
    )

def update_bam_table(
    data: GeneralMutationData, 
    idx, 
    selected_rows,
    bam_table_display_cols,
    gen_data_mut_index_name_func,
    init_max_bams_view
):
    
    '''
    Display bam table with bam file paths in a single column.
    
    Parameters
    ----------
    selected_rows: State list
        List passed by a component State reference that indicates which bam rows are selected.
        
    bam_table_display_cols: list
        List of columns to display the bams_df table
        
    gen_data_mut_index_name_func: func
        Function used to parse the index to filter the mutation table
        
    init_max_bams_view:
        Number of bams to pre-select for loading to IGV.
    '''
    
    idx_mut_df = data.mutations_df.loc[
        data.mutations_df[data.mutation_groupby_cols].apply(
            lambda r: gen_data_mut_index_name_func(r.astype(str).tolist()), 
            axis=1
        ) == idx,
    ]
    
    bam_ref_values = idx_mut_df[data.mutations_df_bam_ref_col].tolist()
    
    bams_df = data.bams_df.loc[data.bams_df[data.bams_df_ref_col].isin(bam_ref_values)].copy()

    stack_cols = [data.bams_df_ref_col] + bam_table_display_cols
    
    stack_bams_df = pd.concat(
        [
            bams_df.set_index(stack_cols)[data.bam_cols].stack().reset_index().rename(columns={0: 'bam', f'level_{len(stack_cols)}': 'bam_source'}), 
            bams_df.set_index(stack_cols)[data.bai_cols].stack().reset_index().rename(columns={0: 'bai', f'level_{len(stack_cols)}': 'bai_source'}), 
        ],
        axis=1
    )
    
    stack_bams_df = stack_bams_df.loc[:,~stack_bams_df.columns.duplicated()]
    
    valid_indices = [i for i in selected_rows if i in range(stack_bams_df.shape[0])]
    
    return [valid_indices, stack_bams_df.to_dict('records'), [{"name": i, "id": i} for i in stack_bams_df.columns.tolist()]]
    
    
