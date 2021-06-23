### Low Latency Synchronous IO For OpenZFS Using Persistent Memory

> OpenZFS is a storage system that combines volume management and filesystem services.
> The ZFS Intent Log (ZIL) is ZFS's mechanism for supporting synchronous IO semantics.
> To improve ZIL performance, ZFS allows for the configuration of a separate log device (SLOG) that it uses exclusively for ZIL allocations.
> 
> Persistent memory (PMEM) is an emerging technology that provides low-latency memory-mapped byte-addressable persistent storage.
> The Linux kernel's /dev/pmem pseudo block device allows existing block device consumers to benefit from PMEM's high throughput and low latency without modification.
> 
> To explore the use of PMEM as a storage medium for the ZIL, we configure a ZFS storage pool that uses /dev/pmem as a SLOG.
> We find that the current ZIL implementation (ZIL-LWB) exhibits significantly higher latency and sub-par throughput compared to the raw PMEM hardware in a 4k synchronous random write workload.
> An analysis of wall clock time distribution among the ZFS components involved in this type of IO operation reveals that block-device-oriented abstractions and data structures account for the vast majority of the overall latency.
> 
> Motivated by this observation, we propose a new type of ZIL called **ZIL-PMEM** that exclusively targets persistent memory to take advantage of its remarkable performance characteristics.
> We refactor ZFS to support different **ZIL kinds** at runtime, enabling coexistence of ZIL-LWB and ZIL-PMEM.
> ZIL-PMEM maintains the same crash consistency guarantees towards userspace as ZIL-LWB and uses the same checksum to ensure data integrity.
> We validate our core data structure through extensive unit testing as well as the upstream test suite and stress testing tool.
> Our implementation shows high speedups over ZIL-LWB, with a maximum of 8x in a single-threaded 4k synchronous random write workload on the same storage hardware.


This repository contains the text & presentations for my [Master's Thesis](https://github.com/problame/master-thesis/blob/master/releases/thesis-2021-06-07-6bbb186.pdf).
Our tree of OpenZFS is published [here](https://github.com/problame/zfs-master-thesis).

* PDF builds of the thesis in `./releases`
  * Final submission: [`thesis-2021-06-07-6bbb186.pdf`](https://github.com/problame/master-thesis/blob/master/releases/thesis-2021-06-07-6bbb186.pdf)
* Intermediate Presentation ([Google Slides](https://docs.google.com/presentation/d/1bsovsHMcMKI9dxca54QYlfYFpSxTps3s1rI3wVEC_Xw/edit?usp=sharing), archive in `./presentations/intermediate`)
* Final Presentation ([Google Slides](https://docs.google.com/presentation/d/1Sw1P6MAKrdRaDXpTohwd_IvWoCf_ecnDJ1rA1Em-Hm0/edit?usp=sharing), archive in `./presentations/final`)
* Sources:
    * Latex: `./thesis.tex`
        * Build with `make thesis.pdf` (uses `latexmk`, Python 3.7, and `rsvg-convert`)
    * Plots in `./fig_src/static/evaluation`: [separate repo, copy-pasted over manually](https://github.com/problame/master-thesis-evaluation)
    * Figures in `./fig_src/lucidchart/*.zip`: exported from [LucidChart Document](https://lucid.app/lucidchart/f56c7cda-140a-49a2-bfe6-1f31173f1267/view?page=0_0#)
        * read `./fig_src/generate_fig.py`
        * Note: I changed 'File -> Page Settings -> Content Scale' to 200% on some pages after the last export to get the appropriate DPI for Google Slides when copy-pasting selections with Ctrl-C + Ctrl-V.

