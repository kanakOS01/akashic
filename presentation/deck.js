const terminalScripts = {
  init: [
    { text: "mkdir system-memory && cd system-memory", kind: "command", typed: true, pause: 250 },
    { text: "akashic init", kind: "command", typed: true, pause: 320 },
    { text: "created   .akashic/config.yaml", kind: "good", pause: 140 },
    { text: "created   services/ flows/ system/ entities/", kind: "good", pause: 140 },
    { text: "created   adr/ glossary/ README.md .gitignore", kind: "good", pause: 140 },
    { text: "initialized Git repository", kind: "info", pause: 180 },
    { text: "committed  Initialize knowledge repository", kind: "good", pause: 200 },
    { text: "ready      akashic attach <source>", kind: "accent", pause: 0 },
  ],
  generate: [
    { text: "akashic attach ../payments --name payments", kind: "command", typed: true, pause: 200 },
    { text: "attached   payments", kind: "good", pause: 180 },
    { text: "akashic attach ../identity --name identity", kind: "command", typed: true, pause: 200 },
    { text: "attached   identity", kind: "good", pause: 180 },
    { text: "akashic generate", kind: "command", typed: true, pause: 300 },
    { text: "Changed files:", kind: "dim", pause: 140 },
    { text: "- services/payments.md", kind: "good", pause: 100 },
    { text: "- services/identity.md", kind: "good", pause: 100 },
    { text: "- flows/checkout.md", kind: "good", pause: 100 },
    { text: "- system/overview.md", kind: "good", pause: 100 },
    { text: "- adr/use-postgres.md", kind: "good", pause: 100 },
    { text: "State written: .akashic/cache/state.json", kind: "accent", pause: 0 },
  ],
}

let playback = 0

const wait = (duration, id) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(id === playback), duration)
  })

const appendCursor = (line) => {
  const cursor = document.createElement("span")
  cursor.className = "terminal-cursor"
  line.append(cursor)
  return cursor
}

const playTerminal = async (slide) => {
  const name = slide.dataset.terminal
  const screen = slide.querySelector(".terminal-screen")
  if (!name || !screen || !terminalScripts[name]) return
  const id = ++playback
  screen.replaceChildren()
  if (!(await wait(900, id))) return
  for (const entry of terminalScripts[name]) {
    if (id !== playback) return
    const line = document.createElement("div")
    line.className = `terminal-line ${entry.kind}`
    screen.append(line)
    const cursor = appendCursor(line)
    if (entry.typed) {
      for (const character of entry.text) {
        if (id !== playback) return
        cursor.before(character)
        if (!(await wait(entry.text.length > 48 ? 12 : 23, id))) return
      }
    } else {
      cursor.before(entry.text)
    }
    screen.scrollTo({ top: screen.scrollHeight, behavior: "smooth" })
    cursor.remove()
    if (!(await wait(entry.pause, id))) return
  }
  const finalLine = screen.lastElementChild
  if (finalLine) appendCursor(finalLine)
}

const renderStaticTerminals = () => {
  document.querySelectorAll("[data-terminal]").forEach((slide) => {
    const name = slide.dataset.terminal
    const screen = slide.querySelector(".terminal-screen")
    if (!name || !screen || !terminalScripts[name]) return
    screen.replaceChildren()
    terminalScripts[name].forEach((entry) => {
      const line = document.createElement("div")
      line.className = `terminal-line ${entry.kind}`
      line.textContent = entry.text
      screen.append(line)
    })
    screen.scrollTop = screen.scrollHeight
  })
}

Reveal.on("ready", (event) => {
  if (window.location.search.includes("print-pdf")) renderStaticTerminals()
  else playTerminal(event.currentSlide)
})

Reveal.on("slidechanged", (event) => playTerminal(event.currentSlide))
window.addEventListener("beforeprint", renderStaticTerminals)

const initializeDeck = async () => {
  await document.fonts.ready
  await Reveal.initialize({
    hash: true,
    history: true,
    controls: false,
    progress: false,
    center: false,
    transition: "none",
    backgroundTransition: "none",
    slideNumber: false,
    width: 1280,
    height: 720,
    margin: 0,
    minScale: 0.2,
    maxScale: 1.8,
    autoAnimateDuration: 0.8,
    autoAnimateEasing: "cubic-bezier(0.22, 1, 0.36, 1)",
  })
}

initializeDeck()
