#!/usr/bin/env python3
"""
Create scrollable Sankey plot of nucleotide transitions from FASTA

Usage: python fasta_sankey.py input.fasta [--output file.html] [--range START END]
"""

import argparse
import sys
from collections import defaultdict
import plotly.graph_objects as go
import pysam

# Nucleotide colors
NUC_COLORS = {
    'A': '#D00000', 'T': '#00D000', 'U': '#00D000',
    'G': '#FFB400', 'C': '#0000D0', 'N': '#808080'
}

def read_fasta(filepath):
    """Read and validate FASTA sequences"""
    sequences = []
    seq_length = None
    
    with pysam.FastxFile(filepath) as fh:
        for i, entry in enumerate(fh):
            seq = entry.sequence.upper()
            if seq_length is None:
                seq_length = len(seq)
            elif len(seq) != seq_length:
                sys.exit(f"Error: Sequence {i+1} has length {len(seq)}, expected {seq_length}")
            sequences.append(seq)
    
    if not sequences:
        sys.exit("Error: No sequences found")
    
    return sequences, seq_length

def make_sankey(sequences, seq_length, pos_range=None, width=2000, height=1200):
    """Create Sankey diagram"""
    # Determine position range
    start, end = (pos_range[0]-1, pos_range[1]-1) if pos_range else (0, seq_length-1)
    
    # Count nucleotides and transitions
    pos_nucs = defaultdict(int)
    transitions = defaultdict(int)
    
    for seq in sequences:
        for i in range(start, end + 1):
            pos_nucs[(i, seq[i])] += 1
            if i < end:
                transitions[(i, seq[i], seq[i+1])] += 1
    
    # Build nodes
    node_map = {}
    labels, colors, x_pos, y_pos = [], [], [], []
    idx = 0
    
    for col, pos_i in enumerate(range(start, end + 1)):
        x = col / max(1, end - start)
        nucs = [(n, pos_nucs[(pos_i, n)]) for n in 'ACGTUN' if (pos_i, n) in pos_nucs]
        total = sum(c for _, c in nucs)
        y = 0.0
        
        for nuc, count in nucs:
            node_map[(pos_i, nuc)] = idx
            labels.append(f"P{pos_i+1}_{nuc} ({count})")
            colors.append(NUC_COLORS.get(nuc, '#808080'))
            x_pos.append(x)
            y_pos.append(y + count / total / 2)
            y += count / total
            idx += 1
    
    # Build links
    sources, targets, values, link_colors = [], [], [], []
    
    for (pos_i, src, tgt), count in transitions.items():
        if (pos_i, src) in node_map and (pos_i + 1, tgt) in node_map:
            sources.append(node_map[(pos_i, src)])
            targets.append(node_map[(pos_i + 1, tgt)])
            values.append(count)
            
            col = NUC_COLORS.get(src, '#808080')
            r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)
            link_colors.append(f'rgba({r},{g},{b},0.4)')
    
    # Create figure
    fig = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=10, line=dict(width=0.5), 
                  label=labels, color=colors, x=x_pos, y=y_pos),
        link=dict(source=sources, target=targets, value=values, color=link_colors)
    ))
    
    fig.update_layout(
        title="Nucleotide Transitions",
        font=dict(size=10),
        width=width,
        height=height,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def save_html(fig, filepath, width, height):
    """Save as scrollable HTML"""
    import plotly.io as pio
    plot_html = pio.to_html(fig, include_plotlyjs='cdn', full_html=False, 
                            config={'responsive': False, 'scrollZoom': True})
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Nucleotide Transitions</title>
    <style>
        body {{ margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; }}
        .scroll-box {{ 
            width: 100%; 
            height: 85vh; 
            overflow: scroll; 
            border: 2px solid #ddd; 
            background: white;
        }}
        .plot {{ 
            width: {width}px; 
            height: {height}px; 
            min-width: {width}px; 
            min-height: {height}px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <p><strong>📊 Scroll and drag to navigate</strong></p>
        <div class="scroll-box">
            <div class="plot">{plot_html}</div>
        </div>
    </div>
</body>
</html>'''
    
    with open(filepath, 'w') as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description='Sankey plot of nucleotide transitions')
    parser.add_argument('fasta', help='Input FASTA file')
    parser.add_argument('-o', '--output', help='Output HTML file')
    parser.add_argument('--range', nargs=2, type=int, metavar=('START', 'END'))
    parser.add_argument('--width', type=int, default=2000)
    parser.add_argument('--height', type=int, default=1200)
    args = parser.parse_args()
    
    print(f"Reading {args.fasta}...")
    sequences, seq_length = read_fasta(args.fasta)
    print(f"Loaded {len(sequences)} sequences of length {seq_length}")
    
    fig = make_sankey(sequences, seq_length, args.range, args.width, args.height)
    
    if args.output:
        save_html(fig, args.output, args.width, args.height)
        print(f"Saved to {args.output}")
    else:
        fig.show()

if __name__ == '__main__':
    main()