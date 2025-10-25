#!/bin/bash
# Quick demo script for Email+Calendar Graph System

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Email+Calendar Graph System - Quick Demo                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Running setup..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo ""
else
    source venv/bin/activate
fi

# Run main analysis
echo "▶️  Running analysis pipeline..."
echo ""
python src/main.py
echo ""

# Generate visualizations
echo "▶️  Generating visualizations..."
echo ""
python src/visualization/generate_plots.py
echo ""

# Display results
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   📊 Results Generated                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📄 Text Reports:"
echo "   • outputs/summary_report.txt"
echo "   • outputs/analysis.log"
echo ""
echo "📊 Data Files:"
echo "   • outputs/timeline.csv"
echo "   • outputs/collaboration_bursts.csv"
echo "   • outputs/participant_stats.csv"
echo "   • outputs/graph_stats.json"
echo ""
echo "📈 Visualizations:"
echo "   • outputs/visualizations/timeline.png"
echo "   • outputs/visualizations/participants.png"
echo "   • outputs/visualizations/bursts.png"
echo "   • outputs/visualizations/statistics.png"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎯 Quick Actions                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "View summary report:"
echo "  cat outputs/summary_report.txt"
echo ""
echo "Open visualizations:"
echo "  open outputs/visualizations/"
echo ""
echo "Explore data:"
echo "  open outputs/timeline.csv"
echo ""
echo "✅ Demo complete!"
