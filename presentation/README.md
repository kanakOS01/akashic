# Akashic presentation

This is a Reveal.js deck with automatic CSS motion, native fragments, auto-animate continuity, scripted terminal playback, responsive layouts, and print styling.

## Present locally

```sh
cd presentation
python3 -m http.server 4173
```

Open `http://localhost:4173`. Use one arrow-key or space-bar press per slide. Slides run their staged animation automatically. The workflow slide uses fragments, so continue pressing to reveal each step. Press `F` for full screen, `S` for speaker view, and `Esc` for overview.

## Structure

- `index.html`: slide content and Reveal.js markup
- `styles.css`: layouts, diagrams, motion, responsive behavior, and print styling
- `deck.js`: Reveal.js setup and terminal playback
- `fonts/`: bundled Bricolage Grotesque font files
- `Akashic_Reveal_Deck.pdf`: 14-page review export
- `Akashic_Reveal_Preview.mp4`: complete motion preview

The deck includes its Reveal.js runtime locally for reliable presenting, uses a 1280 by 720 stage, and uses the native macOS terminal font stack.
