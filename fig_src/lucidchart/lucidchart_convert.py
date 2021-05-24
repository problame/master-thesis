#!/usr/bin/env python3

from zipfile import ZipFile
from pathlib import Path
import shutil
import subprocess
import os

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
        ]

def process_lucidchart_zip(zip_path, format, outdir, overwrite=False):

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


outdir = Path("./out")
if outdir.is_dir():
    shutil.rmtree(outdir)
outdir.mkdir()

svgs = process_lucidchart_zip('export_svg_transparent_background_all_pages_crop_to_content.zip', 'svg', outdir / "svg")
for svg in svgs:
    dst = svg.parent / "inkscape_pdf" / f"{svg.stem}.pdf"
    assert not dst.exists()
    dst.parent.mkdir(exist_ok=True)
    #subprocess.run(["inkscape",
    #    #"--export-area-drawing",
    #    "--export-dpi=72", "--export-text-to-path", "-o", dst, "--export-type=pdf", svg], check=True)
    subprocess.run(["rsvg-convert", "--zoom=0.474", "-f", "pdf", "-o", dst, svg], check=True)
    assert dst.exists()

#process_lucidchart_zip('export_png_transparent_background_all_pages_crop_to_content_print_quality.zip', 'png', outdir / "png")
#process_lucidchart_allpages_pdf('export_pdf_all_pages_crop_to_content.pdf', outdir / "pdf")

