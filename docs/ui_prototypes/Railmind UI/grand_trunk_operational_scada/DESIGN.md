---
name: Grand Trunk Operational SCADA
colors:
  surface: '#141319'
  surface-dim: '#141319'
  surface-bright: '#3a383f'
  surface-container-lowest: '#0e0d13'
  surface-container-low: '#1c1b21'
  surface-container: '#201f25'
  surface-container-high: '#2b2930'
  surface-container-highest: '#36343b'
  on-surface: '#e5e1ea'
  on-surface-variant: '#c9c4d4'
  inverse-surface: '#e5e1ea'
  inverse-on-surface: '#312f36'
  outline: '#928f9d'
  outline-variant: '#484552'
  surface-tint: '#c8bfff'
  primary: '#c8bfff'
  on-primary: '#2f1c80'
  primary-container: '#7769cc'
  on-primary-container: '#040023'
  inverse-primary: '#5e50b1'
  secondary: '#c8c1ee'
  on-secondary: '#312c50'
  secondary-container: '#474268'
  on-secondary-container: '#b7b0dc'
  tertiary: '#ffb4a1'
  on-tertiary: '#5b1a08'
  tertiary-container: '#b65e47'
  on-tertiary-container: '#120100'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e5deff'
  primary-fixed-dim: '#c8bfff'
  on-primary-fixed: '#1a0064'
  on-primary-fixed-variant: '#463698'
  secondary-fixed: '#e5deff'
  secondary-fixed-dim: '#c8c1ee'
  on-secondary-fixed: '#1b163a'
  on-secondary-fixed-variant: '#474268'
  tertiary-fixed: '#ffdbd2'
  tertiary-fixed-dim: '#ffb4a1'
  on-tertiary-fixed: '#3c0800'
  on-tertiary-fixed-variant: '#79301c'
  background: '#141319'
  on-background: '#e5e1ea'
  surface-variant: '#36343b'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: 0em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: 0em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: 0.01em
  title-lg:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: 0.02em
  title-md:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: 0.01em
  title-sm:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.05em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.08em
  telemetry-data:
    fontFamily: JetBrains Mono
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 26px
    letterSpacing: -0.03em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
---

## Brand & Style

This design system synthesizes the century-spanning legacy of Indian Railways with mission-critical modern control room informatics. It bridges the authoritative, stoic discipline of historical railway administration with the ultra-precise, split-second demands of electrified multi-track supervisory control and data acquisition (SCADA). 

The visual style is **Industrial High-Density SCADA Modernism**. It prioritizes extreme legibility under fatigue, zero-ambiguity status recognition, and strict visual ergonomics across round-the-clock shift cycles. The emotional cadence is unyielding, sovereign, and calm—evoking the structural mass of heavy steel locomotives, mechanical interlockings, and optical track-circuit telemetry. 

Interfaces present high-contrast, razor-sharp vector structures over deep midnight-slate voids. Functional states avoid decorative fluff in favor of disciplined data density, architectural framing, and authoritative physical metaphors reminiscent of cast-iron control desks translated into modern illuminated panels.

## Colors

The chromatic architecture is engineered specifically for deep-void dark environments, ensuring that signal colors retain instantaneous visual priority without inducing retinal burn.

- **Foundational Canvas**: The primary root surface is not dead black, but an ultra-dense IR Midnight Navy (`#030614`), layered with SCADA plate tiers (`#080C22` base surface, `#0E1430` elevated console tier, and `#151D42` active overlay).
- **Primary Deep Indigo (`#7769cc`)**: The updated historic identity and control accent color. When applied as an active surface fill, it is bounded with illuminated brightened borders to prevent low-contrast clipping against dark canvas plates. Used for primary control engagement, authoritative headers, route lock indicators, and system master actions.
- **Critical Crimson (`#78729b` / Secondary & `#470b00` / Tertiary)**: Directly derived from heritage IR coaching stock and signaling caution/danger. Utilized exclusively for emergency brake overrides (EBPs), track section shunts, trip interlocks, critical alarm badges, and immediate operational exceptions. Paired with a vibrant emissive warning glow (`#FF3B30`) when active telemetry faults occur.
- **Surface Highlight / Lavender Tint (`#470b00`)**: A crisp, high-luminance steel-chalk neutral used for top-level numeric telemetry readouts, primary switchgear nomenclature, and illuminated edge fillets. It counters eye fatigue by softening stark white contrast down to a comfortable daylight-readable level.
- **Industrial Steel Neutral (`#79767e`)**: The mechanical backbone. Applied to inactive track segments, secondary metadata, grid lines, structural dividers, unselected toggle shells, and disabled physical actuators.
- **Functional Telemetry Accents**: 
  - *Track Clear / Traction On (Signal Green)*: `#00D06C`
  - *Route Held / Caution (Traction Amber)*: `#F5A623`
  - *Overhead Equipment (OHE) Energized*: `#00E5FF`

