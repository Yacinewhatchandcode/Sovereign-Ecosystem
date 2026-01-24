#!/bin/bash
# Generate TECH-AESTHETIC Agent Videos
# Creates dark, code-like visualizations for each agent

echo "🎬 Generating TECH Agent Streams..."
echo "===================================="

cd ~/aSiReM/sovereign-dashboard

generate_agent_video() {
    local agent=$1
    local color=$2
    local label=$3
    
    local OUTPUT_DIR="outputs/agent_streams/$agent"
    local OUTPUT_FILE="$OUTPUT_DIR/idle_stream.mp4"
    mkdir -p "$OUTPUT_DIR"
    
    echo "📹 Generating TECH stream for: $agent"
    
    # Create a dark tech-style video with agent branding
    ffmpeg -y \
        -f lavfi -i "color=c=0x0a0a14:s=1280x720:d=10,format=yuv420p" \
        -vf "
            drawtext=text='◉ $agent':fontcolor=$color:fontsize=56:x=60:y=60:fontfile=/System/Library/Fonts/Menlo.ttc:shadowcolor=black:shadowx=3:shadowy=3,
            drawtext=text='$label':fontcolor=$color@0.6:fontsize=28:x=60:y=140:fontfile=/System/Library/Fonts/Menlo.ttc,
            drawtext=text='STATUS ACTIVE':fontcolor=$color@0.8:fontsize=22:x=60:y=200:fontfile=/System/Library/Fonts/Menlo.ttc,
            drawtext=text='────────────────────────────':fontcolor=$color@0.2:fontsize=20:x=60:y=240:fontfile=/System/Library/Fonts/Menlo.ttc,
            drawtext=text='UPTIME %{pts\:hms}':fontcolor=$color@0.5:fontsize=18:x=60:y=280:fontfile=/System/Library/Fonts/Menlo.ttc,
            drawtext=text='◆ SOVEREIGN LINK ◆':fontcolor=$color@0.7:fontsize=18:x=60:y=(h-60):fontfile=/System/Library/Fonts/Menlo.ttc,
            drawgrid=width=50:height=50:thickness=1:color=$color@0.03
        " \
        -t 10 -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
        "$OUTPUT_FILE" 2>/dev/null
    
    if [ -f "$OUTPUT_FILE" ]; then
        SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "   ✅ Created: $SIZE"
    else
        echo "   ❌ Failed"
    fi
}

# Generate for each agent with unique color and label
generate_agent_video "azirem" "0xff00ff" "STRATEGIC MASTER"
generate_agent_video "bumblebee" "0xffcc00" "EXECUTION MASTER"
generate_agent_video "spectra" "0xaa88ff" "KNOWLEDGE MASTER"
generate_agent_video "scanner" "0x00ff88" "DISCOVERY AGENT"
generate_agent_video "classifier" "0xffaa00" "TAGGING AGENT"
generate_agent_video "extractor" "0x00aaff" "CODE ANALYST"
generate_agent_video "summarizer" "0xff88ff" "NL GENERATOR"
generate_agent_video "researcher" "0x00ffff" "WEB SEARCH"
generate_agent_video "architect" "0xff8844" "SYSTEM DESIGN"
generate_agent_video "qa" "0x88ff88" "TESTING"
generate_agent_video "devops" "0xff6666" "DEPLOYMENT"
generate_agent_video "security" "0x44ff44" "PROTECTION"
generate_agent_video "evolution" "0x6688ff" "SELF-IMPROVEMENT"

echo ""
echo "===================================="
echo "✅ TECH Agent streams ready!"
ls outputs/agent_streams/*/idle_stream.mp4 2>/dev/null | wc -l | xargs echo "Total streams:"
echo "Refresh dashboard at http://localhost:8082"
echo "===================================="
