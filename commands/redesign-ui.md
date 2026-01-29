# Redesign UI Component with Visual Regression Testing

Autonomous UI/UX redesign with baseline capture, visual regression testing, responsive validation, and zero-regression guarantee.

## Instructions

You are redesigning: **$ARGUMENTS**

Follow this systematic 7-phase approach to safely redesign UI components while preserving 100% functionality.

---

## Phase 1: Analysis & Baseline Capture (10%)

**Capture current state before making any changes:**

1. **Component Analysis**
   - Identify the component file location and all dependencies
   - Map all imports, exports, and prop interfaces
   - Document current behavior and user interactions
   - List all files that will be modified

2. **Visual Baseline**
   - Capture screenshots at breakpoints:
     * Desktop (1920x1080)
     * Tablet (768x1024)
     * Mobile (375x667)
   - Capture all states: default, hover, active, disabled, error
   - Save to `.orchestr8/baselines/[component-name]/screenshots/`

3. **Performance Baseline**
   - Measure current render time
   - Check bundle size impact
   - Document re-render frequency
   - Use React DevTools profiling if applicable

4. **Accessibility Baseline**
   - Run accessibility scan (axe-core or similar)
   - Document current ARIA attributes
   - Test keyboard navigation
   - Check color contrast ratios

5. **Create Baseline Report**
   - Save to `.orchestr8/baselines/[component-name]/baseline-report.md`
   - Include component structure diagram (ASCII art)
   - Document current metrics
   - List known issues or technical debt

**CHECKPOINT:** Baseline validated ✓

---

## Phase 2: Design Planning (15%)

**Create detailed design plan:**

1. **Design Specification**
   - Interpret design goals into concrete changes
   - Define new component structure
   - Plan props interface changes
   - Specify styling strategy (Tailwind/CSS Modules/styled-components)

2. **Component Architecture Diagrams**
   Create ASCII diagrams showing:
   - **Before**: Current component tree
   - **After**: Proposed component tree
   - **Data Flow**: Props, state, events

3. **File Change Plan**
   Create table of changes:

   | File Path | Change Type | Description |
   |-----------|-------------|-------------|
   | path/to/Component.tsx | MODIFY | Update layout |
   | path/to/NewComponent.tsx | CREATE | New child |
   | path/to/OldComponent.tsx | DELETE | Deprecated |

4. **Responsive Design Plan**
   - Mobile (< 768px): Layout approach
   - Tablet (768px - 1024px): Layout approach
   - Desktop (> 1024px): Layout approach

5. **Risk Assessment**
   - Breaking changes to identify
   - Integration challenges
   - Rollback complexity

6. **Save Design Plan**
   - Create `.orchestr8/docs/design/[component-name]-design-plan.md`
   - Include all diagrams and specifications

**CHECKPOINT:** Design plan comprehensive ✓

---

## Phase 3: Component Development (25%)

**Build new components in isolation:**

1. **Implementation**
   - Create new components per design plan
   - Use TypeScript with proper type definitions
   - Implement responsive design (mobile-first)
   - Add ARIA attributes and accessibility features

2. **Props Interface**
   - Define comprehensive TypeScript interfaces
   - Document all props with JSDoc comments
   - Set sensible defaults

3. **Styling**
   - Follow project's styling approach
   - Implement responsive breakpoints
   - Ensure consistency with design system

4. **Unit Tests**
   - Test default render
   - Test all prop variations
   - Test user interactions
   - Test accessibility (keyboard navigation, ARIA)
   - Test responsive behavior
   - Aim for >80% coverage

5. **Build Verification**
   - Run TypeScript compiler (tsc --noEmit)
   - Run tests (npm test)
   - Run linter (npm run lint)
   - Verify zero console errors

**CHECKPOINT:** New components built and tested ✓

---

## Phase 4: Integration & Migration (20%)

**Update existing components and integrate:**

1. **Update Modified Components**
   - Import new components
   - Update props passing
   - Integrate new state management
   - Wire up event handlers

2. **Integration Steps** (minimize breakage)
   - Step 1: Add new components without removing old
   - Step 2: Wire up new components
   - Step 3: Remove old components

3. **Dependency Updates**
   - Update import statements
   - Update component exports
   - Update index files

4. **Integration Testing**
   - Run TypeScript compiler
   - Run build process (npm run build)
   - Run full test suite
   - Start dev server and manual test
   - Check console for errors

5. **Rollback Preparation**
   - Document files modified
   - Create rollback guide at `.orchestr8/docs/[component-name]-rollback.md`

**CHECKPOINT:** Integration complete, zero build errors ✓

---

## Phase 5: Visual Regression Testing (15%)

**Automated visual regression detection:**

1. **Screenshot Capture**
   - Capture new screenshots at all breakpoints
   - Capture all states (default, hover, active, etc.)
   - Save to `.orchestr8/screenshots/new/`

2. **Visual Diff Generation**
   - Compare baseline vs. new screenshots
   - Use Playwright visual comparison or pixelmatch
   - Calculate diff percentage for each
   - Save diff images to `.orchestr8/screenshots/diffs/`

3. **Diff Analysis**
   - Identify intended vs. unintended changes
   - Document unintended changes requiring review
   - Validate intended changes match design goals
   - Create visual regression report

4. **Cross-Browser Testing**
   - Test in Chrome, Firefox, Safari
   - Document browser-specific differences

5. **Responsive Validation**
   - Verify mobile layout works (< 768px)
   - Verify tablet layout works (768px - 1024px)
   - Verify desktop layout works (> 1024px)
   - Check no horizontal scroll
   - Verify touch targets >44px on mobile

6. **Create Report**
   - Save to `.orchestr8/docs/reports/[component-name]-visual-regression-report.md`
   - Include before/after/diff image links
   - Document all changes with assessment

