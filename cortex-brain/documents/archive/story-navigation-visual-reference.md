# Chapter Navigation Buttons - Visual Preview

## Desktop Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Story chapter content ends here...]                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                                                            ││
│  │  ┌──────────────────────┐    ┌──────────────────────┐    ││
│  │  │  ←                   │    │                   →  │    ││
│  │  │  PREVIOUS            │    │            NEXT      │    ││
│  │  │  Chapter 3: The      │    │  Chapter 5: The      │    ││
│  │  │  SQLite Intervention │    │  Knowledge Graph...  │    ││
│  │  └──────────────────────┘    └──────────────────────┘    ││
│  │                                                            ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [Next chapter begins...]                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Glassmorphism container with blur effect
- Two buttons side-by-side
- Left-aligned "Previous" with ← arrow
- Right-aligned "Next" with → arrow
- Cyan gradient on hover

## Mobile Layout (<768px)

```
┌──────────────────────────┐
│                          │
│  [Content ends...]       │
│                          │
│  ┌──────────────────────┐│
│  │                      ││
│  │  ┌──────────────┐   ││
│  │  │  ←           │   ││
│  │  │  PREVIOUS    │   ││
│  │  │  Chapter 3:  │   ││
│  │  │  The SQLite  │   ││
│  │  │  Intervention│   ││
│  │  └──────────────┘   ││
│  │                      ││
│  │  ┌──────────────┐   ││
│  │  │           →  │   ││
│  │  │      NEXT    │   ││
│  │  │  Chapter 5:  │   ││
│  │  │  The Knowled │   ││
│  │  │  ge Graph... │   ││
│  │  └──────────────┘   ││
│  │                      ││
│  └──────────────────────┘│
│                          │
│  [Next chapter...]       │
└──────────────────────────┘
```

**Features:**
- Stacked vertical layout
- Full-width buttons
- Centered text
- Same hover effects

## Special Cases

### Prologue (First Chapter)
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Prologue content ends...]                                    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                                                            ││
│  │                           ┌──────────────────────┐        ││
│  │                           │                   →  │        ││
│  │                           │            NEXT      │        ││
│  │                           │  Chapter 1: The      │        ││
│  │                           │  Goldfish Theory     │        ││
│  │                           └──────────────────────┘        ││
│  │                                                            ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
**Note:** Only "Next" button shown, right-aligned

### Epilogue (Last Chapter)
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Epilogue content ends...]                                    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                                                            ││
│  │  ┌──────────────────────┐                                ││
│  │  │  ←                   │                                ││
│  │  │  PREVIOUS            │                                ││
│  │  │  Chapter 11: The     │                                ││
│  │  │  3.0 Revolution      │                                ││
│  │  └──────────────────────┘                                ││
│  │                                                            ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
**Note:** Only "Previous" button shown, left-aligned

## Color Palette

**Container:**
- Background: `rgba(255, 255, 255, 0.03)` (very subtle white overlay)
- Border: `rgba(255, 255, 255, 0.08)` (subtle white border)
- Backdrop: `blur(10px)` (glassmorphism effect)

**Buttons:**
- Default Background: `linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(0, 150, 255, 0.1))`
- Default Border: `rgba(0, 255, 255, 0.2)` (cyan border)
- Default Text: `#00ffff` (cyan)

**Buttons (Hover):**
- Hover Background: `linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(0, 150, 255, 0.2))`
- Hover Border: `rgba(0, 255, 255, 0.4)` (brighter cyan)
- Hover Shadow: `0 8px 20px rgba(0, 255, 255, 0.2)` (cyan glow)
- Transform: `translateY(-2px)` (lift effect)

## Typography

**Navigation Direction Label:**
- Font size: `0.75rem`
- Color: `rgba(255, 255, 255, 0.6)` (muted white)
- Text transform: `uppercase`
- Letter spacing: `0.5px`

**Chapter Title:**
- Font size: `0.9rem`
- Color: `#fff` (pure white)
- Font weight: `500`

**Arrow Icons:**
- Font size: `1.2rem`
- Characters: `←` (left) and `→` (right)

## Interaction States

1. **Default:** Cyan gradient with subtle border
2. **Hover:** Brighter cyan, lifted 2px, glowing shadow
3. **Active/Click:** Smooth scroll to target chapter (100px offset)
4. **Focus:** (Inherits hover state for accessibility)

## Accessibility

- Semantic `<a>` tags with `href` attributes
- Keyboard navigable (Tab key)
- Screen reader friendly (chapter titles in text)
- Clear visual focus indicators
- Sufficient color contrast (cyan on dark background)

## Animation

- Transition: `all 0.3s ease`
- Smooth scroll: `behavior: 'smooth'`
- No jarring movements
- Performance optimized with CSS transforms
