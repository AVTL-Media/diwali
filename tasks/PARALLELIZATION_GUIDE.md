# Multi-Agent Parallelization Guide

## Overview

This guide provides coordination strategies for multiple agents working in parallel on the Diwali Projection System refactoring.

## Maximum Parallelization by Phase

| Phase | Weeks | Max Agents | Task Files |
|-------|-------|------------|------------|
| **Phase 1** | 1-2 | **3 agents** | phase1_task1_config_manager.md<br>phase1_task2_asset_manager.md<br>phase1_task3_error_handling.md |
| **Phase 2** | 2-3 | **3 agents** | phase2_task1_test_infrastructure.md<br>phase2_tests_parallel.md (3 sub-tasks) |
| **Phase 3** | 4-5 | **1 agent** ⚠️ | phase3_sequential.md |
| **Phase 4** | 6-8 | **4 agents** | phase4_parallel_components.md (4 components) |
| **Phase 5** | 9 | **4 agents** | phase5_parallel_refactoring.md (4 components) |
| **Phase 6** | 10-11 | **2 agents** | phase6_parallel_performance.md (2 tracks) |

## Phase-by-Phase Strategy

### Phase 1: Foundation (Weeks 1-2) - 3 Agents

**Parallel Tasks:**

- **Agent A**: ConfigManager (Week 1) → Error Handling (Week 2)
- **Agent B**: AssetManager (Week 1) → Test Infrastructure (Week 2)
- **Agent C**: Can assist with testing or documentation

**Dependencies:**
- Tasks 1 & 2 are fully independent (Week 1)
- Task 3 requires Tasks 1 & 2 complete (Week 2)

**Coordination:**
- No shared files during Week 1
- Week 2: Agent A adds error handling to existing code

**Files to Watch:**
- `src/config_manager.py` (Agent A)
- `src/asset_manager.py` (Agent B)
- `src/logger.py` (Agent A, Week 2)
- `tests/base.py` (Agent B, Week 2)

---

### Phase 2: Testing Foundation (Weeks 2-3) - 3 Agents

**Parallel Tasks:**

- **Agent A**: Write ConfigManager tests
- **Agent B**: Write AssetManager tests
- **Agent C**: Write Logger/ErrorHandler tests

**Dependencies:**
- All require Test Infrastructure (Task 1) complete
- Can start in parallel once infrastructure ready

**Coordination:**
- Separate test files, no conflicts
- All push to same coverage report
- Daily sync on coverage progress

**Files to Watch:**
- `tests/test_config_manager.py` (Agent A)
- `tests/test_asset_manager.py` (Agent B)
- `tests/test_logger.py` (Agent C)
- `tests/test_error_handler.py` (Agent C)

---

### Phase 3: Architecture (Weeks 4-5) - 1 Agent ⚠️

**⚠️ SEQUENTIAL ONLY - BOTTLENECK**

- **Week 4**: Event System (Agent A)
- **Week 5**: State Machine (Agent A)

**Why Sequential:**
- State Machine depends on Event System
- Both are architectural foundations
- Complex integration testing required

**Other Agents:**
- Write additional tests for Phase 1/2
- Improve documentation
- Prepare for Phase 4 by studying component extraction

**Critical Path:**
This is the bottleneck. Cannot parallelize.

---

### Phase 4: Component Extraction (Weeks 6-8) - 4 Agents

**Parallel Tasks:**

- **Agent A**: FireworksManager
- **Agent B**: RangoliRenderer
- **Agent C**: EtherealEffects
- **Agent D**: FloatingObjects

**Dependencies:**
- All require Phase 3 complete
- Components are independent

**Coordination:**

**Shared Resource: VisualGenerator**
All agents will modify VisualGenerator to extract their component.

**Strategy:**
1. Each agent creates adapter methods first
2. Work in separate feature branches
3. Merge order: A → B → C → D
4. Agent A coordinates merges

**Branch Strategy:**
```bash
improvements                  # Base branch
  ├─ feature/fireworks       # Agent A
  ├─ feature/rangoli         # Agent B
  ├─ feature/ethereal        # Agent C
  └─ feature/floating        # Agent D
```

**Merge Process:**
1. Agent A merges first to improvements
2. Agent B rebases on improvements, then merges
3. Agent C rebases on improvements, then merges
4. Agent D rebases on improvements, then merges

**Week 8: Integration (All Agents)**
- All agents collaborate on integration testing
- Enable all feature flags together
- Visual regression testing
- Performance testing

**Files to Watch:**
- `src/components/fireworks_manager.py` (Agent A)
- `src/components/rangoli_renderer.py` (Agent B)
- `src/components/ethereal_effects.py` (Agent C)
- `src/components/floating_objects.py` (Agent D)
- `src/visual_generator.py` (ALL AGENTS - high conflict risk)

---

### Phase 5: Method Refactoring (Week 9) - 4 Agents

**Parallel Tasks:**

- **Agent A**: Refactor FireworksManager
- **Agent B**: Refactor RangoliRenderer
- **Agent C**: Refactor EtherealEffects
- **Agent D**: Refactor FloatingObjects

**Dependencies:**
- All require Phase 4 complete
- Highly independent (different files)

**Coordination:**
- No shared files
- Minimal coordination needed
- Can work completely in parallel

**Success Metrics:**
- No method > 30 lines
- Single responsibility principle applied
- All tests pass

---

### Phase 6: Performance (Weeks 10-11) - 2 Agents

**Parallel Tasks:**

- **Agent A**: Performance Optimization (Week 10)
  - SurfaceCache implementation
  - Component optimizations
  - Benchmarking

