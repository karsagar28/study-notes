#!/usr/bin/env python3
"""Regenerate the SVG figures in notes/img/ from code.

Usage:  python3 tools/figures.py
Edit the figure functions below, re-run, refresh the browser.
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "notes", "img")

INK, MUTED, LINE = "#1A1D21", "#5C6470", "#E3E4DE"
C = {  # fill, stroke
    "teal":   ("#E4F0EC", "#0E6E5C"),
    "purple": ("#ECE8F4", "#6B5CA8"),
    "coral":  ("#F6E7E2", "#B4543E"),
    "pink":   ("#F7E6EE", "#B0507E"),
    "gray":   ("#F1F2ED", "#9AA0A6"),
}

STYLE = f"""<style>
text{{font-family:'IBM Plex Sans','Segoe UI',system-ui,sans-serif;fill:{INK}}}
.th{{font-size:14px;font-weight:600}}
.ts{{font-size:12px;fill:{MUTED}}}
</style>"""

MARKER = ('<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" '
          'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
          '<path d="M2 1L8 5L2 9" fill="none" stroke="' + MUTED +
          '" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')


def svg(w, h, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-size="14" role="img"><title>{title}</title>{STYLE}{MARKER}{body}</svg>')


def box(x, y, w, h, color, title, sub=None, title_cls="th"):
    fill, stroke = C[color]
    cx = x + w / 2
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
    if sub:
        s += (f'<text class="{title_cls}" x="{cx}" y="{y + h/2 - 9}" text-anchor="middle" dominant-baseline="central">{title}</text>'
              f'<text class="ts" x="{cx}" y="{y + h/2 + 10}" text-anchor="middle" dominant-baseline="central">{sub}</text>')
    else:
        s += f'<text class="{title_cls}" x="{cx}" y="{y + h/2}" text-anchor="middle" dominant-baseline="central">{title}</text>'
    return s


def container(x, y, w, h, label):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{LINE}" stroke-dasharray="5 4"/>'
            f'<text class="th" x="{x+16}" y="{y+24}">{label}</text>')


def arrow(x1, y1, x2, y2, dashed=False):
    d = ' stroke-dasharray="3 3"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="1.2"{d} marker-end="url(#a)"/>'


def curve(x1, y1, x2, y2):
    mx = (x1 + x2) / 2
    return (f'<path d="M{x1} {y1} C {mx} {y1} {mx} {y2} {x2} {y2}" fill="none" '
            f'stroke="{MUTED}" stroke-width="1.2" marker-end="url(#a)"/>')


def row4(y, color, items):
    xs = [52, 200, 348, 496]
    return "".join(box(x, y, 140, 56, color, t, s) for x, (t, s) in zip(xs, items))


def row3(y, color, items):
    xs = [56, 252, 448]
    return "".join(box(x, y, 180, 56, color, t, s) for x, (t, s) in zip(xs, items))


# ---------------------------------------------------------------- figures

def fig_nvidia():
    b = container(40, 20, 600, 112, "NVIDIA data center GPUs")
    b += row4(60, "teal", [("Hopper", "H100 · H200"), ("Blackwell", "B200 · GB200"),
                           ("Blackwell Ultra", "B300 · GB300"), ("Rubin", "R100 · H2 2026")])
    b += container(40, 172, 600, 112, "NVIDIA CPUs")
    b += row4(212, "purple", [("Grace", "72 Arm cores"), ("GH200", "Grace + Hopper"),
                              ("GB200 / GB300", "Grace+Blackwell"), ("Vera", "pairs with Rubin")])
    return svg(680, 296, "NVIDIA data center GPU and CPU lineups", b)


def fig_silicon_one():
    b = container(40, 20, 600, 184, "Cisco Silicon One ASICs")
    b += row3(60, "coral", [("Web-scale switching", "G100 · G200 · G202"),
                            ("Deep-buffer routing", "P100 · P200"),
                            ("Core routing", "Q100 · Q200 · Q211")])
    b += row3(132, "coral", [("SP edge and metro", "K100 · K200"),
                             ("Enterprise routing", "E100 · E200"),
                             ("Campus access", "A100 · A200")])
    return svg(680, 224, "Cisco Silicon One families by role", b)


def fig_broadcom():
    b = container(40, 20, 600, 184, "Broadcom switch and routing ASICs")
    b += row3(60, "pink", [("Scale-out switching", "Tomahawk 5 · 6"),
                           ("Scale-up / HPC", "Tomahawk Ultra"),
                           ("Enterprise and ToR", "Trident 4 · 5")])
    b += row3(132, "pink", [("AI scheduled fabric", "Jericho3-AI + Ramon3"),
                            ("Scale-across DCI", "Jericho4 + Ramon4"),
                            ("SP edge routing", "Qumran 2C · 3")])
    return svg(680, 224, "Broadcom ASIC families by role", b)


def fig_die_budget():
    def chip(x, title, sub, blocks, extra=""):
        cx = x + 90
        s = (f'<text class="th" x="{cx}" y="48" text-anchor="middle">{title}</text>'
             f'<text class="ts" x="{cx}" y="64" text-anchor="middle">{sub}</text>'
             f'<rect x="{x}" y="76" width="180" height="232" rx="10" fill="none" stroke="{MUTED}"/>')
        for by, bh, color, label in blocks:
            s += box(x + 8, by, 164, bh, color, label, title_cls="ts")
        return s + extra
    b = chip(40, "Scale-out fabric", "Tomahawk · G-series", [
        (86, 80, "gray", "SerDes 512 × 112G"), (174, 40, "purple", "Shared SRAM buffer"),
        (222, 40, "teal", "Fast fixed pipeline"), (270, 30, "coral", "Small tables")])
    hbm = (f'<line x1="300" y1="308" x2="300" y2="318" stroke="{MUTED}"/>'
           f'<line x1="380" y1="308" x2="380" y2="318" stroke="{MUTED}"/>'
           + box(258, 318, 164, 30, "purple", "HBM · GBs of buffer", title_cls="ts"))
    b += chip(250, "Deep-buffer router", "Jericho · P-series", [
        (86, 50, "gray", "SerDes"), (144, 40, "teal", "VOQ scheduler"),
        (192, 50, "coral", "Large FIB + MACsec"), (250, 50, "purple", "HBM controller")], hbm)
    b += chip(460, "Feature-rich edge", "Trident · K · E-series", [
        (86, 40, "gray", "SerDes (fewer)"), (134, 55, "teal", "Flexible parser"),
        (197, 60, "coral", "TCAM · ACL · MAC"), (265, 35, "coral", "NetFlow telemetry")])
    legend = [("gray", "I/O", 40), ("purple", "Memory / buffering", 110),
              ("teal", "Packet pipeline", 260), ("coral", "Tables / features", 400)]
    for color, label, x in legend:
        fill, stroke = C[color]
        b += (f'<rect x="{x}" y="364" width="12" height="12" rx="2" fill="{fill}" stroke="{stroke}"/>'
              f'<text class="ts" x="{x+18}" y="370" dominant-baseline="central">{label}</text>')
    return svg(680, 396, "Where die area goes, by use case", b)


def fig_voq():
    b = arrow(14, 88, 38, 88)
    b += box(40, 60, 150, 56, "gray", "Ingress pipeline", "classify to VOQ")
    b += arrow(192, 88, 248, 88)
    b += box(250, 60, 170, 56, "teal", "On-chip buffer", "SRAM · shared pool")
    b += arrow(422, 88, 478, 88)
    b += box(480, 60, 160, 56, "gray", "Egress scheduler", "credit-based grants")
    b += arrow(642, 88, 666, 88)
    b += arrow(305, 118, 305, 186) + arrow(365, 188, 365, 120)
    b += f'<text class="ts" x="390" y="155" dominant-baseline="central">congested VOQs only</text>'
    b += box(250, 190, 170, 56, "purple", "External HBM", "GBs · shared pool")
    return svg(680, 266, "Two-tier deep buffer: shared pools, per-VOQ accounting", b)


def fig_afd_dpp():
    b = arrow(14, 128, 38, 128)
    b += box(40, 100, 150, 56, "gray", "Flow classifier", "ETRAP elephant trap")
    b += curve(192, 114, 248, 76) + curve(192, 142, 248, 180)
    b += box(250, 48, 220, 56, "teal", "DPP express lane", "first packets of new flows")
    b += box(250, 152, 220, 56, "coral", "AFD-managed queue", "elephants · early ECN / drop")
    b += arrow(360, 210, 360, 232, dashed=True)
    b += f'<text class="ts" x="374" y="230" dominant-baseline="central">probabilistic mark, fair-rate based</text>'
    b += curve(472, 76, 528, 114) + curve(472, 180, 528, 142)
    b += box(530, 100, 110, 56, "gray", "Egress port")
    return svg(680, 256, "CloudScale intelligent buffering: DPP and AFD", b)


def fig_pipeline_rtc():
    b = f'<text class="th" x="40" y="40">Pipeline model</text>'
    b += arrow(14, 88, 38, 88)
    stages = ["Parser", "L2 lookup", "L3 lookup", "ACL · QoS"]
    for i, s in enumerate(stages):
        x = 40 + i * 124
        b += box(x, 66, 100, 44, "gray", s, title_cls="ts")
        if i < 3:
            b += arrow(x + 102, 88, x + 122, 88)
    b += arrow(514, 88, 548, 88)
    b += f'<text class="ts" x="40" y="134">fixed stage sequence · deterministic latency · unused stages still cost time</text>'
    b += f'<text class="th" x="40" y="182">Run-to-completion model</text>'
    b += arrow(14, 240, 38, 240)
    fill, stroke = C["teal"]
    b += (f'<rect x="40" y="200" width="390" height="80" rx="8" fill="{fill}" stroke="{stroke}"/>'
          f'<text class="ts" x="235" y="216" text-anchor="middle" dominant-baseline="central">Packet processor array · shared tables</text>')
    for i in range(6):
        b += f'<rect x="{62 + i*60}" y="232" width="40" height="30" rx="4" fill="none" stroke="{stroke}"/>'
    b += arrow(432, 240, 466, 240)
    b += f'<text class="ts" x="40" y="300">one engine runs the whole program per packet · long programs OK · latency varies</text>'
    return svg(680, 310, "Pipeline vs run-to-completion execution", b)


FIGS = {
    "fig-nvidia-lineup.svg": fig_nvidia,
    "fig-silicon-one.svg": fig_silicon_one,
    "fig-broadcom.svg": fig_broadcom,
    "fig-die-budget.svg": fig_die_budget,
    "fig-voq-two-tier.svg": fig_voq,
    "fig-afd-dpp.svg": fig_afd_dpp,
    "fig-pipeline-vs-rtc.svg": fig_pipeline_rtc,
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FIGS.items():
        path = os.path.join(OUT, name)
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", os.path.relpath(path))
