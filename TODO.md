# TODO

## ✅ COMPLETED: Founding PM Logic Fix

### ✅ Problem Solved
- **Issue**: Aurora was incorrectly skipped due to "redundant founding/startup theme" logic
- **Root Cause**: Rigid theme checking logic that should be user-specific preference, not hardcoded system logic
- **Expected**: Enact, Aurora, Meta for utility industry job with 7 years experience and Senior Product experience

### ✅ Solution Implemented
- **Removed problematic logic**: Commented out founding PM theme checking
- **Simplified selection**: Now picks top 3 case studies by score
- **Maintained functionality**: Kept Samsung logic and all scoring multipliers
- **Added comprehensive tests**: Created test suite to verify Aurora is now selected

### ✅ Results Verified
- **Selection**: Meta (4.4), Aurora (2.4), Enact (0.0) ✅
- **Aurora now selected**: No longer skipped due to theme logic ✅
- **Diverse mix**: Founding story (Enact), scaleup story (Aurora), public company story (Meta) ✅
- **All tests pass**: Comprehensive test suite validates fix ✅

### ✅ Documentation Updated
- **README.md**: Added enhanced case study selection section
- **PR Template**: Created comprehensive template for future PRs
- **Tests**: Added `test_founding_pm_fix.py` with full test coverage

## 🔄 CURRENT PRIORITY: Enhanced Case Study Scoring MVP

### 🎯 MVP Goal
Enhance case study selection with LLM semantic matching, PM levels integration, and work history context preservation.

### 📋 Phase 1: Fix Current Scoring System - ✅ COMPLETED
**Goal**: Restore proper keyword matching and integrate LLM job parsing results

**Tasks:**
- ✅ **Fix broken scoring** - restore base keyword matching that was broken
- ✅ **Test current system** - verify Enact, Aurora, Meta get proper scores (not 0.0)
- ✅ **Add debug logging** - track scoring decisions for transparency
- ✅ **Add missing tags** - add org_leadership, strategic_alignment, people_development to case studies
- ✅ **Add default scoring** - +2 points for tags that don't fit predefined categories
- ✅ **Test with Duke Energy JD** - verify better keyword matching
- ✅ **Fix founding PM logic** - remove problematic theme checking that was skipping Aurora

**Success Criteria:**
- ✅ Case studies get proper scores (not 0.0)
- ✅ Enact: 3.0 → 7.3 points (3 matches)
- ✅ Aurora: 3.0 → 7.3 points (3 matches) 
- ✅ Meta: 1.0 → 4.4 points (1 match)
- ✅ Debug logging shows scoring decisions clearly
- ✅ Aurora is now correctly selected instead of being skipped

### 📋 Phase 2: PM Levels Integration - ✅ COMPLETED
**Goal**: Add light PM levels scoring to prioritize level-appropriate competencies

**Tasks:**
- ✅ **Create PM level competencies** mapping in `data/pm_levels.yaml`
- ✅ **Add level-based scoring** - bonus points for level-appropriate competencies
- ✅ **Implement simple scoring**:
  ```python
  def add_pm_level_scoring(base_score, case_study, job_level):
      level_competencies = get_level_competencies(job_level)
      level_matches = count_matching_tags(case_study.tags, level_competencies)
      return base_score + (level_matches * 2)
  ```
- ✅ **Track selection patterns** - log which case studies selected for each level
- ✅ **Create analytics** - simple metrics on level-competency matching
- ✅ **User feedback collection** - allow users to rate case study relevance

**Success Criteria:**
- ✅ L5 jobs prioritize L5 competencies (org_leadership, strategic_alignment, etc.)
- ✅ PM level scoring adds meaningful bonus points (up to +12.0 for L5 jobs)
- ✅ Selection patterns are tracked for future improvement
- ✅ Analytics collection is implemented

**Results:**
- **Job Level Detection**: 4/5 correct (80% accuracy)
- **Level Competencies**: L2(10), L3(14), L4(20), L5(27), L6(32) competencies
- **Scoring Impact**: L5 jobs get +12.0 bonus for Meta, +12.0 for Enact, +8.0 for Aurora
- **Selection Changes**: PM level scoring significantly changes case study selection order

### 📋 Phase 3: Work History Context Enhancement - ✅ COMPLETED
**Goal**: Use LLM to preserve parent-child work history relationships

**Tasks:**
- ✅ **Create context enhancement function**:
  ```python
  def enhance_case_study_context(case_study, parent_work_history):
      # Single LLM call to preserve parent-child relationship
      # Returns enhanced tags that include both specific and inherited context
  ```
- ✅ **Add parent work history tags** to case study scoring
- ✅ **Test context preservation** - verify Enact gets cleantech context from parent
- ✅ **Implement tag inheritance** - case studies inherit relevant parent tags
- ✅ **Add semantic tag matching** - "internal_tools" matches "platform" and "enterprise_systems"
- ✅ **Create tag hierarchy** - specific tags (case study) + inherited tags (parent)

