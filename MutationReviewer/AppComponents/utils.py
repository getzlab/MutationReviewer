import igv_remote

def load_bams_igv(bams_list, chroms, poss, view_type="collapsed", sort="base", img_dir= "igv_snapshots/"):
    ir = igv_remote.IGV_remote()
    if len(bams_list) > 0:
        # load igv
        try:
            ir.connect()
        except AssertionError:
            ir.close()
            ir.connect()
        ir.new()
        print('set_saveopts')
        ir.set_saveopts(img_dir=img_dir, img_basename = "test.png" )
        print('set viewopts')
        ir.set_viewopts(view_type=view_type, sort=sort)
        loci_list = [{f'chr{i}': chroms[i], f'pos{i}': poss[i]} for i in range(len(chroms))]
        loci_dict = {k: v for d in loci_list for k, v in d.items()}
        print(loci_dict)
        print('loci')
        ir.goto_multiple(**loci_dict)
        ir.load(*bams_list)
        ir.close()
    else:
        try:
            ir.connect()
        except AssertionError:
            ir.close()
            ir.connect()
        ir.new()
        ir.close()

        
def load_bam_igv(bam, chrom, pos, view_type="collapsed", sort="base"):
    
    try:
        ir.connect()
    except AssertionError:
        ir.close()
        ir.connect()
        
    ir.load(bam)
    ir.close()