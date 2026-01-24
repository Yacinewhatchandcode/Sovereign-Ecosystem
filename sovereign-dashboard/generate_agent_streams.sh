#!/bin/bash
# Generate MP4 streams for all agents

echo "🎬 Generating Agent MP4 Streams..."
echo "=================================="

cd ~/aSiReM/sovereign-dashboard

AGENTS=("scanner" "classifier" "extractor" "summarizer" "researcher" "azirem" "bumblebee" "spectra" "architect" "qa" "devops" "security" "evolution")

for agent in "${AGENTS[@]}"; do
    OUTPUT_DIR="outputs/agent_streams/$agent"
    OUTPUT_FILE="$OUTPUT_DIR/idle_stream.mp4"
    
    if [ ! -f "$OUTPUT_FILE" ]; then
        echo "📹 Generating stream for: $agent"
        
        # Generate a looping video with agent name overlay
        ffmpeg -y -loop 1 -i assets/bg-loop.mp4 \
            -vf "drawtext=text='$agent':fontcolor=cyan:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/System/Library/Fonts/SFNS.ttf" \
            -t 5 -c:v libx264 -preset ultrafast -pix_fmt yuv420p \
            "$OUTPUT_FILE" 2>/dev/null
            
        if [ -f "$OUTPUT_FILE" ]; then
            echo "   ✅ Created: $(ls -lh $OUTPUT_FILE | awk '{print $5}')"
        else
            # Fallback: just copy the base loop
            cp assets/bg-loop.mp4 "$OUTPUT_FILE"
            echo "   ℹ️  Copied base loop"
        fi
    else
        echo "✓ Stream exists for: $agent"
    fi
done

echo ""
echo "=================================="
echo "✅ Agent streams ready!"
echo ""
echo "Streams created in: outputs/agent_streams/"
ls -lh outputs/agent_streams/*/idle_stream.mp4 2>/dev/null | wc -l | xargs echo "Total streams:"
echo ""
echo "Next: Refresh dashboard at http://localhost:8082/index.html"
echo "=================================="
