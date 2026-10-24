---
name: VicDar Linux
description: A graphite expedition-kit desktop for XFCE 4.20 / GTK3, with one safety-orange tag on whatever is live.
colors:
  live: "#FF6B1A"
  live-hover: "#FF8240"
  rail: "#1C1F21"
  well: "#1E2123"
  ground: "#26292C"
  raised: "#2F3438"
  hover: "#383E42"
  rule: "#3A4045"
  rule-dim: "#33383C"
  bone: "#E9E6DF"
  glyph: "#C9C5BD"
  slate: "#9AA1A7"
  title-dim: "#8A9198"
  muted: "#6B737A"
  field: "#31373C"
  contour: "#383F44"
  contour-index: "#414950"
  danger: "#E5534B"
  danger-press: "#C9443D"
  warning: "#E5B567"
  ok: "#8CC265"
typography:
  ui:
    fontFamily: "Overpass, sans-serif"
    fontSize: "10pt"
    fontWeight: 400
  window-title:
    fontFamily: "Overpass, sans-serif"
    fontSize: "10pt"
    fontWeight: 600
  rail-time:
    fontFamily: "Overpass, sans-serif"
    fontSize: "11pt"
    fontWeight: 600
    fontFeature: "\"tnum\""
  rail-date:
    fontFamily: "Overpass, sans-serif"
    fontSize: "8pt"
    fontWeight: 400
    fontFeature: "\"tnum\""
  workspace-tag:
    fontFamily: "Overpass, sans-serif"
    fontSize: "10pt"
    fontWeight: 600
  mono:
    fontFamily: "Overpass Mono, monospace"
    fontSize: "11pt"
    fontWeight: 400
rounded:
  none: "0px"
  hairline: "1px"
  control: "2px"
spacing:
  frame-border: "2px"
  live-tag: "4px"
  menu-item: "5px 12px"
  tab: "5px 14px"
  terminal: "8px 12px"
  title-bar: "28px"
  rail: "48px"
components:
  button:
    backgroundColor: "{colors.raised}"
    textColor: "{colors.bone}"
    rounded: "{rounded.control}"
  button-hover:
    backgroundColor: "{colors.hover}"
  button-active:
    backgroundColor: "{colors.rail}"
  button-suggested:
    backgroundColor: "{colors.live}"
    textColor: "{colors.rail}"
    rounded: "{rounded.control}"
  button-suggested-hover:
    backgroundColor: "{colors.live-hover}"
  button-destructive:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.rail}"
    rounded: "{rounded.control}"
  entry:
    backgroundColor: "{colors.well}"
    textColor: "{colors.bone}"
    rounded: "{rounded.control}"
  menu:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.bone}"
    rounded: "{rounded.control}"
    padding: "4px 0"
  menu-item:
    padding: "{spacing.menu-item}"
  menu-item-hover:
    backgroundColor: "{colors.live}"
    textColor: "{colors.rail}"
  rail:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.bone}"
    width: "{spacing.rail}"
  workspace-tag:
    textColor: "{colors.slate}"
    rounded: "{rounded.control}"
    padding: "3px 0"
  workspace-tag-current:
    backgroundColor: "{colors.live}"
    textColor: "{colors.rail}"
  window-title-active:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.bone}"
    height: "{spacing.title-bar}"
  window-title-inactive:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.title-dim}"
    height: "{spacing.title-bar}"
  notification:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.bone}"
    rounded: "{rounded.control}"
  terminal:
    backgroundColor: "{colors.well}"
    textColor: "{colors.bone}"
    typography: "{typography.mono}"
    padding: "{spacing.terminal}"
---

# Design System: VicDar Linux

## Overview

**Creative North Star: "The Expedition Kit"**

The desktop is packed like field gear: a matte graphite rail clipped to the left edge, every workspace a numbered gear tag, and one safety-orange tag on whatever is live. Surfaces are powder-coat graphite separated by 1px rules, never by shadow, gradient or glow. Text is warm bone on graphite; secondary text is slate. The wallpaper is a slate topographic map drawn by a script in the repository.

