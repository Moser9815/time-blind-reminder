# Time Blind Reminder — PRD

## Goal
A solar-powered e-ink calendar display for someone with ADHD time blindness. The problem isn't reading a clock — it's that "11:00 standup" feels imaginary until 10:58. The device makes time *visible* and *spatial*: a giant countdown to the next event, plus a vertical day timeline showing the literal shape of remaining hours. Glanceable from across the room. Lives on a windowsill, runs forever on sunlight.

Owner: Robert Moser (personal project; not for distribution).

## User principles

These are non-negotiable. Every UI decision traces back to these. Each principle has a stated mechanism (what cognitive deficit it targets) and a source. See "Evidence base" at the bottom for caveats — most support is theoretical/clinical-consensus, not direct UI RCT evidence.

1. **Externalize time. Information lives in the environment, not in working memory.**
   *Targets*: time-based prospective memory failure; ADHD's collapsed temporal horizon.
   *Source*: Barkley (1997, 2012); Solanto (2011). Core principle of CBT-for-adult-ADHD; the "point of performance" maxim — the cue must be present at the place and moment the action happens.

2. **Show time as a depleting resource, not an abstract numeral.**
   *Targets*: deficit in perceptual time estimation/reproduction (meta-analytic effect sizes g ≈ 0.5–0.7).
   *Source*: Barkley (1997, 2012); Janeslätt et al. (2017) — the only direct RCT on visual-time interventions in ADHD (n=38, positive on time-processing and parent-rated daily time management).
   *Implementation*: countdown numerals AND shrinking spatial elements (depleting bar, vanishing timeline slot). Pure "3:42 PM" digital wall-clock does not satisfy this.

3. **Externalize the day's structure spatially.**
   *Targets*: weak nonverbal working-memory representation of time horizons ("temporal myopia").
   *Source*: Barkley (1997, 2012); CHADD (2024) clinical guidance on day planners.
   *Implementation*: vertical timeline of working hours showing where in the day you are, with completed slots visually distinct from upcoming ones.

4. **Surface "next," de-emphasize "later."**
   *Targets*: time-based prospective memory — the single most consistently impaired PM type in ADHD across child and adult studies.
   *Source*: Altgassen et al. (2013); Talbot & Kerns (2014).
   *Implementation*: hero pixel allocation goes to the next event. Later events appear on the timeline but at reduced visual weight.

5. **Escalate salience as deadlines approach.**
   *Targets*: temporal/delay discounting — distant events feel weak; ADHD groups choose smaller-sooner over larger-later more often (small-to-medium meta-analytic effects).
   *Source*: Jackson & MacKillop (2016); Marx et al. (2021); Sonuga-Barke (2003) delay aversion model.
   *Implementation*: imminent-event indicator (red, larger, higher contrast) triggers as a meeting approaches. Non-imminent events stay in ink (calm).

6. **Be a peripheral resource, not an attention demand.**
   *Targets*: notifications worsen inattention/hyperactivity even in non-ADHD users; ADHD users habituate to repetitive notifications faster.
   *Source*: Kushlev, Proulx, & Dunn (2016); Massa & O'Desky (2012) on impaired visual habituation.
   *Implementation*: ambient display, glanceable from 6+ feet, no buzzer, no LED, no audio. The user encounters information passively.

