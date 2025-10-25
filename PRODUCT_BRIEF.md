# ProjectTrace - Product Brief

**Antler Hackathon Submission | October 2025**

---

## The Problem

Every project generates thousands of emails and calendar events. **Nobody knows what actually happened.**

Project teams struggle to answer basic questions:
- When did we pivot strategy? 
- Who influenced key decisions?
- Which collaboration periods were most productive?
- When did knowledge transfer between team members?

Manual timeline reconstruction takes weeks. Collaboration patterns remain invisible. Learning from past projects is impossible.

---

## The Solution

**ProjectTrace** turns email + calendar data into instant project intelligence using a multi-agent AI system.

Drop in your data → Get complete project analysis in **7 seconds**.

### What It Does

**6 AI Agents analyze collaboration patterns simultaneously:**

🔥 **Burst Detector** - Finds intense collaboration periods  
🎯 **Milestone Finder** - Identifies key project events  
🔄 **Phase Mapper** - Detects strategic pivots using topic modeling  
💬 **Sentiment Analyzer** - Tracks communication patterns (12+ metrics)  
🏆 **Influence Scorer** - Ranks who actually drives decisions (PageRank)  
🤝 **Handoff Tracker** - Maps knowledge transfer between team members

**Zero configuration. Zero manual tagging. Just insights.**

---

## How It Works

```
Email + Calendar JSON → Graph Construction → 6 AI Agents → Interactive Dashboard
```

**Tech:** Python, NetworkX (graph engine), TF-IDF (topic modeling), Streamlit (dashboard)  
**Speed:** Analyzes 3+ years of project data in ~7 seconds  
**Output:** 12 data files + interactive 6-tab dashboard

---

## Proof: Real Project Analysis

**Dataset:** 3.67-year consulting project (Aug 2022 - Apr 2026)
- 47 events (27 emails + 20 meetings)
- 42 participants across 5+ organizations
- 1,340 days reconstructed automatically

**Results:**
- ✅ 7 collaboration bursts detected (66% avg confidence)
- ✅ 8 milestones identified (72.5% confidence) 
- ✅ 4 strategic pivots mapped (93% topic shift)
- ✅ 42 influence rankings calculated
- ✅ 38 team handoffs tracked
- ✅ Crisis periods auto-detected (12.8% of events)

**Impact:** Weeks of manual work → 7 seconds automated

---

## Why It's Different

| Feature | ProjectTrace | Existing Tools |
|---------|--------------|----------------|
| **Auto Timeline** | ✅ Complete | ❌ Manual only |
| **Phase Detection** | ✅ AI topic modeling | ❌ None |
| **Influence Mapping** | ✅ PageRank algorithm | ❌ None |
| **Cross-source** | ✅ Email + Calendar | ❌ Single source |
| **Zero Config** | ✅ Drop & go | ❌ Requires setup |

**Innovation:** First multi-agent system that builds a unified temporal graph from communication data.

---

## Target Market

**Who needs this:**
1. **Consulting Firms** - Analyze client project patterns, optimize team structures
2. **Enterprise PMOs** - Learn from completed projects, identify best practices  
3. **Startup Leaders** - Understand collaboration dynamics, spot bottlenecks
4. **HR/People Ops** - Map informal influence networks, plan succession

**Market Size:** $50B+ project management software market, $5B+ collaboration analytics segment

---

## Traction & Status

✅ **Production-ready** system (not a prototype)  
✅ **Tested** on real 1,340-day dataset  
✅ **Open source** - [github.com/Krut-in/ProjectTrace](https://github.com/Krut-in/ProjectTrace)  
✅ **3,000+ lines** of code across 20+ modules  
✅ **Full documentation** (1,593 lines of analysis)

**Try it:**
```bash
git clone https://github.com/Krut-in/ProjectTrace.git
./setup.sh && python src/main.py
streamlit run src/visualization/dashboard.py
```

---

## Business Model

**SaaS Pricing (Planned):**
- Free: 100 events/month
- Pro: $49/mo (1,000 events)
- Enterprise: $499/mo (unlimited + API)

**Revenue Streams:** Subscriptions, API access, consulting, white-label

---

## What's Next

**Immediate (Post-Hackathon):**
- Real-time monitoring (live email/calendar streams)
- Slack/Teams integration
- Predictive analytics (forecast next milestone)

**6-12 Months:**
- Multi-project benchmarking
- LLM-powered natural language queries
- Team composition recommendations
- API for third-party integrations

---

## The Ask

**Looking for:**
- Beta users (consulting firms, PMOs)
- Technical mentorship on scaling graph algorithms
- Potential partnerships with PM tool vendors

**Contact:** [@Krut-in](https://github.com/Krut-in) | [Your Email]

---

## Why This Matters

**Billions of emails and meetings happen daily. Almost none of it becomes organizational knowledge.**

ProjectTrace changes that. It's not just analytics—it's **automated project memory** that helps teams understand what actually happened, who drove it, and how to do it better next time.

**Built in 2025. Ready to ship. Let's turn communication data into competitive advantage.**