**Success Criteria:**
- ✅ Case studies maintain parent work history context
- ✅ Enact gets cleantech context from parent work history
- ✅ Tag inheritance works correctly
- ✅ Semantic tag matching improves matching accuracy

**Results:**
- **Parent Context Found**: 4/4 case studies (100% success rate)
- **Inherited Tags**: 2/4 case studies got leadership inheritance (Aurora, Samsung)
- **Semantic Tags**: 4/4 case studies got semantic tag enhancement
- **Average Confidence**: 0.90 (excellent confidence scores)
- **Tag Enhancement**: Significant improvement in tag coverage
- **Key Enhancements**:
  - Enact: Added mobile, revenue_growth, expansion, scaling, b2c tags
  - Aurora: Added leadership inheritance, scaleup, revenue_growth, expansion tags
  - Meta: Added platform, ai_ml, productivity, operations, enterprise_systems tags
  - Samsung: Added leadership inheritance, ai_ml, revenue_growth, consumer, expansion tags

### 📋 Phase 4: Hybrid LLM + Tag Matching
**Goal**: Implement two-stage selection with LLM semantic scoring for top candidates

**Tasks:**
- [ ] **Stage 1: Tag-based filtering** - fast pre-filtering with enhanced tags
- [ ] **Stage 2: LLM semantic scoring** - only for top 5-10 candidates
- [ ] **Implement hybrid approach**:
  ```python
  def select_case_studies(job_keywords, job_level):
      # Stage 1: Tag filtering (fast)
      candidates = filter_by_tags(case_studies, job_keywords)
      
      # Stage 2: LLM scoring (top candidates only)
      scored = llm_semantic_score(candidates[:10], job_keywords, job_level)
      
      return select_top_3(scored)
  ```
- [ ] **Create semantic scoring prompt**:
  ```
  Job: {job_description}
  Case Study: {case_study}
  
  Rate relevance (1-10) and explain why this case study fits this job.
  Consider: role level, industry, skills, company stage, business model.
  ```
- [ ] **Add confidence scoring** - LLM provides confidence in its reasoning
- [ ] **Implement fallback** - if LLM fails, use tag-based scoring

**Success Criteria:**
- Two-stage selection works correctly
- LLM semantic scoring improves selection quality
- System is fast (<2 seconds for case study selection)
- LLM cost is controlled (<$0.10 per job application)

### 📋 Phase 5: Testing & Validation
**Goal**: Comprehensive testing and user feedback integration

**Tasks:**
- [ ] **Test with multiple job types** - L2 startup, L5 enterprise, L4 growth
- [ ] **Validate PM level matching** - ensure L5 jobs prioritize L5 competencies
- [ ] **Test context preservation** - verify work history context is maintained
- [ ] **Performance testing** - ensure hybrid approach is fast enough
- [ ] **Add user rating system** - let users rate case study relevance
- [ ] **Collect feedback data** - track which selections users approve/reject
- [ ] **Implement learning loop** - use feedback to improve PM level definitions

**Success Criteria:**
- All job types work correctly
- PM level matching is validated
- Context preservation works
- Performance meets requirements
- User feedback is collected and used

## 🔄 NEXT PRIORITY: Manual Parsing Cleanup

### Immediate Next Steps:
1. **Performance Tracking**: Implement metrics to compare LLM parsing vs manual parsing
2. **Google Drive Fix**: Re-enable Google Drive with correct folder ID
3. **Gap Analysis Fix**: Resolve JSON parsing error in gap analysis
4. **User Interface**: Add PM level selection to job search preferences
5. **Clean Up Manual Parsing**: Remove or deprecate manual parsing code since LLM parsing is working

### Manual Parsing Cleanup Tasks:
- [ ] **Remove manual parsing methods** from `cover_letter_agent.py` (keep fallback only)
- [ ] **Update documentation** to reflect LLM parsing as primary method
- [ ] **Remove manual parsing tests** that are no longer needed
- [ ] **Clean up legacy code** in `_parse_job_description_manual()` methods
- [ ] **Update comments** to reflect LLM parsing as the standard approach

## 🚀 Future Enhancements

### Advanced LLM Integration:
- [ ] **Multi-modal matching** - consider case study content beyond tags
- [ ] **Dynamic prompt engineering** - optimize prompts based on job type
- [ ] **Batch LLM processing** - process multiple case studies in single call
- [ ] **Semantic similarity caching** - cache LLM results for similar jobs

### Advanced PM Levels:
- [ ] **Competency gap analysis** - identify missing competencies for target level
- [ ] **Level progression tracking** - suggest case studies for career advancement
- [ ] **Industry-specific leveling** - different competencies for different industries
- [ ] **Machine learning integration** - learn from user feedback to improve leveling

### Advanced Analytics:
- [ ] **Selection pattern analysis** - understand which combinations work best
- [ ] **A/B testing framework** - test different scoring algorithms
- [ ] **Predictive modeling** - predict which case studies will be most effective
- [ ] **User behavior analysis** - learn from how users interact with selections 