7. **Live in one fixed place to act as a context cue.**
   *Targets*: leverages context-stable cue→action association (Barkley's "point of performance"); a device that always lives in the same spot becomes part of the prospective-memory scaffold, not just an information source.
   *Source*: Barkley (2012). Convergent with habit research (Wood & Neal, 2007).
   *Implementation*: form factor and mounting (windowsill, desk corner) presume one stable home location.

8. **Reserve high-salience signals for the single most imminent thing.**
   *Targets*: ADHD shows altered salience processing — too many "high-salience" elements compete and the actually-important one loses.
   *Source*: Hauser et al. (2015).
   *Implementation*: red is used ONLY for the active countdown / imminent-event marker. Never decorative. Tri-color discipline (paper / ink / red) is itself a salience budget.

---

Principles 9 and 10 are aesthetic / production-layer constraints, downstream of the cognitive principles 1–8. They do not override 1–8 — they govern *how* those principles are realized in pixels.

9. **Designed at panel resolution.**
   *Targets*: not a cognitive deficit — a production-quality requirement. The 800×480 tri-color e-ink panel (≈100 ppi at typical viewing distance) cannot render thin strokes, small type, or fine detail without aliasing/jaggedness that defeats glanceability (Principle 6). Detail that the browser preview renders cleanly via subpixel anti-aliasing collapses to broken edges after the panel quantizes to three colors.
   *Source*: not science — design constraint. Panel spec from `eink-calendar/hardware/BOM.md` (Waveshare 7.5" tri-color, GDEY075Z08, 800×480).
   *Implementation* (concrete minimums — these are floors, not targets):
   - Body text: ≥ 18px (~14pt at this DPI)
   - Labels (NOW / NEXT / TODAY / hour ticks): ≥ 16px, ALL CAPS, ≥0.1em letter-spacing
   - Headlines (event titles): ≥ 28px
   - Hero countdown: ≥ 92px (already met by current spec)
   - No stroke, border, or divider thinner than 2px
   - No element smaller than ~40×40px as a glanceable region. **Exempt**: structural strokes (dividers, depletion bars, the now-marker on the rail edge) are 1D linear elements, not regions, and may be smaller along the short axis. They still must be ≥2px on the stroke axis.
   - No more than ~6 distinct text elements visible at once on the canvas
   - Padding: minimum 24px between major zones, minimum 12px within a zone
   - No serif faces, no italics, no font weights below 500

10. **Teenage Engineering visual language.**
    *Targets*: aesthetic coherence and product feel. The device is for personal use; the user wants it to read as a Teenage Engineering object (OP-1, TX-6, OB-4, EP-133, computer-1) rather than a generic information dashboard.
    *Source*: not science — explicit user direction (2026-04-29).
    *Implementation*:
    - **Typography**: pick ONE technical numerals family from the geometric-sans / monospace canon (e.g. Space Mono, JetBrains Mono, Berkeley Mono, NB Architekt, IBM Plex Mono, Suisse Int'l Mono) and use it for ALL contextual numerals (clock, hour ticks, meta lines, durations). Tabular figures (`font-feature-settings: "tnum" 1`) required. Labels in ALL CAPS with ≥0.1em tracking. **One optional display face** (e.g. Doto) is permitted exclusively for the single hero numeral — this is Nothing's "one moment of surprise" rule, allowing a deliberate departure from the technical face for the screen's primary signal.
    - **Layout**: strong functional grid. Label-next-to-value pairs, the way labels sit next to controls on a hardware front panel. Generous negative space — fewer elements, larger.
    - **Forms**: rounded rectangles with one consistent radius (recommend 6px). Hard edges. No drop shadows, no gradients, no inner glows.
    - **Color discipline**: already satisfied by the 3-color e-ink palette. Red is the functional code color for "active / now," never decoration (this also restates Principle 8).
    - **Decorative restraint**: every line, label, and block must have a function. If removing it does not lose meaning, remove it. No ornamental rules, no secondary "accent" lines, no flourishes.
    - **Iconography** (if any): blocky, designed *at* the target resolution, not scaled down vector art.

## Anti-patterns (do NOT add these — they have counter-evidence)

- **No push notifications, alarms, or audible beeps.** Smartphone notifications increase inattention/hyperactivity symptoms even in neurotypical users (Kushlev et al., 2016); ADHD users habituate to repetitive cues faster (Massa & O'Desky, 2012). Ambient display is the explicit alternative.
- **No "always show full week with equal weight."** Equal-weight future events compete with the imminent one and reduce its salience — temporal discounting working *against* the user (Sonuga-Barke, 2003).
- **No built-in Pomodoro / fixed time-boxing as default.** Clinician-popular but lacks high-quality RCT evidence in ADHD populations. If added later (parking lot), make it opt-in, not default.
- **No "tap to see status."** Any required interaction gates a prospective-memory event. The cue must be passively encountered (Barkley, 2012).
- **No uniform color/motion/size escalation across multiple elements.** Reserve escalation for the single most imminent item (Hauser et al., 2015).
- **No cramming detail.** Total information density is bounded by Principle 9. To add an element, remove an element first. The screen is not a dashboard.
- **No sub-minimum type sizes.** Anything under the Principle 9 floors (18px body / 16px label / 28px headline / 2px strokes) renders jagged after the panel quantizes — that directly undercuts the glanceability requirement of Principle 6.
- **No thin lines, hairlines, or 1px borders.** They render as broken segments at 100 ppi tri-color. Use 2px minimum, or replace lines with negative space and grid alignment.
- **No decorative elements without function.** Vector flourishes, ornamental rules, secondary "accent" lines that aren't structural — all violate Principle 10's restraint requirement *and* Principle 8's salience budget.

## Behavior

### Display states

- **Active workday with a current event**: hero is "X min" countdown to event end (red). Below: current event title + end time. Right: timeline with current slot highlighted.
- **Active workday between events**: hero is "X min" countdown to next event start (red if <30 min, ink otherwise). Below: next event title + start time + attendees.
- **Active workday with no upcoming events**: hero says "—" or hides; topbar shows date; timeline shows the workday with completed slots greyed.
- **Outside working hours**: TBD (parking lot: "rest" view showing tomorrow's first event)
- **Error / no network**: leave the previous frame on screen (e-ink persists with no power). The firmware retries on `RETRY_SECONDS` cadence.

### Refresh cadence

- Default refresh: every 15 minutes (`REFRESH_SECONDS=900` in `firmware/src/secrets.h`)
- Manual refresh: button press wakes immediately (`PIN_BUTTON=13`)
- Failure backoff: retry after `RETRY_SECONDS=60`. After `MAX_RETRIES=3` consecutive failures, sleep for the full refresh interval to conserve battery during outages.

### Calendar handling

- Source: Google Calendar via `calendar.readonly` OAuth scope
- Calendars used: configurable in `eink-calendar/ui/config.json` (defaults to `["primary"]`)
- All-day events: skipped. They have no `dateTime` and don't fit the timeline view.
- Recurring events: handled via `singleEvents=true` in the API call (Google expands them).
- Working hours window: 9:00–17:00, configurable in `config.json`.
- Attendee display: up to 60 chars of comma-joined non-self attendees on the "next" event. Truncated.

### Power

- Target: multiple weeks of buffer through cloudy weather
- Battery: 2500 mAh LiPo
- Active per cycle: ~15 sec (WiFi + HTTP + e-ink refresh)
- Sleep current target: ~10 µA
- Solar: 2W panel behind window glass, ~660 mAh/day generated assumption (5h sun × 50% loss)
- Daily consumption: ~48 mAh/day at default refresh rate
- Low-battery behavior: TBD (parking lot: warn at <3.6V on display)

## Hardware

- MCU: Adafruit Feather ESP32-S3 (4MB Flash / 2MB PSRAM) — product 5477. PSRAM required for framebuffers.
- Display: Waveshare 7.5" tri-color (B/W/R) e-paper, 800×480, GDEY075Z08 controller
- Battery: 2500 mAh LiPo
- Solar: 2W panel
- Charging: integrated on Feather
- Button: single momentary on `PIN_BUTTON=13`, also wakes from deep sleep
- Form factor: windowsill / desk corner. Eventual 3D-printed enclosure (parking lot).
- Mounting: TBD (kickstand + window suction in parking lot)

## Out of scope (explicit)

- **Multiple users / multi-tenant**: single user, single device. No accounts beyond the owner's Google login.
- **Bidirectional editing**: read-only calendar. Don't add the ability to create/edit events from the device.
- **Notifications / alarms**: see Anti-patterns. Passive ambient display is the deliberate alternative.
- **Always-online cloud service**: render server runs on the user's own machine (laptop or Pi). Not deploying a SaaS.
- **Color screen / animations**: tri-color e-ink is the medium. No backlight, no refresh-flash entertainment.
- **Apple Calendar / Outlook**: Google Calendar only for v1.

## Evidence base

Honest scoping of how grounded these principles actually are:

- **Strong**: ADHD time-perception and prospective-memory deficits are robustly replicated across meta-analyses (Zheng et al., 2022; Nejati & Yazdani, 2024; Altgassen et al., 2013). The general principle of "externalize executive function to the environment" is core to evidence-based CBT for adult ADHD (Safren et al., 2010; Solanto et al., 2010).
- **Moderate**: Visual time externalization (Time Timer-style) has one small RCT in ADHD children (Janeslätt et al., 2017, n=38) plus strong clinical-consensus support. The widely-cited "27% on-task improvement" Time Timer marketing claim does **not** appear in indexed peer review.
- **Theoretical / mechanistic**: Most of the specific UI choices (countdown vs clock, vertical timeline, red-for-imminent) are downstream applications of Barkley's executive-function theory (1997, 2012) rather than tested in their own UI-comparison RCTs.

What this means for product decisions: when a principle conflicts with another goal (e.g., "more visible later events would be nice"), defer to the principle, but don't pretend the literature dictates a specific pixel layout. The literature dictates direction; the design dictates form.

## References

Barkley, R. A. (1997). Behavioral inhibition, sustained attention, and executive functions: Constructing a unifying theory of ADHD. *Psychological Bulletin*, 121(1), 65–94.
Barkley, R. A. (2012). *Executive Functions: What They Are, How They Work, and Why They Evolved.* Guilford Press.
Altgassen, M., Kretschmer, A., & Schnitzspahn, K. M. (2013). Time-based prospective memory in adults with ADHD. *PLOS ONE*, 8(3), e58338.
CHADD (2024). Time Management and ADHD; Remembering the Future. chadd.org.
Hauser, T. U., et al. (2015). Altered salience processing in ADHD. *Human Brain Mapping*, 36(11), 4541–4551.
Jackson, J. N. S., & MacKillop, J. (2016). ADHD and monetary delay discounting: A meta-analysis. *Biological Psychiatry: CNNI*, 1(4), 316–325.
Janeslätt, G., Kottorp, A., & Granlund, M. (2017). Effectiveness of time-related interventions in children with ADHD aged 9–15 years: a randomized controlled study. *European Child & Adolescent Psychiatry*, 27(3), 329–342.
Kushlev, K., Proulx, J., & Dunn, E. W. (2016). "Silence Your Phones": Smartphone notifications increase inattention and hyperactivity symptoms. *Proceedings of CHI 2016*, 1011–1020.
Marx, I., Hacker, T., Yu, X., Cortese, S., & Sonuga-Barke, E. (2021). ADHD and the choice of small immediate over larger delayed rewards: A comparative meta-analysis. *Journal of Attention Disorders*, 25(2), 171–187.
Massa, J., & O'Desky, I. H. (2012). Impaired visual habituation in adults with ADHD. *Journal of Attention Disorders*, 16(7), 553–561.
Nejati, V., & Yazdani, S. (2024). Time-perception deficits in ADHD: A systematic review and meta-analysis. *Developmental Neuropsychology*, 49(1).
Safren, S. A., et al. (2010). Cognitive behavioral therapy vs relaxation with educational support for medication-treated adults with ADHD and persistent symptoms. *JAMA*, 304(8), 875–880.
Solanto, M. V., et al. (2010). Efficacy of meta-cognitive therapy for adult ADHD. *American Journal of Psychiatry*, 167(8), 958–968.
Solanto, M. V. (2011). *Cognitive-Behavioral Therapy for Adult ADHD: Targeting Executive Dysfunction.* Guilford Press.
Sonuga-Barke, E. J. S. (2003). The dual pathway model of AD/HD. *Neuroscience and Biobehavioral Reviews*, 27(7), 593–604.
Talbot, K. D. S., & Kerns, K. A. (2014). Event- and time-triggered remembering in children with ADHD. *Journal of Experimental Child Psychology*, 127, 126–143.
Zheng, Q., et al. (2022). Time perception deficits in children and adolescents with ADHD: A meta-analysis. *Journal of Attention Disorders*, 26(2), 267–281.
Wood, W., & Neal, D. T. (2007). A new look at habits and the habit-goal interface. *Psychological Review*, 114(4), 843–863.

## Change log

- 2026-04-29: Initial PRD seeded from existing code and `eink-calendar/README.md`. Captures current behavior, not future direction.
- 2026-04-29: User principles rewritten to be evidence-grounded — replaced the original three intuition-based principles with eight principles, each tied to a cognitive deficit and a source. Added Anti-patterns section with counter-evidence citations. Added Evidence base section noting honest scoping (most principles are theoretical/clinical-consensus, not direct UI RCT). Added References section.
- 2026-04-29: Added aesthetic / production-layer principles 9 (Designed at panel resolution — concrete minimums for type, strokes, padding, element count) and 10 (Teenage Engineering visual language — typography, layout, forms, decorative restraint). Added matching anti-patterns: cramming detail, sub-minimum type sizes, thin lines/hairlines, decorative elements without function. Trigger: user feedback that the current layout crams too much detail into elements too small for the panel resolution and lacks the desired Teenage Engineering look-and-feel.
