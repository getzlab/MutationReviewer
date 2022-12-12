import igv_remote as ir


def load_bams_igv(bams_list, chrom, pos, view_type="collapsed", sort="base"):
    
    if len(bams_list) > 0:
        # load igv
        try:
            ir.connect()
        except AssertionError:
            ir.close()
            ir.connect()
        ir.new()
        ir.set_viewopts(view_type=view_type, sort=sort)
        ir.goto(chrom, pos)
        ir.load(*bams_list)
        ir.close()
    else:
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