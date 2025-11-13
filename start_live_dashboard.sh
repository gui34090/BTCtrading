#!/bin/bash
# Start the BTC/USDT Smart Money Live Dashboard

echo "=================================================="
echo "  BTC/USDT Smart Money Live Dashboard"
echo "=================================================="
echo ""
echo "Starting web server..."
echo "The dashboard will open in your browser automatically."
echo ""
echo "Controls:"
echo "  - Change timeframe and settings in the sidebar"
echo "  - Enable 'Auto Refresh' for live updates"
echo "  - Press Ctrl+C to stop"
echo ""
echo "=================================================="
echo ""

streamlit run btc_live_dashboard.py --server.port 8501 --server.address 0.0.0.0
