#!/bin/bash
# Create optimized, small MP4 loops for agent avatars

echo "🎬 Creating Optimized Agent Streams (100x100px)"
echo "=============================================="

cd ~/aSiReM/sovereign-dashboard

AGENTS=("scanner" "classifier" "extractor" "summarizer" "researcher" "azirem" "bumblebee" "spectra" "architect" "qa" "devops" "security" "evolution")

for agent in "${AGENTS[@]}"; do
    OUTPUT_DIR="outputs/agent_streams/$agent"
    OUTPUT_FILE="$OUTPUT_DIR/idle_stream.mp4"
    
    echo "📹 Optimizing stream for: $agent"
    
    # Create a small, optimized 100x100px video loop
    ffmpeg -y -i assets/bg-loop.mp4 \
        -vf "scale=100:100:force_original_aspect_ratio=decrease,pad=100:100:(ow-iw)/2:(oh-ih)/2,fps=15" \
        -c:v libx264 -preset ultrafast -crf 28 \
        -pix_fmt yuv420p -an \
        -t 3 \
        "$OUTPUT_FILE" 2>/dev/null
        
    if [ -f "$OUTPUT_FILE" ]; then
        SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        echo "   ✅ Created: $SIZE (100x100px, 15fps, 3sec loop)"
    fi
done

echo ""
echo "=============================================="
echo "✅ All agent streams optimized!"
echo ""
echo "Streams:"
ls -lh outputs/agent_streams/*/idle_stream.mp4 | awk '{print "  " $9 " - " $5}'
echo ""
echo "Next: Refresh dashboard (Cmd+Shift+R)"
echo "=============================================="
