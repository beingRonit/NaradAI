# Plan: Email OTP Login Page Before Onboarding

## Current State
- `src/app/page.tsx` checks `localStorage.narad-onboarding-complete` → redirects to `/onboarding` or `/dashboard`
- No auth/login flow exists
- Onboarding has 4 steps: Welcome → Persona → Preferences → Awaken
- Visual style: dark bg `#0A0A0F`, violet accents, premium futuristic AI aesthetic

## Target Flow
```
Open app
  ↓
page.tsx checks localStorage "narad-session"
  ↓ (no session)
/login — enter email → receive OTP → verify OTP → set "narad-session"
  ↓ (has session)
check "narad-onboarding-complete"
  ↓ (not complete)
/onboarding → dashboard
  ↓ (complete)
/dashboard
```

## Files to Create
1. **`src/app/login/page.tsx`** — Login page (full screen dark layout, centered card)
2. **`src/components/login/LoginForm.tsx`** — Step 1: email input + send OTP button
3. **`src/components/login/OtpVerify.tsx`** — Step 2: 6-digit OTP input + verify button

## Files to Modify
1. **`src/app/page.tsx`** — Add auth check before onboarding check

## Visual Design
- Full screen `bg-[#0A0A0F]` with centered content
- Logo at top with violet glow (matching sidebar logo)
- "Narad AI" wordmark + "Autonomous Creator" subtitle
- Dark card `bg-[#0f1423]` with `border-slate-700/60` and `backdrop-blur-sm`
- Email input: native `<input>` with `bg-[#0B0F19]` + violet focus ring
- OTP: 6 individual digit boxes, auto-focus next on input
- Violet gradient buttons with shadow glow
- Framer Motion animations (fade-in, slide-up)
- Simulated OTP: always "123456" for demo (shown as helper text)

## Implementation Details

### `src/app/page.tsx`
```tsx
// Check narad-session first
const session = localStorage.getItem("narad-session");
if (!session) → /login

// Then check onboarding
const onboarding = localStorage.getItem("narad-onboarding-complete");
if (onboarding) → /dashboard
else → /onboarding
```

### `src/app/login/page.tsx`
- Renders `<LoginForm>` on step 1, `<OtpVerify>` on step 2
- State: `email`, `otpSent`, `otpVerified`
- On verify success: set `narad-session` in localStorage, redirect based on onboarding status

### `src/components/login/LoginForm.tsx`
- Logo + wordmark header
- "Sign in to Narad AI" heading
- Email input field
- "Send OTP" button (ParticleButton)
- Helper text: "Demo: use any email"

### `src/components/login/OtpVerify.tsx`
- "Verify OTP" heading
- 6-digit OTP input boxes (individual inputs, auto-advance)
- "Verify & Continue" button
- "Change email" back link
- Helper text: "Demo OTP: 123456"

## Routing Changes Summary
- `/login` — new route (no layout wrapper needed, standalone page)
- `/` — now checks auth → login → onboarding → dashboard

## No Changes To
- Onboarding wizard
- Dashboard
- Feed / Intelligence / Memory / Sources
- Sidebar, AppShell, layout.tsx
- globals.css (existing styles sufficient)
- types.ts (no new types needed)
