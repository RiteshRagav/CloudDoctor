{
  "brand": {
    "product_name": "CloudDoctor",
    "visual_personality": [
      "dark, clean ops-tool aesthetic (Grafana/Datadog vibes)",
      "high-signal, low-noise", 
      "trustworthy + incident-response urgency",
      "dense data, but breathable spacing",
      "subtle depth (borders + soft shadows), no glossy gradients"
    ],
    "brand_attributes": {
      "sophisticated": "neutral graphite surfaces, restrained accents",
      "motivating": "clear status colors + progress cues + confidence meters",
      "trustworthy": "consistent tokens, predictable layouts, strong contrast"
    }
  },

  "design_tokens": {
    "notes": [
      "Use Tailwind + CSS variables (shadcn style) as the single source of truth.",
      "Dark theme only: set <html class=\"dark\"> at app root.",
      "Avoid purple. Primary accent is ocean-cyan/teal; secondary is amber for warnings."
    ],

    "css_custom_properties": {
      "path": "/app/frontend/src/index.css",
      "instructions": [
        "Replace the existing :root and .dark token blocks with the following (keep --radius).",
        "These are HSL triplets compatible with shadcn tokens.",
        "Keep chart tokens aligned with severity palette for monitoring charts."
      ],
      "token_block": "@layer base {\n  :root {\n    --background: 220 18% 98%;\n    --foreground: 222 47% 11%;\n\n    --card: 0 0% 100%;\n    --card-foreground: 222 47% 11%;\n\n    --popover: 0 0% 100%;\n    --popover-foreground: 222 47% 11%;\n\n    --primary: 199 89% 48%;\n    --primary-foreground: 210 40% 98%;\n\n    --secondary: 210 40% 96%;\n    --secondary-foreground: 222 47% 11%;\n\n    --muted: 210 40% 96%;\n    --muted-foreground: 215 16% 47%;\n\n    --accent: 199 89% 48%;\n    --accent-foreground: 210 40% 98%;\n\n    --destructive: 0 84% 60%;\n    --destructive-foreground: 210 40% 98%;\n\n    --border: 214 32% 91%;\n    --input: 214 32% 91%;\n    --ring: 199 89% 48%;\n\n    /* charts */\n    --chart-1: 199 89% 48%; /* cyan */\n    --chart-2: 160 84% 39%; /* green */\n    --chart-3: 38 92% 50%;  /* amber */\n    --chart-4: 0 84% 60%;   /* red */\n    --chart-5: 215 20% 65%; /* slate */\n\n    --radius: 0.75rem;\n\n    /* extra (non-shadcn) */\n    --surface-0: 220 18% 98%;\n    --surface-1: 220 16% 96%;\n    --surface-2: 220 14% 94%;\n    --shadow-color: 220 40% 2%;\n\n    --status-ok: 160 84% 39%;\n    --status-warn: 38 92% 50%;\n    --status-error: 0 84% 60%;\n    --status-info: 199 89% 48%;\n    --status-neutral: 215 20% 65%;\n  }\n\n  .dark {\n    --background: 222 22% 7%;\n    --foreground: 210 40% 98%;\n\n    --card: 222 22% 9%;\n    --card-foreground: 210 40% 98%;\n\n    --popover: 222 22% 9%;\n    --popover-foreground: 210 40% 98%;\n\n    --primary: 199 89% 52%;\n    --primary-foreground: 222 22% 7%;\n\n    --secondary: 222 18% 14%;\n    --secondary-foreground: 210 40% 98%;\n\n    --muted: 222 18% 14%;\n    --muted-foreground: 215 20% 70%;\n\n    --accent: 199 89% 52%;\n    --accent-foreground: 222 22% 7%;\n\n    --destructive: 0 72% 52%;\n    --destructive-foreground: 210 40% 98%;\n\n    --border: 222 16% 18%;\n    --input: 222 16% 18%;\n    --ring: 199 89% 52%;\n\n    /* charts */\n    --chart-1: 199 89% 52%;\n    --chart-2: 160 84% 42%;\n    --chart-3: 38 92% 54%;\n    --chart-4: 0 72% 52%;\n    --chart-5: 215 18% 62%;\n\n    /* extra (non-shadcn) */\n    --surface-0: 222 22% 7%;\n    --surface-1: 222 22% 9%;\n    --surface-2: 222 18% 12%;\n    --shadow-color: 220 40% 2%;\n\n    --status-ok: 160 84% 42%;\n    --status-warn: 38 92% 54%;\n    --status-error: 0 72% 52%;\n    --status-info: 199 89% 52%;\n    --status-neutral: 215 18% 62%;\n  }\n}\n"
    },

    "palette": {
      "backgrounds": {
        "app_bg": "hsl(var(--background))  #0f1116-ish",
        "panel_bg": "hsl(var(--card))  #121622-ish",
        "panel_bg_alt": "hsl(var(--surface-2))  #171c2a-ish"
      },
      "text": {
        "primary": "hsl(var(--foreground))",
        "muted": "hsl(var(--muted-foreground))",
        "inverse": "hsl(var(--primary-foreground))"
      },
      "accents": {
        "primary_cyan": "hsl(var(--primary))",
        "focus_ring": "hsl(var(--ring))",
        "link": "hsl(var(--primary))"
      },
      "status_semantics": {
        "healthy": "hsl(var(--status-ok))",
        "warning": "hsl(var(--status-warn))",
        "error": "hsl(var(--status-error))",
        "info": "hsl(var(--status-info))",
        "neutral": "hsl(var(--status-neutral))"
      },
      "severity_mapping": {
        "FATAL": "status-error",
        "ERROR": "status-error",
        "WARN": "status-warn",
        "INFO": "status-info",
        "DEBUG": "status-neutral"
      }
    },

    "gradients_and_texture": {
      "allowed_usage": [
        "Only as subtle section background overlays (hero header strip / top bar glow).",
        "Never on tables/log text areas.",
        "Keep gradient coverage under 20% viewport."
      ],
      "approved_gradients": [
        {
          "name": "cyan-slate-glow",
          "css": "radial-gradient(600px circle at 20% 0%, hsla(199, 89%, 52%, 0.18), transparent 55%), radial-gradient(500px circle at 80% 10%, hsla(160, 84%, 42%, 0.10), transparent 60%)"
        }
      ],
      "noise_overlay": {
        "css": "background-image: url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"160\" height=\"160\"><filter id=\"n\"><feTurbulence type=\"fractalNoise\" baseFrequency=\"0.8\" numOctaves=\"3\" stitchTiles=\"stitch\"/></filter><rect width=\"160\" height=\"160\" filter=\"url(%23n)\" opacity=\"0.06\"/></svg>');",
        "usage": "Apply to app background container via ::before overlay with pointer-events-none."
      }
    },

    "radius_shadow": {
      "radius": {
        "panel": "rounded-xl",
        "control": "rounded-lg",
        "pill": "rounded-full"
      },
      "shadow": {
        "panel": "shadow-[0_1px_0_hsla(0,0%,100%,0.04),0_12px_30px_hsla(var(--shadow-color),0.35)]",
        "inset": "shadow-[inset_0_1px_0_hsla(0,0%,100%,0.04)]"
      },
      "borders": {
        "default": "border border-border/70",
        "hover": "hover:border-border",
        "focus": "focus-visible:ring-2 focus-visible:ring-ring/60 focus-visible:ring-offset-0"
      }
    },

    "spacing": {
      "principle": "Use 2–3x more spacing than feels comfortable; prefer 24/32px section padding.",
      "layout": {
        "page_padding": "px-4 sm:px-6 lg:px-8",
        "page_vertical": "py-6 sm:py-8",
        "card_padding": "p-4 sm:p-5",
        "dense_table_padding": "py-2.5 px-3"
      }
    }
  },

  "typography": {
    "font_pairing": {
      "heading": {
        "name": "Space Grotesk",
        "google_fonts": "https://fonts.google.com/specimen/Space+Grotesk",
        "usage": "H1/H2, section titles, KPI numbers"
      },
      "body": {
        "name": "IBM Plex Sans",
        "google_fonts": "https://fonts.google.com/specimen/IBM+Plex+Sans",
        "usage": "UI labels, tables, paragraphs"
      },
      "mono": {
        "name": "IBM Plex Mono",
        "google_fonts": "https://fonts.google.com/specimen/IBM+Plex+Mono",
        "usage": "log lines, code-ish metadata"
      }
    },
    "implementation": {
      "instructions": [
        "Add Google Fonts <link> tags in public/index.html (CRA) for Space Grotesk + IBM Plex Sans + IBM Plex Mono.",
        "Set body font to IBM Plex Sans; headings use Space Grotesk via utility class (e.g., font-heading).",
        "For logs, apply font-mono and slightly smaller size with increased leading."
      ],
      "tailwind_utilities": {
        "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
        "h2": "text-base md:text-lg text-muted-foreground",
        "section_title": "text-sm font-medium tracking-wide text-muted-foreground uppercase",
        "kpi": "text-2xl sm:text-3xl font-semibold tabular-nums",
        "table": "text-sm",
        "log": "font-mono text-xs sm:text-sm leading-6"
      }
    }
  },

  "layout_and_navigation": {
    "global_shell": {
      "pattern": "Left sidebar + top utility bar + main content",
      "sidebar": {
        "width": "w-[280px] lg:w-[300px]",
        "mobile": "Use shadcn Sheet for sidebar drawer",
        "sections": [
          "Brand block (CloudDoctor + environment selector)",
          "Nav (Dashboard, Log Analyzer, AI Diagnosis, Reports)",
          "Health pills stack (4 services) pinned near top",
          "Footer meta (last check, API status)"
        ]
      },
      "content_grid": {
        "dashboard": "grid grid-cols-1 xl:grid-cols-12 gap-4 sm:gap-6",
        "dashboard_left": "xl:col-span-8",
        "dashboard_right": "xl:col-span-4"
      }
    },

    "page_skeletons": {
      "dashboard": [
        "Top row: Health pills (4) + Trigger Incident CTA",
        "Middle: Incident timeline / active incident card + mini charts (latency, errors)",
        "Right rail: Quick actions + recent incidents list"
      ],
      "log_analyzer": [
        "Header: severity filter chips + search input + pause/resume streaming toggle",
        "Main: log stream panel (ScrollArea) with sticky toolbar",
        "Side: counts by severity + sparkline"
      ],
      "ai_diagnosis": [
        "Left: incident selector + run diagnosis button",
        "Right: results card with root cause, recommended fixes, confidence meter, MTTR estimate",
        "Bottom: evidence (top log lines)"
      ],
      "reports": [
        "Table with density toggle + status filter",
        "Row click opens Drawer with incident details + lifecycle actions"
      ]
    }
  },

  "components": {
    "component_path": {
      "shadcn_primary": [
        "/app/frontend/src/components/ui/button.jsx",
        "/app/frontend/src/components/ui/badge.jsx",
        "/app/frontend/src/components/ui/card.jsx",
        "/app/frontend/src/components/ui/table.jsx",
        "/app/frontend/src/components/ui/tabs.jsx",
        "/app/frontend/src/components/ui/scroll-area.jsx",
        "/app/frontend/src/components/ui/skeleton.jsx",
        "/app/frontend/src/components/ui/tooltip.jsx",
        "/app/frontend/src/components/ui/dialog.jsx",
        "/app/frontend/src/components/ui/sheet.jsx",
        "/app/frontend/src/components/ui/select.jsx",
        "/app/frontend/src/components/ui/separator.jsx",
        "/app/frontend/src/components/ui/progress.jsx",
        "/app/frontend/src/components/ui/sonner.jsx"
      ],
      "recommended_new_components_to_create": [
        "/app/frontend/src/components/StatusPill.js",
        "/app/frontend/src/components/SeverityChip.js",
        "/app/frontend/src/components/LogLine.js",
        "/app/frontend/src/components/ConfidenceMeter.js",
        "/app/frontend/src/components/IncidentTimeline.js",
        "/app/frontend/src/components/EmptyState.js"
      ]
    },

    "component_specs": {
      "status_pill": {
        "base": "inline-flex items-center gap-2 rounded-full px-3 py-1.5 border border-border/70 bg-card/60 backdrop-blur supports-[backdrop-filter]:bg-card/40",
        "dot": "h-2.5 w-2.5 rounded-full",
        "states": {
          "healthy": "[--pill:theme(colors.emerald.400)]",
          "warning": "[--pill:theme(colors.amber.400)]",
          "error": "[--pill:theme(colors.red.400)]",
          "unknown": "[--pill:theme(colors.slate.400)]"
        },
        "dot_style": "bg-[hsl(var(--status-ok))] (swap per state)",
        "micro_interaction": "On hover: border becomes stronger + subtle lift (translate-y-[-1px]) with shadow; on click: press scale 0.98.",
        "testids": {
          "pill": "health-pill-{service-name}",
          "status_text": "health-pill-{service-name}-status"
        }
      },

      "severity_chip": {
        "use": "ToggleGroup (multi) or Badge as clickable filter chips",
        "base": "rounded-full px-3 py-1 text-xs font-medium border",
        "active": "bg-secondary text-foreground border-border",
        "inactive": "bg-transparent text-muted-foreground border-border/60 hover:text-foreground hover:border-border",
        "colors": {
          "ERROR": "data-[state=on]:bg-[hsla(0,72%,52%,0.18)] data-[state=on]:border-[hsla(0,72%,52%,0.35)]",
          "WARN": "data-[state=on]:bg-[hsla(38,92%,54%,0.16)] data-[state=on]:border-[hsla(38,92%,54%,0.35)]",
          "INFO": "data-[state=on]:bg-[hsla(199,89%,52%,0.14)] data-[state=on]:border-[hsla(199,89%,52%,0.35)]",
          "DEBUG": "data-[state=on]:bg-[hsla(215,18%,62%,0.14)] data-[state=on]:border-[hsla(215,18%,62%,0.30)]",
          "FATAL": "data-[state=on]:bg-[hsla(0,72%,52%,0.22)] data-[state=on]:border-[hsla(0,72%,52%,0.45)]"
        },
        "testids": {
          "chip": "log-severity-filter-{level}"
        }
      },

      "log_stream_panel": {
        "container": "rounded-xl border border-border/70 bg-card/50 backdrop-blur",
        "toolbar": "sticky top-0 z-10 flex flex-wrap items-center gap-2 border-b border-border/60 bg-card/70 px-3 py-2",
        "body": "h-[60vh] sm:h-[70vh]",
        "scroll": "Use <ScrollArea> for smooth scrolling; keep monospace.",
        "line": "grid grid-cols-[auto_1fr] gap-3 px-3 py-2 hover:bg-secondary/40",
        "timestamp": "text-xs text-muted-foreground tabular-nums",
        "message": "text-sm text-foreground/90",
        "badge": "Use Badge variant=outline with severity color border",
        "testids": {
          "panel": "log-stream-panel",
          "pause_button": "log-stream-pause-button",
          "search_input": "log-search-input"
        }
      },

      "confidence_meter": {
        "use": "Progress + numeric label",
        "layout": "flex items-center gap-3",
        "bar": "h-2 rounded-full bg-secondary",
        "fill": "bg-[hsl(var(--primary))]",
        "label": "text-sm text-muted-foreground",
        "value": "text-sm font-medium tabular-nums",
        "testids": {
          "meter": "diagnosis-confidence-meter",
          "mttr": "diagnosis-mttr"
        }
      },

      "incident_table": {
        "use": "shadcn Table",
        "density": "Default comfortable; add a density toggle (compact) that switches to smaller paddings.",
        "row": "hover:bg-secondary/40 cursor-pointer",
        "status_badge": "Badge with semantic colors (open=amber, diagnosed=cyan, resolved=green)",
        "testids": {
          "table": "incident-reports-table",
          "row": "incident-row-{incident-id}",
          "status": "incident-status-{incident-id}"
        }
      },

      "trigger_incident": {
        "use": "Dialog",
        "controls": "Select scenario + confirm button",
        "primary_cta": "Button variant=default with cyan accent",
        "danger_note": "Alert component for warning about simulation",
        "testids": {
          "open": "trigger-incident-open-button",
          "scenario": "trigger-incident-scenario-select",
          "confirm": "trigger-incident-confirm-button"
        }
      }
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Motion communicates state changes (streaming, incident created, diagnosis running).",
      "Keep durations short: 120–180ms for hover, 180–240ms for enter/exit.",
      "Avoid universal transition: never transition: all."
    ],
    "recommended_library": {
      "name": "framer-motion",
      "why": "Entrance animations for panels, subtle list updates, and loading skeleton transitions.",
      "install": "npm i framer-motion",
      "usage_scaffold_js": "import { motion, AnimatePresence } from 'framer-motion';\n\nexport default function Panel({ children }) {\n  return (\n    <motion.div\n      initial={{ opacity: 0, y: 6 }}\n      animate={{ opacity: 1, y: 0 }}\n      transition={{ duration: 0.22, ease: 'easeOut' }}\n    >\n      {children}\n    </motion.div>\n  );\n}\n"
    },
    "hover_states": {
      "buttons": "hover:brightness-110 active:scale-[0.98] transition-[filter,box-shadow] duration-150",
      "cards": "hover:border-border hover:shadow-[0_1px_0_hsla(0,0%,100%,0.05),0_18px_40px_hsla(var(--shadow-color),0.45)] transition-[box-shadow,border-color] duration-200",
      "rows": "transition-[background-color] duration-150"
    },
    "loading_states": {
      "use": "Skeleton for charts, tables, and diagnosis results; show streaming shimmer only in header strip (not on log text).",
      "toasts": "Use Sonner for incident triggered / diagnosis complete / resolve actions."
    }
  },

  "data_visualization": {
    "library": "recharts (already installed)",
    "chart_style": {
      "grid": "stroke: hsla(222,16%,18%,0.9) (dark) / hsla(214,32%,91%,0.6) (light)",
      "line": "stroke: hsl(var(--chart-1))",
      "thresholds": "Use ReferenceLine with amber/red for warn/error",
      "tooltip": "Use shadcn Tooltip/Popover styling; keep compact"
    },
    "recommended_widgets": [
      "Mini sparkline cards for error rate and latency",
      "Stacked bar for log counts by severity",
      "MTTR trend line in Reports"
    ]
  },

  "accessibility": {
    "requirements": [
      "WCAG AA contrast: muted text must still be readable on card backgrounds.",
      "Visible focus rings on all interactive elements (ring color = --ring).",
      "Keyboard navigation: sidebar, filters, table rows.",
      "Reduced motion: respect prefers-reduced-motion by disabling entrance animations."
    ],
    "aria_and_labels": [
      "All icon-only buttons must have aria-label.",
      "Log severity chips should announce pressed state (ToggleGroup handles)."
    ]
  },

  "image_urls": {
    "backgrounds": [
      {
        "category": "app-shell-background",
        "description": "Optional subtle abstract grid texture for login/empty states only (not behind log text). Apply with low opacity overlay.",
        "url": "https://images.unsplash.com/photo-1626123080782-10b336a160b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwyfHxkYXJrJTIwYWJzdHJhY3QlMjBncmlkJTIwdGV4dHVyZSUyMGJhY2tncm91bmR8ZW58MHx8fHRlYWx8MTc3NjM2NjY3Mnww&ixlib=rb-4.1.0&q=85"
      }
    ]
  },

  "instructions_to_main_agent": {
    "global": [
      "Remove default CRA App.css centering styles; do not use .App { text-align:center }.",
      "Set dark mode at root: <div className=\"dark\"> wrapping Router.",
      "Implement app background with subtle radial glow (approved gradient) + optional noise overlay via ::before.",
      "Use IBM Plex Mono for log lines; ensure line wrapping toggle (wrap vs no-wrap) for readability.",
      "All interactive and key informational elements MUST include data-testid in kebab-case (role-based).",
      "Use shadcn components from /src/components/ui only (no raw HTML dropdowns/calendars/toasts).",
      "Use Sonner for toasts (already present)."
    ],
    "page_specific": {
      "dashboard": [
        "Health pills: show service name + status + last check time; clicking opens HoverCard with details.",
        "Trigger Incident: Dialog with scenario Select + confirm; show Alert warning about simulation impact.",
        "Add mini charts using recharts in Cards; keep axes minimal and muted."
      ],
      "log_analyzer": [
        "Use ToggleGroup for severity filters; include counts per severity.",
        "Add Pause/Resume streaming Switch; show a small live indicator dot when streaming.",
        "Use ScrollArea for log list; keep toolbar sticky."
      ],
      "ai_diagnosis": [
        "Run button shows loading state; results animate in.",
        "Confidence meter uses Progress + numeric percent; MTTR displayed as pill.",
        "Recommended fixes as ordered list with copy buttons."
      ],
      "reports": [
        "Table rows open Drawer with details; include lifecycle actions (Diagnose/Resolve) with confirmation AlertDialog.",
        "Add status filter Select and a compact density toggle."
      ]
    },
    "testid_examples": [
      "sidebar-nav-dashboard-link",
      "sidebar-nav-log-analyzer-link",
      "dashboard-trigger-incident-button",
      "log-severity-filter-error",
      "ai-diagnosis-run-button",
      "reports-status-filter-select"
    ]
  },

  "General UI UX Design Guidelines": [
    "- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms",
    "- You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text",
    "- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json",
    "\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead.\n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
  ]
}