The desktop stays quiet so terminal and VSCodium can do the work. Orange is the only colour that means anything, so on an unfamiliar machine the eye finds the current workspace, the focused window, the selection and the main action without searching. Everything is native GTK3 and XFCE: the theme sits on Adwaita dark for widget coverage and overrides its colours, borders and corners.

The system must run on a 4 GB laptop with old Intel graphics. No blur, no transparency, no fades or slides, no compositor shadows.

**Key Characteristics:**
- A left rail, 48px wide, solid graphite: no bottom taskbar, no top bar plus dock.
- One reserved colour: safety orange, painted solid on live things only.
- Flat graphite surfaces, 1px rules, 2px control corners, square window frames.
- One family: Overpass for all UI, Overpass Mono for terminal and editor, tabular figures in status text.
- Generated, reproducible artwork: wallpaper and window frames come from `tools/gen-theme-assets.py`.

## Colors

Matte graphite neutrals with warm bone text and one safety-orange accent; status colours appear only where a state needs them.

### Primary
- **Safety Orange** (`live`): the live colour. Selection, keyboard focus outline, the current workspace tag, the focused window's title tag, the focused app's rail indicator, the open tab's top stroke, check/switch/slider fill, progress, the text caret and terminal cursor, and the suggested (main) action. Text on orange is always `rail` graphite, never white.
- **Hot Orange** (`live-hover`): hover state of an orange button only.

### Neutral
- **Rail Graphite** (`rail`): the panel rail, active title bars, header bars, toolbars, menus, popovers, tooltips, notifications, the Whisker menu. Also the ink on orange.
- **Well Graphite** (`well`): text wells: views, lists, sidebars, entries, terminal and editor backgrounds.
- **Window Graphite** (`ground`): window ground, inactive title bars, disabled controls, the open tab.
- **Raised Graphite** (`raised`): buttons at rest; hover for list rows, rail buttons and flat buttons.
- **Hover Graphite** (`hover`): hover for regular buttons.
- **Rule** (`rule`): every 1px border and separator; scrollbar thumbs. `rule-dim` is the inactive window frame's rule.
- **Bone** (`bone`): primary text and symbolic glyphs (tray, session button).
- **Glyph Bone** (`glyph`): window-button glyphs on an active frame.
- **Slate** (`slate`): secondary text: dim labels, accelerators, placeholders, statusbars, notification bodies, idle workspace numerals.
- **Title Slate** (`title-dim`): inactive window titles.
- **Muted Slate** (`muted`): disabled text, inactive window glyphs, the running (unfocused) app indicator, hovered tag/notification borders.
- **Field** (`field`), **Contour** (`contour`), **Index Contour** (`contour-index`): wallpaper only. The field is lighter than the rail, so the rail needs no edge rule.

### Status
- **Danger** (`danger`): destructive buttons, the close button's hover (`danger-press` when pressed), error colour.
- **Warning** (`warning`) and **OK** (`ok`): GTK warning/success colours; also the terminal's yellow and green.

### Named Rules
**The One Live Colour Rule.** Orange marks what is live right now: selected, focused, current, running in front, or the one main action. Never decoration, never a brand stripe, never two competing orange areas inside one control. If a new element is orange, ask what it is the live instance of.

**The Graphite Ink Rule.** Anything on orange or danger red is drawn in `rail` graphite.

## Typography

**UI Font:** Overpass (variable, OFL, shipped in `overlay/usr/share/fonts/truetype/overpass/`)
**Mono Font:** Overpass Mono (same source)

**Character:** A sturdy, signage-like grotesque with its own mono, so UI and code read as one kit.

### Hierarchy
- **Window title** (SemiBold 600, 10pt): xfwm4 titles, left-aligned, 8px in from the tag.
- **UI** (Regular 400, 10pt): all GTK text (`xsettings` FontName). The greeter uses 11pt.
- **Rail time** (SemiBold 600, 11pt, tabular): clock hours `HH:MM`.
- **Rail date** (Regular 400, 8pt, tabular, uppercase month): `24 OCT` under the time.
- **Workspace tag** (SemiBold 600, UI size): the numerals 1 to 4.
- **Mono** (Regular 400, 11pt terminal, 14px editor): terminal, VSCodium editor and integrated terminal; GTK MonospaceFontName is Overpass Mono 10.