## Typography

The typographic hierarchy separates spatial overview navigation, explanatory prose, and mechanical telemetry:

- **Display & Section Headers (Space Grotesk)**: Chosen for its deliberate geometric architecture and subtle mechanical joins. It gives section markers, route blocks, and train schedules a commanding presence reminiscent of modernist technical transport diagrams.
- **Narrative & System Ergonomics (IBM Plex Sans)**: Handles log feeds, incident tickets, contextual tooltips, and operator instructions. It provides unyielding clarity, exceptional distinction between easily confused glyphs (e.g., `0`, `O`, `l`, `1`, `I`), and balanced horizontal metrics during extended viewing.
- **Telemetry & State Readouts (JetBrains Mono)**: Reserved for tabular engine data, axle-counter outputs, kilometer post markers (KM/TP), speed indicators, track circuit IDs, and signal aspects. All tabular telemetry must render with strict tabular numerals (`font-variant-numeric: tabular-nums`) to prevent shifting layouts under high-frequency refresh loops.

## Layout & Spacing

The layout philosophy relies on a **Modular Instrument Grid (Fixed/Fluid Hybrid)** calibrated on a hard 4px base unit. Control interfaces operate within a strict spatial ledger that mimics instrument rack architectures (19-inch rack units).

- **Desktop SCADA Consoles (1440px and wider)**: Organized in an asymmetrical 24-column grid. Gutters are locked to `1rem` (16px) with an operational outer margin of `1.5rem` (24px). Columns group into 3 dominant operational zones: System Master Navigation & Alarms (4 columns), Live Mimic Display / Track Geometry (14 columns), and Detail Telemetry / Interlocking Actuators (6 columns).
- **Tablet Consoles (768px – 1439px)**: Reflows to a 12-column grid with `0.75rem` (12px) gutters. The live track mimic pinches horizontally with horizontal scroll enabled for extended inter-station blocks; telemetry modules fold into lower split drawers.
- **Field Inspector Mobile (320px – 767px)**: Collapses to a single-column 4-grid module structure. Margins drop to `0.75rem` (12px), gutters to `0.5rem` (8px). Visual mimic maps convert into serialized tabular track circuit cards, prioritizing immediate shunt state and block occupancy over spatial cartography.
- **Spacing Principle**: High-density grouping. Related metrics are clamped tightly using `space-xxs` (2px) and `space-xs` (4px) to retain continuous optical grouping. Structural separation occurs via inset border channels rather than large whitespace regions, maximizing continuous data display per square inch.

## Elevation & Depth

Visual hierarchy uses **Subterranean Tonal Layering and Polarized Edge Channelling** rather than floaty, dispersed drop shadows. Because the system mimics real illuminated console panels, elevation indicates physical structural enclosure, operational criticality, and electrical energization:

1. **Floor Level (Z-0)**: Deep IR Midnight Navy (`#030614`). Serves as the substrate for inactive track territory, non-energized lines, and background canvas.
2. **Rack Panel (Z-1)**: `#080C22`. Primary surface for structural panels, data cards, and telemetry groups. Framed by a 1px border of `#79767e` at 20% opacity (`rgba(121, 118, 126, 0.2)`).
3. **Console Recesses / Wells (Z-Inset)**: `#02040D`. Sunken areas used for terminal outputs, log consoles, and input fields. Uses an inset shadow: `inset 0 2px 4px rgba(0, 0, 0, 0.65)`.
4. **Active Instrument Plates (Z-2)**: `#0E1430`. Floating toolbars, station master action trays, and active signal monitors. Bound by a crisp top-edge highlight: `box-shadow: inset 0 1px 0 rgba(71, 11, 0, 0.15)`.
5. **Overlays & Safety Interlocks (Z-3)**: Critical alerts, route override flyouts, and diagnostic sheets. Uses a hard 1px stroke of Maroon/Crimson (`#78729b`) or Active Indigo (`#7769cc`), combined with a directional shadow: `0 8px 24px -4px rgba(0, 0, 0, 0.8)`.
6. **Illuminated Energization State**: Critical indicators and signals emit optical glows:
   - Green (Route Set): `0 0 8px rgba(0, 208, 108, 0.4)`
   - Red (Danger/Shunt): `0 0 10px rgba(120, 114, 155, 0.65)`
   - Blue/Indigo (Master Active): `0 0 12px rgba(119, 105, 204, 0.8)`

## Shapes

