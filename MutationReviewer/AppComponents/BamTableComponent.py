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
    bam_table_display_cols,
    bam_table_page_size=10,
    init_max_bams_view=3
):
    
    return AppComponent(
        name='Sample Bam table',
        layout=gen_mutation_table_igv_layout(bam_table_display_cols, bam_table_page_size, init_max_bams_view),
        callback_input=[Input('bam-table', 'selected_rows')],
        callback_output=[Output('bam-table', 'selected_rows'), Output('bam-table', 'data'), Output('bam-table', 'columns')],
        new_data_callback=new_update_bam_table,
        internal_callback=update_bam_table,
    )

def gen_mutation_table_igv_layout(
    bam_table_display_cols,
    bam_table_page_size,
    init_max_bams_view
):
    return html.Div(
        children=[
            # dbc.Table.from_dataframe(df=pd.DataFrame())
            dash_table.DataTable(
                id='bam-table',
                # columns=[
                #     {"name": i, "id": i} for i in bam_table_display_cols
                # ],
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
    # chrom, pos = idx.split(':', 1)
    # pos = int(pos)
    # samples = data.mutations_df.loc[
    #     (data.mutations_df[data.chrom_col] == chrom) & (data.mutations_df[data.start_pos_col] == pos),
    #     data.mutations_df_sample_col
    # ].tolist()
    # bams_df = data.bams_df.loc[data.bams_df[data.bam_df_sample_col].isin(samples), bam_table_display_cols]
    # load_bams_list = bams_df[data.bam_col].tolist()

    # load_bams_igv(load_bams_list, chrom, pos)
    # return [bams_df.to_dict('records')]
    
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
    
    
