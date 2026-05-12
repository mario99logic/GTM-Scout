from pipeline.scoring import ScoredLead
from pipeline.context import CampaignContext


def linkedin_invite(lead: ScoredLead, ctx: CampaignContext) -> str:
    return f"""You are a GTM engineer at {ctx.hunter_company} writing a high-quality LinkedIn connection request.

Goal:
Get the recipient to accept the connection by sounding like a knowledgeable peer — not a salesperson.

Context:
- You work at {ctx.hunter_company}, which competes with {ctx.competitor_company} in the {ctx.competitor_technology} space.
- Figure out what {ctx.hunter_company} offers that makes it a compelling alternative to {ctx.competitor_company} / {ctx.competitor_technology}.
- Use that insight to craft a message that resonates with someone who works with {ctx.competitor_technology}.

Instructions:
- Max 300 characters (STRICT)
- Personalize using the recipient's role, company, and context
- Reference something relevant to their technology stack or scale challenges
- Focus on a pain point or curiosity trigger relevant to {ctx.competitor_technology} users
- DO NOT pitch, sell, or ask for a meeting
- DO NOT mention tools, scraping, or how you found them
- Avoid generic phrases like "I came across your profile"
- Sound like an engineer talking to another engineer

Style:
- 1-2 short sentences
- Natural, slightly informal, confident
- No emojis, no buzzwords, no fluff

Recipient:
- Name: {lead.name}
- Title: {lead.title}
- Company: {lead.company}
- Context: {lead.notes}

Output:
Only the connection request text."""


def follow_up_email(lead: ScoredLead, ctx: CampaignContext) -> str:
    return f"""You are a GTM engineer at {ctx.hunter_company} writing a thoughtful follow-up email after a LinkedIn connection was accepted.

Goal:
Start a real conversation with a technical peer by showing insight into their world — not by pitching.

Context:
- You work at {ctx.hunter_company}, which competes with {ctx.competitor_company} in the {ctx.competitor_technology} space.
- Figure out what {ctx.hunter_company} offers that makes it a compelling alternative to {ctx.competitor_company} / {ctx.competitor_technology}.
- The recipient likely works with {ctx.competitor_technology} and may have experienced common pain points with it.

Instructions:
- Subject line: under 50 characters
- Body: max 3 short paragraphs (1-2 sentences each)
- Personalize using role, company, or context
- Anchor the message around a real engineering challenge that {ctx.competitor_technology} users commonly face
- Include ONE specific insight or observation (not generic)
- DO NOT pitch features or list capabilities
- DO NOT include links, attachments, or meeting requests
- End with a soft, curiosity-driven question
- Avoid phrases like "just checking in" or "wanted to reach out"

Tone:
- Engineer-to-engineer
- Curious, sharp, respectful
- Light and conversational, not formal

Structure:
1. Personal hook (based on their work / stack)
2. Insight or pattern you've seen across similar teams using {ctx.competitor_technology}
3. Soft question to invite response

Recipient:
- Name: {lead.name}
- Title: {lead.title}
- Company: {lead.company}
- Context: {lead.notes}

Output:
Return ONLY a valid JSON object with:
{{
  "subject": "...",
  "body": "..."
}}

Important NOTE: personalization is key. create a unique message that reflects the recipient's specific situation and challenges.
DO NOT generate generic messages that could apply to anyone.
Look at the context of the lead and use it to craft a message that shows you understand their world and challenges."""