### Named Rules
**The Steady Numerals Rule.** Every label on the rail uses tabular figures (`font-feature-settings: "tnum"`), so ticking numbers never shift the rail.

## Layout

The screen is a left rail plus a free field. The rail is a deskbar-mode xfce4-panel, 48px, locked to the left edge, full height, with 24px icons. Top to bottom: app menu (grid icon), four workspace tags, a line separator, pinned and running apps, a flexible gap, the tray (network, volume, power), the clock, the session button. The desktop shows no icons. New windows open centred.

Spacing is small and fixed, sized for 1366x768 as much as 1080p: menu items 5px by 12px, menu padding 4px top and bottom, tabs 5px by 14px, rail app buttons 8px vertical padding, workspace tags 3px by 10px margin, terminal text 8px by 12px from the edge (set in skel user CSS because xfce4-terminal overrides theme padding).

## Elevation & Depth

Flat. Depth comes from three graphite steps (well below ground below raised) and 1px rules, never from shadows. xfwm4 frame, popup and dock shadows are off; every GTK `box-shadow` is `none`. The only `box-shadow` values are inset solid strokes used as orange tags: the open tab (2px top), the Whisker category (3px left), the Thunar path segment (2px bottom), and the 1px inner ring on a focused entry.

### Named Rules
**The No Shadow Rule.** Layers separate by tone and a 1px rule. A soft shadow, glow or gradient is a defect.

## Shapes

Controls have tight 2px corners (buttons, entries, checks, switches, menus, tooltips, notifications, workspace tags). Troughs and fills use 1px. Window frames, rail buttons and scrollbar thumbs are square. Window frames are a 1px rule plus 1px ground (2px side and bottom border) under a 28px title bar whose top row is the rule.

**The Tag Rule.** Live state is shown as a solid orange tag on an edge: 4px at the left end of the focused title bar, a rail indicator on the focused app, a 2 to 3px inset stroke on tabs and menu categories. Tags are solid fills, not outlines with glow.

## Components

### Rail
- **Style:** solid `rail`, no edge rule, no shadow. Buttons transparent and square; hover and checked use `raised`.
- **Apps (docklike):** focused app gets an orange edge indicator; running but unfocused apps get a `muted` indicator. No previews, no window counts.
- **Tray and session:** symbolic bone glyphs only. The session button is a launcher with a bone SVG power glyph, because the stock actions plugin icons are coloured.

### Workspace tags
- **Shape:** 1px `rule` border, 2px corners, SemiBold numerals in `slate`.
- **Hover:** numerals `bone`, border `muted`.
- **Current:** filled `live`, numerals `rail`. Exactly four workspaces, named 1 to 4.

### Window frame (xfwm4)
- **Active:** `rail` title bar, `bone` title, `glyph` buttons, 4px orange tag at the far left (painted into the leftmost menu button because xfwm clips the top-left corner).
- **Inactive:** `ground` title bar, `title-dim` title, `muted` glyphs, `rule-dim` edges, no tag.
- **Buttons:** layout menu at left, minimise/maximise/close at right, 28px square, no spacing. Hover `rule-dim` graphite with bone glyph; close hovers `danger` with graphite glyph.
- **Source:** all XPMs and `themerc` are written by `tools/gen-theme-assets.py`; change the constants there and regenerate, never hand-edit XPMs.

### Buttons
- **Default:** `raised` fill, 1px `rule`, 2px corners, no gradient or text shadow. Hover `hover`; pressed or checked `rail`.
- **Suggested action / default focus:** `live` fill and border, `rail` label; hover `live-hover`.
- **Destructive:** `danger` fill, `rail` label.
- **Flat:** transparent until hover (`raised` plus rule).