- **Agent B**: Thread Safety (Week 11)
  - ThreadedCameraInput
  - ThreadedPersonDetector
  - Thread-safe utilities

**Dependencies:**
- Can work in parallel
- Different files, different concerns

**Coordination:**
- Minimal coordination needed
- Integrate at end of Week 11
- Test combined performance

---

## General Coordination Strategies

### Daily Standups

Each agent reports:
1. **Yesterday**: What I completed
2. **Today**: What I'm working on
3. **Blockers**: What's blocking me
4. **Conflicts**: Any merge conflicts anticipated

### Branch Strategy

```
main                          # Production
  └─ improvements             # Integration branch
      ├─ feature/task-name    # Agent feature branches
      └─ ...
```

**Rules:**
1. Create feature branch from `improvements`
2. Commit frequently to feature branch
3. Pull request to `improvements` when complete
4. Agent coordinator reviews and merges

### Conflict Resolution

**If two agents modify same file:**

1. **Prevention**: Communicate before starting
2. **Detection**: Daily git status checks
3. **Resolution**:
   - Agents coordinate on merge order
   - First agent merges
   - Second agent rebases and resolves conflicts
   - Second agent tests thoroughly after rebase

**Priority Order** (when conflicts occur):
1. Agent A (longest tenure on project)
2. Agent B
3. Agent C
4. Agent D

### Communication Channels

**Required:**
- Shared task tracker (GitHub Issues/Projects)
- Daily standup (async or sync)
- Merge conflict alerts

**Recommended:**
- Shared Slack/Discord channel
- Code review process
- Pair programming for complex integrations

### Testing Protocol

**Before Committing:**
1. Run local tests: `pytest tests/`
2. Verify no regressions
3. Check test coverage maintained

**Before Merging:**
1. All tests pass on CI/CD
2. Code review approved
3. Visual regression tests pass
4. Performance benchmarks acceptable

### Feature Flag Management

**Config Structure:**
```json
{
  "experimental": {
    "use_new_config_manager": false,
    "use_event_system": false,
    "components": {
      "use_fireworks_manager": false,
      "use_rangoli_renderer": false
    }
  }
}
```

**Rules:**
1. New features start with flag = false
2. Enable flag after testing complete
3. Document flag purpose in code
4. Remove flag after stabilization period

---

## Critical Success Factors

### 1. Communication is Key

❌ **Bad**: Work in silence, surprise merge conflicts
✅ **Good**: Daily updates, coordinate on shared files

### 2. Test Early and Often

❌ **Bad**: Write all code, test at end
✅ **Good**: Test-driven development, continuous testing

### 3. Respect Dependencies

❌ **Bad**: Start Phase 4 before Phase 3 complete
✅ **Good**: Wait for dependencies, work on other tasks

### 4. Coordinate on Shared Files

❌ **Bad**: Multiple agents edit VisualGenerator simultaneously
✅ **Good**: Coordinate merge order, use adapters

### 5. Feature Flags Enable Safety

❌ **Bad**: All-or-nothing merge to main
✅ **Good**: Feature flag, gradual enablement, easy rollback

---

## Escalation Process

**If blocked:**

1. **Level 1**: Ask other agents for help
2. **Level 2**: Document blocker, work on different task
3. **Level 3**: Escalate to project lead
4. **Level 4**: Adjust timeline/scope if needed

**Common Blockers:**
- Waiting on dependency (work on tests/docs)
- Merge conflicts (coordinate with other agent)
- Test failures (pair debug with another agent)
- Performance regression (profile together)

---

## Timeline Overview

```
Week 1:  [A: Config][B: Asset][C: Doc]
Week 2:  [A: Errors][B: TestInfra][C: Help]
Week 3:  [A: ConfigTests][B: AssetTests][C: ErrorTests]
Week 4:  [A: EventSystem]--SEQUENTIAL--
Week 5:  [A: StateMachine]--SEQUENTIAL--
Week 6:  [A: Fireworks][B: Rangoli][C: Ethereal][D: Floating]
Week 7:  [A: Fireworks][B: Rangoli][C: Ethereal][D: Floating]
Week 8:  [ALL: Integration Testing]
Week 9:  [A: RefactorA][B: RefactorB][C: RefactorC][D: RefactorD]
Week 10: [A: Performance][B: Prep]
Week 11: [A: Finalize][B: Threading]
```

**Critical Path**: Phase 3 (Weeks 4-5) - only 1 agent can work

**Maximum Parallelization**: Phase 4 & 5 (Weeks 6-9) - 4 agents

---

## Resource Requirements

**Per Agent:**
- Development environment (see README.md)
- Access to improvements branch
- Ability to run tests locally
- Camera for testing (or mock camera)

**Shared Resources:**
- CI/CD pipeline
- Code review process
- Shared documentation
- Test coverage reports

---

## Success Metrics

**Per Phase:**
- All planned tasks complete
- All tests passing
- Code reviewed and merged
- Documentation updated

**Overall:**
- 70%+ test coverage
- 60+ FPS performance
- All features working
- Clean, maintainable code
- Cultural authenticity preserved

---

## Conclusion

With proper coordination, this 11-week project can leverage:
- **Phase 1**: 3 agents (saves ~1 week)
- **Phase 2**: 3 agents (saves ~1 week)
- **Phase 3**: 1 agent (bottleneck)
- **Phase 4**: 4 agents (saves ~2 weeks)
- **Phase 5**: 4 agents (saves ~1 week)
- **Phase 6**: 2 agents (saves ~1 week)

**Potential time savings**: ~6 weeks with perfect coordination

**Realistic time savings**: ~4 weeks accounting for coordination overhead

**Key to success**: Communication, testing, and respecting dependencies.
