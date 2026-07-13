---
name: webapp-testing
description: >
  Write and run frontend tests for the Angular dashboard (data_visualizer):
  component tests and basic end-to-end flows. Use when adding test coverage
  to the Angular app, testing components/signals/services, or when the user
  says "test the dashboard", "frontend tests", "e2e", "component test". See
  `domains/frontend.md` for the dashboard's stack conventions.
license: MIT
metadata:
  tier: LOW
---

# webapp-testing

## Mandatory pre-flight

Before writing any test:

1. Read `domains/frontend.md` for the dashboard's stack conventions.
2. Inspect the project's `package.json` / `angular.json`.
3. Identify the actual configured runner — Karma, Jest, or Vitest. **Do not assume** — verify first.

## Component test pattern

Render → interact → assert exact rendered output or Signal state. No cosmetic assertions (`toBeDefined()`, `not.toBeNull()`) — assert exact values or counts.

```typescript
it('should render exactly 5 data cards when loading dashboard', async () => {
  await render(DashboardComponent);
  const cards = screen.getAllByTestId('data-card');
  expect(cards.length).toBe(5);
});

it('should update signal state to "active" on click', async () => {
  const component = setup();
  await fireEvent.click(screen.getByText('Activate'));
  expect(component.statusSignal()).toBe('active');
});
```

## Service test pattern (HTTP / TanStack Query)

```typescript
it('should return exactly the expected user record', async () => {
  const mockUser = { id: 'u1', name: 'Julio' };
  queryClient.setQueryData(['user', 'u1'], mockUser);
  const result = await userService.getUser('u1');
  expect(result).toEqual(mockUser);
});
```

## E2E happy path

Use Playwright only if no e2e tool already exists in `package.json` — otherwise match what's already there.

```typescript
test('user can navigate to details and see correct ID', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('.row-1');
  await expect(page.locator('.detail-id')).toHaveText('ID-12345');
});
```

## Run and read failures

Check `package.json` for the actual script (`npm run test`, `npm run test:unit`, etc.). On failure, read the expected-vs-actual diff; if it's a cardinality mismatch, check the mock/data provider before touching the test.

## Ponytail note

Test user-visible behavior and state transitions. Don't test Angular internals, lifecycle hooks, or change detection itself.

## Out of scope

Visual-regression/screenshot testing, cross-browser matrix (one runner, one browser), CI integration, backend/API contract testing, duplicating `domains/frontend.md`'s stack-setup content.
