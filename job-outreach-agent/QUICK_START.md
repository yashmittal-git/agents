# Quick Start - Job Outreach Agent v2.0

## The Easy Way (Same as Before!)

### 1. Activate Environment

```bash
cd /Users/yash/Documents/agents/job-outreach-agent
source ../venv/bin/activate
```

### 2. Run with Screenshot or Text File

```bash
# With a screenshot
python job_outreach_cli.py /path/to/job_screenshot.png

# With a text file
python job_outreach_cli.py /path/to/job_posting.txt
```

That's it! The CLI will:
1. ✅ Extract job info from your image/text (via extraction-agent using GPT-4o Vision)
2. ✅ Research the company (via research-agent)
3. ✅ Match with your profile
4. ✅ Intelligently recommend email vs LinkedIn
5. ✅ Generate personalized content (via content-agent)
6. ✅ Show you the draft
7. ✅ Ask for your approval
8. ✅ Send email (via email-agent) or provide LinkedIn instructions (via linkedin-agent)

## Complete Example

```bash
# Navigate to directory
cd /Users/yash/Documents/agents/job-outreach-agent

# Activate venv
source ../venv/bin/activate

# Run with your screenshot
python job_outreach_cli.py ~/Downloads/job_screenshot.png
```

**Output you'll see:**

```
============================================================
Job Outreach Agent - Full Workflow
============================================================

📋 Step 1: Extracting job information...
📸 Extracting job info from image: job_screenshot.png
✓ Extracted: Anthropic - Senior Software Engineer

🤖 Step 2: Initializing orchestrator...

🎯 Step 3: Processing job application...
   - Researching company
   - Matching your experience
   - Recommending best channel
   - Generating personalized content

============================================================
Processing Job Application
============================================================
Company: Anthropic
Role: Senior Software Engineer
============================================================

📊 Researching company...
✓ Research complete: growth stage

🎯 Matching experience...
✓ Match score: 9/10

🤔 Analyzing best outreach channel...
✓ Recommended: EMAIL
  Reason: Direct email address available

✍️  Creating email content...
✓ Content created

💾 Draft saved: outreach_drafts/20260215_143000_Anthropic.json

============================================================
OUTREACH STRATEGY
============================================================

Channel: EMAIL
Confidence: 90%
Reason: Direct email address available

✓ This channel supports automatic sending

Subject: Application for Senior Software Engineer at Anthropic

Body:
------------------------------------------------------------
Dear Hiring Team,

I was excited to discover the Senior Software Engineer role at
Anthropic. Your work in AI safety deeply resonates with my experience
building production AI systems at scale.

At Convin.AI, I've led the development of an AI Voicebot platform
handling 300K+ automated calls daily with sub-second latency. This
involved implementing RAG-based knowledge systems and achieving 45%
cost reduction in TTS/LLM operations through strategic optimization.

[... full personalized email ...]

Best regards,
Yash Mittal
mittal.yash2000@gmail.com
+91-9756251002
LinkedIn: linkedin.com/in/yashmittal-in
Portfolio: https://yashmittal.co.in
------------------------------------------------------------

============================================================
📧 Step 4: Review and Approve
============================================================

✓ Email draft ready to send

Draft saved to: outreach_drafts/20260215_143000_Anthropic.json

Review the email above.

Send this email? (yes/no): yes

📤 Sending email...

✓ Email sent successfully!

============================================================
✅ Workflow complete!
============================================================
```

## If LinkedIn is Recommended Instead

If the job has LinkedIn but no email:

```
============================================================
OUTREACH STRATEGY
============================================================

Channel: LINKEDIN
Confidence: 85%
Reason: No email found. Recruiter active on LinkedIn

⚠ This channel requires manual action

Follow these steps:
  1. Go to: linkedin.com/in/jane-recruiter
  2. Click 'Connect' or 'Message' button
  3. Copy and paste the message below:
  ...

============================================================
MESSAGE TO SEND:
============================================================
Hi Jane,

I came across the Senior Engineer role at Anthropic and was
immediately drawn to your work in AI safety...

[... personalized LinkedIn message ...]
============================================================

Tips:
  • LinkedIn messages work best 9-11 AM on weekdays
  • Connection requests limited to 300 characters
  • Follow up after 3-5 days if no response

============================================================
📧 Step 4: Review and Approve
============================================================

⚠️  This channel requires manual action

Draft saved to: outreach_drafts/20260215_143000_Anthropic.json

Follow the instructions above to complete the outreach
```

## Your Workflow

### Before (Old Version)
```bash
cd /Users/yash/Documents/job-outreach-agent
source venv/bin/activate
python generate_email.py job.png image
python send_email.py email_drafts/file.json
```

### Now (New Version)
```bash
cd /Users/yash/Documents/agents/job-outreach-agent
source ../venv/bin/activate
python job_outreach_cli.py job.png
# That's it! It does everything in one command
```

## What Changed?

### Same
- ✅ Screenshot/text input support
- ✅ GPT-4o extraction
- ✅ Company research
- ✅ Experience matching
- ✅ Personalized email generation
- ✅ Gmail sending with approval
- ✅ Draft saving

### New/Better
- ✨ **Intelligent channel recommendation** (email vs LinkedIn)
- ✨ **LinkedIn support** (with manual guidance)
- ✨ **One command** workflow (no separate generate/send steps)
- ✨ **Modular architecture** (4 reusable agent services)
- ✨ **Smart decision-making** (analyzes role, company, available contacts)

## Configuration

Your profile is automatically loaded from `../.env`:

```bash
USER_NAME=Yash Mittal
USER_EMAIL=mittal.yash2000@gmail.com
USER_PHONE=+91-9756251002
USER_LINKEDIN=linkedin.com/in/yashmittal-in
USER_PORTFOLIO=https://yashmittal.co.in
```

The CLI uses your AI Voicebot achievements automatically:
- Built AI Voicebot platform with sub-second latency
- Scaled to 300K+ automated calls/day
- 45% cost reduction in TTS/LLM operations
- Led team of 4 engineers
- AWS to OCI migration (50% cost savings)

## Troubleshooting

### "credentials.json not found"

Gmail credentials need to be in the parent directory:

```bash
ls -la /Users/yash/Documents/agents/credentials.json
```

If missing, copy from old location:
```bash
cp /Users/yash/Documents/job-outreach-agent/credentials.json /Users/yash/Documents/agents/
```

### "OPENAI_API_KEY not found"

Check your .env file:
```bash
cat /Users/yash/Documents/agents/.env | grep OPENAI_API_KEY
```

## Advanced Usage

### Process Multiple Jobs

```bash
for job in ~/Downloads/job_*.png; do
    python job_outreach_cli.py "$job"
done
```

### Save Draft Without Sending

The script always saves a draft first. You can review and send later using the orchestrator.

### Use Different User Profile

Edit `job_outreach_cli.py` and modify the `user_profile` dictionary.

## Files Created

- `outreach_drafts/` - Saved drafts (auto-created)
- `outreach_drafts/YYYYMMDD_HHMMSS_Company.json` - Each draft

## Need Help?

- See full example: `python example_usage.py`
- See README: `cat README.md`
- See architecture: `cat ../COMPLETE_REFACTORING_SUMMARY.md`

---

**Quick Start Summary**: Just run `python job_outreach_cli.py <screenshot.png>` and follow the prompts!
