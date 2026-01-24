# 🎬 aSiReM Narrative Intelligence Engine

**A 9-Expert Multi-Agent System for Cinematic AI Video Production**

This engine orchestrates a team of 9 specialized AI agents to deliberate, plan, and generate high-quality video stories about AI for 15-year-olds, ensuring character consistency and narrative depth.

---

## 🏗️ Architecture

The system mimics a professional film studio production pipeline:

### The 9-Expert Team
| Expert | Role | Focus |
|--------|------|-------|
| **Sophia** | Director of Narrative Architecture | Story Arc & Emotion |
| **Marcus** | Visual Consistency Director | Character Design & Continuity |
| **Elena** | Youth Psychology Specialist | Audience Engagement (Gen Z) |
| **David** | AI Education Translator | Clarity of Concepts |
| **Aria** | Sound & Emotion Designer | Audio Atmosphere |
| **Theo** | Technical Feasibility Engineer | Veo3 Constraints |
| **Maya** | Cultural Resonance Specialist | Cinematic References |
| **Omar** | Ethical Narrative Advisor | Responsible AI Messaging |
| **Nadia** | Prompt Engineering Lead | Generative Prompts |

---

## 🚀 How to Run

### 1. Prerequisites
You must have your **Google/Gemini API Key** (with Veo3 access) set in your environment:

```bash
export GOOGLE_API_KEY="your-key-here"
```

### 2. Run the Demo (Simulation)
To seeing the agents deliberate without generating video:

```bash
python cold_azirem/narrative/demo.py
```

### 3. Generate a Full Episode
To run the full production pipeline (5-minute deliberation + video generation):

1. **Edit** `cold_azirem/narrative/demo.py`:
   - Set `deliberation_minutes = 5.0`
   - Ensure the API client is connected (in `factory.py`)

2. **Run**:
   ```bash
   python cold_azirem/narrative/demo.py
   ```

---

## 📂 Output

- **Transcripts**: `cold_azirem/narrative/output/deliberation_transcript.md`
- **Video Chunks**: Saved to `videogen_outputs/` (when enabled)
- **Story Bible**: `cold_azirem/narrative/ASIREM_STORY_BIBLE.md`

---

## 🧠 Core Features

1.  **Character Locking**: Automatic prompt injection for aSiReM's visual identity (bowler hat, amber eyes, etc.).
2.  **Deliberation Protocol**: Agents must discuss specifically for 5+ minutes to refine ideas before generation.
3.  **Cost Estimation**: Real-time calculation of Veo3 credit usage.
