You are a senior system architect. Produce a clear, actionable High Level Design (HLD) for the given PRD.

Target the output for an engineering manager building an MVP. 
Use concise, professional language. Keep sections and headings exactly as shown. Include sample Postgres schema snippets where relevant and call out key tradeoffs. 
Cover infrastructure, data model, pipeline, LLM usage, personalization approach, delivery, testing, monitoring, security, risks, phased roadmap, and deliverables.

INPUT: {PASTE YOUR PRD HERE}
[Replace this with your PRD Content]
- PRODUCT_NAME: "{PRODUCT_NAME}"
- ABSTRACT / PRD: """{PRD_TEXT}"""
- TECH_STACK: {TECH_STACK}   # e.g. Python, Streamlit, Supabase, groqcloud gptoss LLM
- KPI_TABLE: {KPI_TABLE}     # e.g. mapping of goal to metric to question
- MVP_CONSTRAINTS: {MVP_CONSTRAINTS}  # any constraints like latency, cost limits, privacy rules
[Replace this with your PRD Content]

OUTPUT FORMAT:
Start with a short one paragraph system overview. Then provide these numbered sections with headings exactly as below:

# 1. System Overview
- Purpose
- Core components (bulleted list)
- Users
- KPI mapping (small table or short list)

# 2. Logical Architecture (textual diagram)
Provide a simple ASCII or textual diagram showing major components and data flow.

# 3. Data model (Supabase / Postgres schema examples)
- List main tables with columns
- Include optional pgvector usage and a small SQL snippet to create a representative table

# 4. Pipeline: daily flow (MVP)
Step by step flow of ingestion, processing, summarization, ranking, delivery, and feedback.

# 5. Integration details
- LLM integration details and parameters
- Auth and DB notes
- UI integration notes

# 6. Prompt design (example)
- Provide system prompt and user prompt examples for summarization or other LLM tasks
- Include expected JSON output schema

# 7. APIs (minimal set)
List public and internal endpoints with purpose.

# 8. Deployment, scaling and infra
- MVP hosting suggestions
- Scaling notes and cost controls

# 9. Monitoring and observability
List key metrics, alerting triggers, and logging recommendations.

# 10. Security, privacy and compliance
- Auth, data retention, GDPR notes, secure secrets handling

# 11. Testing & QA
- Offline and online testing plus automated tests

# 13. Risks and mitigations
- Short table mapping risk to mitigation

# 14. Deliverables checklist for your engineering team
- Actionable engineering deliverables

Include code blocks for SQL and prompt examples.
Keep it practical and actionable. Now produce the HLD for the input above.
