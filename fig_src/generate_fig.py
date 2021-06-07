#!/usr/bin/env python3

from zipfile import ZipFile
from pathlib import Path
import shutil
import subprocess
import os
import sys
import tempfile

names_in_page_order = [
        "prb_chunk_ownership_cycle__transitions",
        "prb_hdl_log_structure_example",
        "prb_hdl_runtime_states",
        "zil_writepath_and_replay_sequence_logical_level",
        "prb_writepath_crashconsistent_append",
        "prb_persistent_structure__chunklayout",
        "prb_chunk_ownership_cycle__example",
        "prb_counters_table__computation_and_encoding",
        "prb_counters_table__example",
        "zilpmem_architecture_overview",
        "zil_lwb_latency_analysis__breakdown",
        "zil_lwb__physical_structure_append",
        "zil_lwb__physical_structure_overview",
        "zilog_splitup_viz",
        "zfs_log_write_sequence_diagram",
        "zilpmem_dataset_hdl_sync",
        "prb_replay_resume_architecture",
        "zil_writepath_activity_diagram_write_fsync_sync",
        "itxg_bypass_viz",
        "correctness_eval_example_I-_shape",
        "prb_replay_full_example",
        ]

def process_lucidchart_zip(zip_path, format, outdir, overwrite=False):
    """Take a lucidchart ZIP export (that's what you get with 'All pages' + 'Crop to Content') and map it to individual, renamed files."""

    if outdir.exists():
        if overwrite:
            shutil.rmtree(outdir)
        else:
            raise Exception(f"outdir={outdir} must not exist")

    outdir.mkdir()

    with ZipFile(zip_path, 'r') as zf:

        namemap = {f"Page {idx+1}.{format}": name for idx, name in enumerate(names_in_page_order)}

        # ensure 1:1 mapping
        exist_pages = set(zf.namelist())
        desired_pages = set(namemap.keys())
        if exist_pages != desired_pages:
            raise Exception(f"""unexpected content in zip file
            exist_pages={exist_pages}
            desired_pages={desired_pages}
            exist - desired={exist_pages - desired_pages}
            desired - exist={desired_pages - exist_pages}
            """)

        paths = []
        for ep in exist_pages:
            dest_name = namemap[ep]
            dest_path = outdir / f"{dest_name}.{format}"
            dest_path.write_bytes(zf.open(ep).read())
            paths += [dest_path]
        return paths

def process_lucidchart_allpages_pdf(pdf_path, outdir, overwrite=False):
    """I thought this was nice but turns out Lucidchart's PDF exporter produces pretty whacky output for the connector lines (bezier curves, I think)"""

    if not Path(pdf_path).is_file():
        raise Exception(f"{pdf_path} must be a regular file")

    if outdir.exists():
        if overwrite:
            shutil.rmtree(outdir)
        else:
            raise Exception(f"outdir={outdir} must not exist")

    outdir.mkdir()

    pdfpages_dir = outdir / "tmp"

    pdfpages_dir.mkdir()

    subprocess.run(["pdfseparate", os.path.relpath(pdf_path, pdfpages_dir), 'Page %d.pdf'], cwd=pdfpages_dir, check=True)

    zip_path = outdir / "tmp.zip"
    with ZipFile(zip_path, mode='w') as pdfpages_zip:
        for page in pdfpages_dir.iterdir():
            pdfpages_zip.write(page, arcname=page.name)

    tmpout = outdir / "tmp_out"
    tmppaths = process_lucidchart_zip(zip_path, 'pdf', tmpout, overwrite=True)

    shutil.rmtree(pdfpages_dir)
    zip_path.unlink()

    paths = []
    for p in tmppaths:
        dstpath = outdir /  p.name
        p.rename(dstpath)
        paths += [dstpath]

    tmpout.rmdir() # should be empty by now

    return paths

###########################################################################
# Script from now on
###########################################################################


outdir = Path(sys.argv[1])
if outdir.exists():
    raise Exception(f"outdir={outdir} must not exist")
outdir.mkdir()

scriptdir = Path(__file__).parent

# Export Lucidchart
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # Lucidchart's PDF output isn't any good
    #process_lucidchart_allpages_pdf('export_pdf_all_pages_crop_to_content.pdf', outdir / "pdf")

    # Have an option for Lucidchart-generated PNG's in case the SVG export + rsvg resizing below
    # breaks in the future.
    #process_lucidchart_zip(scriptdir / "lucidchart" / 'export_png_transparent_background_all_pages_crop_to_content_print_quality.zip', 'png', outdir / "lucidchart_png")

    # We use the Lucidchart SVG export to generate the PDF figures.
    svgs = process_lucidchart_zip(scriptdir / "lucidchart" / 'export_svg_transparent_background_all_pages_crop_to_content.zip', 'svg', tmp / "svg")
    pdfs = []
    for svg in svgs:
        dst = tmp / "pdf" / f"{svg.stem}.pdf"
        assert not dst.exists()
        dst.parent.mkdir(exist_ok=True)
        # Lucidchart sets SVG 'width' and 'height' to pixel values that correspond to 0.474 of the mm widths in the Lucidchart app
        subprocess.run(["rsvg-convert", "--zoom=0.474", "-f", "pdf", "-o", dst, svg], check=True)
        assert dst.exists()
        pdfs += [dst]

    for pdf in pdfs:
        dst = outdir / pdf.name
        if dst.exists():
            raise Exception(f"file {dst} already exists")
        shutil.move(pdf, dst)

# Export static assets
static_dir = scriptdir / "static"
subprocess.run(["cp", "-npr", *static_dir.iterdir(), f"{outdir}/"], check=True)