**CHECKPOINT:** Visual regression passed, only intended changes ✓

---

## Phase 6: Functional Testing (10%)

**Comprehensive functional validation:**

1. **Test Suite Execution**
   - Run unit tests: `npm test -- --coverage`
   - Run integration tests
   - Run end-to-end tests: `npx playwright test`
   - Ensure 100% pass rate

2. **User Flow Validation**
   - Test all primary user flows
   - Test secondary user flows
   - Test error/edge case flows
   - Document all flows tested

3. **Edge Case Testing**
   - Empty states (no data, null props)
   - Extreme data (very long strings, large numbers)
   - Error states (network failures, validation errors)
   - Browser quirks

4. **Console Error Detection**
   - Check for JavaScript errors
   - Check for React warnings
   - Check for performance warnings
   - **Goal: Zero console errors/warnings**

5. **Accessibility Testing**
   - Run automated accessibility scan
   - Test keyboard navigation
   - Test screen reader compatibility
   - Validate WCAG 2.1 AA compliance

6. **Performance Testing**
   - Compare render performance vs. baseline
   - Check bundle size (ensure <10% increase)
   - Profile with React DevTools

7. **Create Test Report**
   - Save to `.orchestr8/docs/reports/[component-name]-functional-test-report.md`
   - Document 100% pass rate
   - Include performance metrics
   - Document browser compatibility

**CHECKPOINT:** All tests passing, zero console errors ✓

---

## Phase 7: Documentation & Deployment Prep (5%)

**Update documentation and prepare deployment:**

1. **Component Documentation**
   - Update component README/docs
   - Document new props and usage
   - Add usage examples
   - Document accessibility features
   - Document responsive behavior

2. **CHANGELOG Update**
   - Add entry for redesign
   - Document changes, additions, fixes
   - Note any breaking changes

3. **Deployment Guide**
   - Create `.orchestr8/docs/[component-name]-deployment-guide.md`
   - Include pre-deployment checklist
   - Document deployment steps
   - Include post-deployment monitoring plan
   - **Note: User will handle git commit/push/PR**

4. **Rollback Guide**
   - Update `.orchestr8/docs/[component-name]-rollback.md`
   - Document when to rollback
   - Provide rollback procedure
   - List files modified

5. **Migration Guide**
   - Create `.orchestr8/docs/[component-name]-migration-guide.md`
   - Document what changed
   - Provide migration steps for other developers
   - Note breaking changes

**CHECKPOINT:** Documentation complete and deployment-ready ✓

---

## Success Criteria

The UI redesign is complete when:

1. ✅ **Baseline Captured** - Screenshots, metrics, current state documented
2. ✅ **Design Plan Approved** - ASCII diagrams, file changes planned
3. ✅ **New Components Built** - Unit tests >80% coverage, TypeScript clean
4. ✅ **Integration Complete** - Build succeeds, tests pass, zero console errors
5. ✅ **Visual Regression Passed** - Only intended changes (<5% unintended diff)
6. ✅ **Functional Tests Passed** - 100% pass rate, all user flows work
7. ✅ **Responsive Design Validated** - Works on mobile, tablet, desktop
8. ✅ **Cross-Browser Compatible** - Chrome, Firefox, Safari, Edge
9. ✅ **Performance Maintained** - No >10% degradation
10. ✅ **Accessibility Preserved** - Zero WCAG violations, keyboard navigable
11. ✅ **Documentation Updated** - Docs, CHANGELOG, guides complete
12. ✅ **All Quality Gates Passed** - Every checkpoint validated

---

## Important Notes

### Git Workflow
- **User controls git operations** - No automatic commits/pushes
- Create your own branch: `git checkout -b feature/[component-name]-redesign`
- Commit when ready with appropriate messages
- Create PR when ready for review

### Quality Gates
- All gates are mandatory
- No phase can be skipped
- Each checkpoint must pass before proceeding

### Rollback Strategy
- Always have a rollback plan
- Document rollback steps
- Test rollback procedure

### Testing Focus
- Visual regression testing is critical
- 100% test pass rate required
- Zero console errors/warnings
- Accessibility compliance mandatory

---

## Anti-Patterns to Avoid

### DON'T ❌
- Skip baseline capture
- Skip visual regression testing
- Ignore responsive design
- Deploy with failing tests
- Skip accessibility testing
- Ignore performance impact
- Skip documentation
- Change too much at once

### DO ✅
- Capture comprehensive baseline
- Create detailed design plan
- Build components in isolation
- Run visual regression tests
- Test at all breakpoints
- Validate accessibility
- Monitor performance
- Document everything
- Have rollback plan
- Validate at each phase

---

## Example: Supply Tab Redesign

Following this workflow for the Supply Inventory tab redesign:

```
/redesign-ui "SupplyTab - reduce white space 30%, add stock alerts bar, streamline buttons, make search full-width"
```

**Phases:**
1. Capture current Supply tab screenshots, metrics, performance
2. Design new layout with ASCII diagrams, plan StockAlertsBar component
3. Build StockAlertsBar component with tests in isolation
4. Integrate into TableItems, update TableSupplyItems
5. Visual regression: compare before/after at all breakpoints
6. Functional testing: verify all supply tab features work
7. Document changes, create migration guide

**Estimated Time:** 3-4 hours

**Deliverables:**
- New StockAlertsBar component
- Updated TableItems.tsx
- Updated TableSupplyItems.tsx
- Visual regression report with before/after screenshots
- Functional test report (100% pass rate)
- Complete documentation

---

Remember: This workflow ensures **zero functional regressions** while improving UX. Every phase has checkpoints to validate quality before proceeding. Always prioritize safety and testing over speed.
