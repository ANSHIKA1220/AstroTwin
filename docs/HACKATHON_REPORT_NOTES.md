# AstroTwin — Hackathon Report Notes

These are structured internal drafting notes. They intentionally do not fabricate research or citations. Any externally verifiable statement is marked **[SOURCE REQUIRED]**.

## 1. Executive Summary

AstroTwin proposes a persistent astrology identity for AstroLive. Instead of treating consultation as an isolated purchase, it connects a user’s goals, life events, questions and reflections into a loop of daily relevance, shareable discovery and well-timed human consultation.

## 2. AstroLive Product Teardown

- Document the current call/chat discovery, pricing, booking and repeat-use journey. **[SOURCE REQUIRED]**
- Verify current retention mechanisms, loyalty programs and astrologer marketplace positioning. **[SOURCE REQUIRED]**
- Identify where context is lost between sessions through firsthand product review. **[SOURCE REQUIRED]**

## 3. Problem Statement

Transactional consultation marketplaces may struggle to create daily reasons to return, preserve longitudinal user context and acquire users through product-native sharing. Validate the size and frequency of these behaviors with research. **[SOURCE REQUIRED]**

## 4. User Personas

- The milestone navigator: career, exam or project deadline approaching.
- The reflective regular: wants a light daily ritual and pattern journal.
- The relationship explorer: interested in conversation prompts with another person.
- The high-intent seeker: facing a major decision and open to expert consultation.

Personas are hypotheses and require customer interviews. **[SOURCE REQUIRED]**

## 5. Existing Journey

Discover astrologer → compare profile → call/chat → pay → receive guidance → leave. Confirm against the live product and user interviews. **[SOURCE REQUIRED]**

## 6. Proposed Journey

Profile → Daily Guidance → Life Event → Reflection → Memory → More Personal Guidance → Human Consultation → Return.

## 7. AstroTwin

- Persistent context across goals, events, questions and reflections.
- Visible “Using X memories” feedback makes personalization legible.
- User-controlled memory CRUD supports trust and correction.

## 8. Cosmic Daily

- Stable daily scores create a repeatable ritual.
- One recommended action prioritizes behavior over vague prediction.
- Mood and resonance check-ins feed subjective alignment history.

## 9. AstroCircle

- Compatibility categories map to friendship, relationships, co-founders, roommates and teams.
- Public pages carry a strong “Create your own AstroTwin” acquisition CTA.
- Validate likely share rate and conversion through experiments. **[SOURCE REQUIRED]**

## 10. AstroConnect

- Detect high-intent themes and recommend a relevant specialization.
- Keep initial guidance useful before offering a consultation.
- Never route emergencies or guaranteed-outcome questions into astrology advice.

## 11. Architecture

Next.js App Router frontend; FastAPI REST backend; SQLAlchemy persistence; SQLite locally with a PostgreSQL-compatible database URL; isolated deterministic scoring, compatibility, AI and intent services.

## 12. Growth Flywheel

Profile → guidance → reflection → memory → personalization → retention → more context. AstroCircle adds a second loop: user → report → share → friend → new profile.

## 13. Revenue Model

- Per-minute call/chat commissions.
- Potential premium persistent insights or advanced reports; willingness to pay requires validation. **[SOURCE REQUIRED]**
- Potential subscription packaging requires pricing research. **[SOURCE REQUIRED]**

## 14. Success Metrics

- Retention: D1, D7, guidance opens, check-in completion.
- Engagement: questions/user, memories/user, life events/user.
- Virality: invites/user, open-to-create conversion, `K = invites × conversion`.
- Monetization: recommendation → profile → booking funnel.

Targets must come from baseline data or experiments. **[SOURCE REQUIRED]**

## 15. Scalability

- Stateless API service; move from SQLite to managed PostgreSQL.
- Replace deterministic engine through stable provider interfaces.
- Summarize and retrieve memories by importance/relevance as the profile grows.
- Add event queues for analytics and notification delivery.

## 16. Risks

- Sensitive personal-context handling and user consent.
- Overclaiming predictive accuracy.
- Poor memory retrieval creating uncanny or irrelevant responses.
- Marketplace recommendations that feel exploitative at vulnerable moments.
- Public compatibility links exposing information without clear consent.

## 17. Responsible Design

- Use “guidance,” “reflection,” “patterns” and “personal resonance.”
- Display a quiet entertainment/exploration disclaimer.
- Block medical, legal, self-harm and guaranteed financial routing.
- Let users inspect, edit and delete stored memories.

## 18. Future Roadmap

1. Customer interviews and baseline analytics. **[SOURCE REQUIRED]**
2. Production authentication, consent controls and PostgreSQL.
3. Real astrology calculation provider with documented methodology.
4. LLM evaluation set for memory relevance and safety.
5. Real availability, payment, call/chat and notification systems.
6. A/B tests for daily prompts and public-share conversion.

## 19. AI Tools Used

See `AI_DISCLOSURE.md`. Add exact model names and versions before submission.

## 20. Sources Still Requiring External Verification

- AstroLive current product features, scale, pricing and marketplace flow. **[SOURCE REQUIRED]**
- Astrology app/consultation category market size and growth. **[SOURCE REQUIRED]**
- User retention benchmarks for consumer wellness and astrology products. **[SOURCE REQUIRED]**
- Share and invite conversion benchmarks. **[SOURCE REQUIRED]**
- Customer interview findings and willingness-to-pay evidence. **[SOURCE REQUIRED]**
- Applicable privacy, advertising and consumer-protection requirements in launch markets. **[SOURCE REQUIRED]**
