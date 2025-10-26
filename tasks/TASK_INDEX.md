# Diwali Projection System Task Index - REVISED

⚠️ **This is the revised implementation plan. See [REVISED_PLAN.md](REVISED_PLAN.md) for detailed rationale.**

This document provides a chronological index of all implementation tasks for the Diwali Projection System refactoring project.

## Phase 1: Foundation (Weeks 1-2)

**Parallel Tasks** (up to 3 agents):
- [Task 1: ConfigManager](phase1_task1_config_manager.md) - Agent A, Week 1
- [Task 2: AssetManager](phase1_task2_asset_manager.md) - Agent B, Week 1
- [Task 3: Error Handling & Logging](phase1_task3_error_handling.md) - Agent A, Week 2

**Goal**: Establish core infrastructure (Config, Assets, Logging, Error Handling)

## Phase 2: Testing Foundation (Weeks 2-3)

**Parallel Tasks** (up to 3 agents):
- [Task 1: Test Infrastructure Setup](phase2_task1_test_infrastructure.md) - Agent B, Week 2
- [Parallel Test Writing Tasks](phase2_tests_parallel.md) - Agents A, B, C, Week 3

**Goal**: Build safety net for refactoring (runs parallel with Phase 1, Week 2)

**Critical**: Testing comes early to provide confidence during refactoring

## Phase 3: Architectural Patterns (Weeks 4-5)

**Sequential Tasks** (1 agent only - bottleneck):
- [Event System & State Machine](phase3_sequential.md) - Agent A, Weeks 4-5

**Goal**: Establish communication and state patterns

**Critical**: Architecture must be in place BEFORE component extraction

**Warning**: This is the critical path - only 1 agent can work effectively

## Phase 4: Component Decomposition (Weeks 6-8)

**Parallel Tasks** (up to 4 agents):
- [Parallel Component Extraction](phase4_parallel_components.md) - Agents A, B, C, D
  - Task 4.1: FireworksManager (Agent A)
  - Task 4.2: RangoliRenderer (Agent B)
  - Task 4.3: EtherealEffects (Agent C)
  - Task 4.4: FloatingObjects (Agent D)
  - Task 4.5: Integration Testing (All, Week 8)

**Goal**: Break down monolithic VisualGenerator into focused components

**Dependencies**: Requires Event System and State Machine from Phase 3

## Phase 5: Method Refactoring (Week 9)

**Parallel Tasks** (up to 4 agents):
- [Parallel Method Refactoring](phase5_parallel_refactoring.md) - Agents A, B, C, D
  - Task 5.1: Refactor FireworksManager (Agent A)
  - Task 5.2: Refactor RangoliRenderer (Agent B)
  - Task 5.3: Refactor EtherealEffects (Agent C)
  - Task 5.4: Refactor FloatingObjects (Agent D)

**Goal**: Refine extracted components

**Note**: Moved to AFTER component extraction (refactor what's been extracted, not what will be extracted)

## Phase 6: Performance & Concurrency (Weeks 10-11)

**Parallel Tasks** (up to 2 agents):
- [Parallel Performance & Threading](phase6_parallel_performance.md) - Agents A, B
  - Task 6.1: Performance Optimization (Agent A, Week 10)
  - Task 6.2: Thread Safety & Concurrency (Agent B, Week 11)

**Goal**: Optimize stable architecture

**Note**: Performance optimization comes last when architecture is stable

## Task Dependencies (REVISED)

```
Phase 1 (Foundation)
    ↓
Phase 2 (Testing) ← Starts during Phase 1, Week 2
    ↓
Phase 3 (Events & State Machine)
    ↓
Phase 4 (Component Decomposition) ← Requires Events/State
    ↓
Phase 5 (Method Refactoring) ← Refactor extracted components
    ↓
Phase 6 (Performance & Concurrency) ← Optimize stable architecture
```

## Key Changes from Original Plan

1. **Testing moved from Week 11 → Weeks 2-3** (8 weeks earlier!)
2. **Event System moved from Week 9-10 → Week 4** (5 weeks earlier)
3. **State Machine moved from Week 9-10 → Week 5** (4 weeks earlier)
4. **Method Refactoring moved from Week 4 → Week 9** (5 weeks later)

**Rationale**: Architecture first, then extract, then refine. Testing throughout.

## Revised Implementation Order

For best results, implement tasks in this order:

### Phase 1 (Weeks 1-2)
1. **ConfigManager** (Week 1) - [phase1_task1_config_manager.md](phase1_task1_config_manager.md)
2. **AssetManager** (Week 1) - [phase1_task2_asset_manager.md](phase1_task2_asset_manager.md)
3. **Error Handling** (Week 2) - [phase1_task3_error_handling.md](phase1_task3_error_handling.md)

### Phase 2 (Weeks 2-3) ← **EARLY TESTING**
4. **Test Infrastructure** (Week 2) - [phase2_task1_test_infrastructure.md](phase2_task1_test_infrastructure.md)
5. **Test Writing** (Week 3) - [phase2_tests_parallel.md](phase2_tests_parallel.md)

### Phase 3 (Weeks 4-5) ← **ARCHITECTURE FIRST**
6. **Event System & State Machine** (Weeks 4-5) - [phase3_sequential.md](phase3_sequential.md)

### Phase 4 (Weeks 6-8) ← Now can use events/states
7. **Component Extraction** (Weeks 6-8) - [phase4_parallel_components.md](phase4_parallel_components.md)

### Phase 5 (Week 9) ← Refactor extracted code
8. **Method Refactoring** (Week 9) - [phase5_parallel_refactoring.md](phase5_parallel_refactoring.md)

### Phase 6 (Weeks 10-11)
9. **Performance Optimization** (Week 10) - [phase6_parallel_performance.md](phase6_parallel_performance.md)
10. **Thread Safety** (Week 11) - [phase6_parallel_performance.md](phase6_parallel_performance.md)

## Additional Resources

- 📖 [REVISED_PLAN.md](REVISED_PLAN.md) - Why the plan was revised
- 🔄 [INCREMENTAL_MIGRATION.md](INCREMENTAL_MIGRATION.md) - Feature flags and rollback strategy
- 👥 [PARALLELIZATION_GUIDE.md](PARALLELIZATION_GUIDE.md) - Multi-agent coordination guide
- 📋 [README.md](README.md) - Phase summaries and timeline

## Critical Success Factors

✅ **Always maintain working application** - Use feature flags and incremental migration
✅ **Test early and continuously** - Build confidence before risky refactoring
✅ **Architecture enables refactoring** - Establish patterns before extraction
✅ **Refactor what exists** - Extract first, then refine extracted components