# RLTX POPULOUS BUILD MISSION

## OBJECTIVE
Build a production-grade Decision Intelligence demo that makes Fortune 500 leaders immediately want to integrate with their data.

## CONTEXT
Read `CLAUDE.md` for the complete specification. Key points:

1. **The Demo Must Sell**: This isn't a prototype. It's a proof of concept for $500K+ enterprise deals.

2. **The Magic Moment**: Real-time predictions as users type survey questions. AI suggestions. Bias detection. Agent interviews. Execution plans.

3. **The Differentiator**: "Aaru predicts. RLTX decides." We output execution plans with dates and contingencies, not just probabilities.

## PRIORITY ORDER

### P0 - Critical (Do First)
1. Survey Builder with real-time predictions (3-panel layout)
2. AI Suggestions for questions
3. Bias Detection warnings
4. Audience generation with progress
5. Agent interview (chat)
6. Decision Layer output

### P1 - Required
7. Projects Dashboard
8. Audiences page (master-detail)
9. Templates library
10. Results visualization

### P2 - Nice to Have
11. Team Activities feed
12. Smart Alerts

## TECHNICAL CONSTRAINTS

1. **Performance**:
   - Predictions: <500ms
   - Generation: <30s
   - Page loads: <2s

2. **UI**: Match Figma designs exactly (see `/rltx figma images/`)

3. **Backend**: Extend existing FastAPI, don't break existing features

4. **Frontend**: Use existing Next.js setup in `populous-frontend/`

## SUCCESS CRITERIA

- [ ] Survey Builder works with real-time predictions
- [ ] AI suggestions appear contextually
- [ ] Bias detection catches leading questions
- [ ] Can generate 500 synthetic profiles in <30s
- [ ] Can chat with any synthetic profile
- [ ] Decision output shows execution plan with dates
- [ ] All Figma screens implemented
- [ ] Frontend connected to backend
- [ ] Demo scenarios loadable

## BUILD SEQUENCE

Week 1:
1. Survey prediction engine (backend)
2. Bias detection + AI suggestions (backend)
3. Survey Builder UI (frontend)
4. Real-time prediction integration

Week 2:
5. Stanford agent architecture
6. Agent chat functionality
7. Decision Layer
8. All remaining pages

Week 3:
9. Demo scenarios
10. Testing + polish
11. Production deployment

## REFERENCE FILES

- `CLAUDE.md` - Complete specification
- `/rltx figma images/` - UI designs (12 screenshots)
- `/docs/RLTX-Decision-Layer-Build-Guide.md` - Architecture reference
- `/docs/STRATEGIC-SYNTHESIS.md` - Value proposition

## START HERE

1. Read `CLAUDE.md` thoroughly
2. Review Figma images
3. Understand existing code in `rltx-populous/backend/` and `populous-frontend/`
4. Begin with Survey Prediction Engine (`backend/engine/survey_predictor.py`)

Build until all success criteria are met.