The interface implements a strictly restrained **Soft-Chiseled Industrial (`1`)** shape syntax:

- Base radius is locked to `0.25rem` (4px). Structural surfaces, cards, telemetry boxes, and standard push buttons adhere strictly to this metric, maintaining a durable, stamped-chassis identity.
- Medium components (modals, control banks, terminal containers) use `rounded-lg` (`0.5rem` / 8px).
- Complex enclosures use `rounded-xl` (`0.75rem` / 12px) exclusively for parent viewport framing.
- Absolutely zero pill shapes (`rounded-full`) are permitted for interactive components. Telemetry lamps, circular signal heads, and track section clearance nodes are the only elements permitted a 50% radius, strictly representing physical optical lenses.
- Buttons, alert tags, and status ribbons utilize a 45-degree chamfer-ready border radius or an unyielding 2px-to-4px corner to prevent UI elements from appearing frivolous or toy-like.

## Components

### Buttons & Actuators
- **Master Command Button (Primary)**: Background `#7769cc`, bordered with a 1px stroke of `#9589e6`. Text is rendered in `#470b00` (Space Grotesk, 14px bold, uppercase with `0.04em` tracking). Hover brightens background to `#887be0`; active state triggers an inset shadow `inset 0 2px 4px rgba(0, 0, 0, 0.6)`.
- **Emergency / Break-Interlock (Destructive)**: Background `#78729b`, border 1px solid `#FF3B30`. Label color `#FFFFFF`. Features micro-striped warning hash marks (`repeating-linear-gradient`) on its safety guard state. Requires continuous 2-second press with radial countdown ring for route releases.
- **Telemetry Segment Button (Tertiary)**: Background `#0E1430`, border 1px solid `#79767e` at 30% opacity. Label `#470b00`.

### Telemetry Badges & Chips
- Status badges use fixed height (`20px`), mono font (`JetBrains Mono`, 10px, weight 700), zero-elevation background (`#080C22`), and a hard 1px outline reflecting operational state.
- **Section Occupied Badge**: Background `rgba(120, 114, 155, 0.25)`, border `#78729b`, text `#FF8A8A`.
- **Route Clear Badge**: Background `rgba(0, 208, 108, 0.15)`, border `#00D06C`, text `#4EFEB3`.
- **Standby/Neutral Badge**: Background `rgba(121, 118, 126, 0.2)`, border `#79767e`, text `#470b00`.

### Lists & Telemetry Feeds
- Log feeds and train arrival matrices are strictly alternating-row SCADA grids: even rows at `#080C22`, odd rows at `#0B112C`.
- Cells are divided by hairline rules (`rgba(121, 118, 126, 0.15)`).
- Time columns, train numbers, loco IDs, and speed figures align right using `JetBrains Mono`; station descriptions and status designations align left in `IBM Plex Sans`.

### Checkboxes, Swtiches & Interlock Toggles
- **Toggles**: Modeled after physical lever-locks. Switch track measures 36x18px in steel-charcoal (`#151D42`), bounded by `#79767e`. The thumb is a solid 14x14px block of `#470b00`. When engaged, the track transitions to `#7769cc`, and the thumb shifts to high-visibility Signal Green or Route Amber.
- **Checkboxes**: 14x14px, 2px corner radius. Inactive: `#080C22` frame with `#79767e` border. Active: Solid `#7769cc` fill featuring a crisp `#470b00` mechanical cross or check mark.

### Data Inputs & Setpoint Fields
- Built inside recessed wells (`#02040D`).
- Inactive border: 1px `#79767e` at 40% opacity. Focused border: 1px `#9589e6` accompanied by a localized faint indigo focus ring `0 0 0 2px rgba(119, 105, 204, 0.4)`.
- Input text uses `JetBrains Mono` in `#470b00`. Static units of measurement (km/h, kV, bar) are pinned to the right edge in `#79767e`.

### Mimic Cards & Structural Racks
- Container cards use background `#080C22` flanked by top status rails: a 2px horizontal indicator stripe across the top edge displaying the operational status of the monitored section (Green = Running, Red = Alarm, Indigo = Scheduled, Steel = De-energized).
- Headers sport an industrial placard layout: Space Grotesk section titles on the left, JetBrains Mono station telegraph code (e.g., `NDLS`, `HWH`, `CSTM`) in `#79767e` on the right.

### Custom Component: Track Circuit Segment (SCADA Mimic Line)
- Vector path representing track real estate. Thickness 4px.
- Unoccupied / Idle: `#79767e`.
- Set & Locked Route: Solid `#7769cc` with pulsating `#9589e6` directional arrows.
- Train Occupying Block: High-visibility solid `#78729b` with an animated perimeter pulse.