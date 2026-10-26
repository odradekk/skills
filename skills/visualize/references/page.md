# HTML pages

## Build

- **Self-contained:** CSS and JavaScript inline, no network requests at all: no CDN scripts, web fonts, remote images, or fetch calls, so the page works offline and loads instantly. Draw figures as inline SVG or plain HTML and CSS. Mermaid needs a script from the network, so in a page, draw the same diagram as SVG instead.
- **Content first:** the main point in one sentence at the top. Each section carries one figure with a one-line caption saying what the figure shows and what to notice. Use real names, paths, numbers, and short code excerpts from the repository; long detail goes inside `<details>`.
- **Interaction only where it helps:** a stepper that walks through a flow one step at a time, a toggle between before and after, a term that shows its definition on hover and on tap. Every control works from the keyboard.
- **Layout:** text columns no wider than `40em`, which keeps lines readable in both Chinese and English; works from about 400 pixels wide up; the system font stack; light and dark themes through `prefers-color-scheme`.
- **Color carries meaning consistently,** such as added and removed, or one color per component, and never alone: pair it with a label, a symbol, or a line style.
- **Accessible figures:** each SVG has a `<title>` and an `aria-label`.
- **Words:** in the reader's language, by the principles of the `plain-language` skill.

## Open

Open the page with the system's opener: `open <path>` on macOS, `xdg-open <path>` on Linux, `start "" "<path>"` from `cmd` or `explorer <path>` on Windows. When your harness can show an HTML file itself, in a preview pane or a side panel, that works too.

## Check

- The page loads nothing from the network: search it for `http`, and confirm every hit is a plain link for reading, not a `src`, a stylesheet, or a fetch.
- The scripts parse: save the contents of each `<script>` block to a file in the same temporary directory and run `node --check` on it, when Node is installed.
- When you can drive a browser, load the page at desktop and phone widths, in light and dark themes, and confirm that every figure renders and every control works.

Done when the page opens, loads nothing from the network, and its scripts parse.
