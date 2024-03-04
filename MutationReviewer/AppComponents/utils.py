import igv_remote

def load_bams_igv(bams_list, chroms, poss, view_type="collapse", sort="base", img_dir= "igv_snapshots/", verbose=False, recv_timeout=60):
    """
    Loads a list of bams into IGV and navigates to the corresponding location of the genome
    
    Parameters
    ----------
    bams_list: List[Union[str, path]]
        List of paths to bam files
        
    chroms: List
        List of chromosomes to navigate to
        
    poss: List
        List of position to navigate to. Corresponds chromosome value in chroms in the same index
        
    view_type: str, ["collapsed", "expanded", "squished"], default="collapsed"
        How to view the alignments. 
        
    sort: str, default="base"
        Feature to sort by
        
    img_dir: str, Path
        Path to save igv snapshots
    """
    ir = igv_remote.IGV_remote(view_type=view_type, sort=sort, verbose=verbose, recv_timeout=recv_timeout)
    ir.new()
    if len(bams_list) > 0:

        ir.set_saveopts(img_dir=img_dir, img_basename = "test.png" )
        ir.set_viewopts(view_type=view_type, sort=sort)
        
        loci_list = [{f'chr{i + 1}': chroms[i], f'pos{i + 1}': poss[i]} for i in range(len(chroms))]
        loci_dict = {k: v for d in loci_list for k, v in d.items()}
        ir.goto_multiple(**loci_dict)
        ir.load(*bams_list)
    else:
        print("no bams selected")
        
