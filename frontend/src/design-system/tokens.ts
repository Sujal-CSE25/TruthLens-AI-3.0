// TruthLens AI 2.0 — Design Tokens
// Government-grade institutional color system

export const colors = {
  // Primary palette
  navy: '#0B2A5B',
  deepNavy: '#08224A',
  blue: '#1455A0',
  primaryBlue: '#1D63C8',
  lightBlue: '#EAF2FF',

  // Surfaces
  page: '#F7F9FC',
  white: '#FFFFFF',
  surface: '#F4F7FA',
  border: '#D8E0EA',
  divider: '#E4E9F0',

  // Text
  text: '#172B4D',
  secondaryText: '#425466',
  mutedText: '#667085',
  disabled: '#98A2B3',

  // Status
  success: '#18864B',
  successBg: '#EAF7EF',
  warning: '#B7791F',
  warningBg: '#FFF7E6',
  danger: '#B42318',
  dangerBg: '#FFF0EF',
  info: '#1455A0',
  infoBg: '#EAF2FF',
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
  xxxl: '40px',
} as const;

export const radius = {
  sm: '4px',
  md: '6px',
  lg: '8px',
} as const;

export const typography = {
  fontFamily: "'Noto Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  display: { size: '32px', lineHeight: '40px', weight: '700' },
  h1: { size: '28px', lineHeight: '36px', weight: '700' },
  h2: { size: '22px', lineHeight: '30px', weight: '700' },
  h3: { size: '18px', lineHeight: '26px', weight: '700' },
  body: { size: '15px', lineHeight: '22px', weight: '400' },
  strong: { size: '15px', lineHeight: '22px', weight: '600' },
  small: { size: '13px', lineHeight: '18px', weight: '400' },
  micro: { size: '11px', lineHeight: '16px', weight: '600' },
} as const;

export const shadows = {
  card: '0 1px 3px rgba(11,42,91,0.08), 0 1px 2px rgba(11,42,91,0.06)',
  header: '0 1px 4px rgba(11,42,91,0.10)',
  elevated: '0 4px 12px rgba(11,42,91,0.10)',
} as const;

export const transitions = {
  fast: '150ms ease',
  normal: '200ms ease',
  slow: '250ms ease',
} as const;