### Inputs
- **Entry:** `well` fill, 1px `rule`, 2px corners, orange caret. Focus: orange border plus 1px inset orange ring. Placeholder `slate`; disabled `ground` with `muted` text. Progress inside an entry is a 2px orange underline.
- **Check / radio / switch:** `well` with `slate` (checks) or `rule` (switch) border; checked is solid `live` with graphite mark. Switch knob `bone`.
- **Scale / progress:** `well` trough with rule, orange fill, `bone` slider.
- **Scrollbar:** 6px square `rule` thumb on a transparent track, `muted` on hover, orange while dragged.

### Menus, popovers, tooltips
- **Style:** `rail` with a 1px `rule` frame and 2px corners. Items 5px by 12px; hover fills `live` with graphite text; accelerators `slate`; separators 1px `rule`.
- **Whisker menu:** 400 by 450, a single frame on `rail`; favourites are terminal, VSCodium, Firefox, Thunar. The selected category is `raised` with a 3px orange inset at the left. Settings, lock and logout buttons are hidden from its header.

### Tabs
- Header `rail`; tabs `slate` text, hover `bone` on `raised`; the open tab is `ground` with a 2px orange top stroke.

### Notifications
- Opaque `rail` card, 1px `rule` (hover `muted`), 2px corners. Summary SemiBold `bone`, body `slate`. Buttons match default buttons; progress orange. No fade-out, no slide-out.

### Terminal and editor
- **Terminal:** `well` background, `bone` text, Overpass Mono 11, orange block cursor with graphite text, orange selection with graphite text, no scrollbar, 100x30 default. ANSI palette, normal then bright: `#2A2E31 #E5534B #8CC265 #E5B567 #6CA0DC #C397D8 #5FB3B3 #C9C5BD` / `#5A6168 #F07068 #A6D785 #F2CC8F #8FB8E8 #D6B3E6 #7FCCCC #F4F2EE`.
- **VSCodium:** native title bar, Default Dark Modern with colour overrides: editor and panel `well`, activity, title and status bars `rail`, side bar and inactive tabs `#24282B`, borders `rule`, status text `slate`. Orange is the active tab top border, active activity-bar edge, focus border, cursor, primary button, badges and progress. List selection stays graphite (`rule` active, `raised` inactive) so orange keeps one meaning.

### Wallpaper
- An SVG topographic map, 1920x1080 scaled with `slice`: `field` ground, regular contours in `contour` at 1.1px, every fifth (index) contour in `contour-index` at 1.7px. Drawn deterministically by `tools/gen-theme-assets.py` from a fixed integer seed; change the seed to draw a different terrain. The generator asserts the file stays under 1.5 MB and has more than 40 lines. The LightDM greeter uses the same wallpaper, the VicDar theme, Overpass 11 and no user image.

## Do's and Don'ts

### Do:
- **Do** take every colour from the named `@define-color` palette in `themes/VicDar/gtk-3.0/gtk.css` (or the matching constants in `tools/gen-theme-assets.py`).
- **Do** keep orange for live state only, and put `rail` graphite text on it.
- **Do** separate surfaces with a 1px `rule` and a graphite tone step.
- **Do** use 2px corners on controls and square window frames.
- **Do** use tabular figures for any number on the rail.
- **Do** regenerate the wallpaper and xfwm4 frames with `python3 tools/gen-theme-assets.py` instead of editing the outputs.
- **Do** keep symbolic glyphs in `bone` on the rail.

### Don't:
- **Don't** add shadows, glow, gradients, blur or transparency; old laptops and the flat graphite look both rule them out.
- **Don't** add fades, slides or other animation to notifications, menus or windows.
- **Don't** use orange for decoration, headings, branding or hover on neutral controls.
- **Don't** move the rail to the bottom or top, or add a dock; the left rail is the layout.
- **Don't** use white text on orange or red.
- **Don't** add a font beyond Overpass and Overpass Mono, or any non-redistributable font, icon or image.
- **Don't** copy the Windows or macOS look one-to-one, and don't use Debian branding.
