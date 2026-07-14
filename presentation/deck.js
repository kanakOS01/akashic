const terminalScripts = {
  init: [
    { text: "mkdir system-memory && cd system-memory", kind: "command", typed: true, pause: 300 },
    { text: "akashic init", kind: "command", typed: true, pause: 380 },
    { text: "created   .akashic/config.yaml", kind: "good", pause: 170 },
    { text: "created   services/ flows/ system/ entities/", kind: "good", pause: 170 },
    { text: "created   adr/ glossary/ README.md", kind: "good", pause: 170 },
    { text: "initialized Git repository", kind: "info", pause: 200 },
    { text: "committed  Initialize knowledge repository", kind: "good", pause: 240 },
    { text: "ready      attach a source repository", kind: "accent", pause: 0 },
  ],
  generate: [
    { text: "akashic attach ../payments", kind: "command", typed: true, pause: 240 },
    { text: "attached   payments   /repos/payments", kind: "good", pause: 220 },
    { text: "akashic generate", kind: "command", typed: true, pause: 360 },
    { text: "context    3 repositories", kind: "dim", pause: 180 },
    { text: "prompt     5 document templates composed", kind: "dim", pause: 180 },
    { text: "session    interactive authoring started", kind: "info", pause: 300 },
    { text: "written    services/payments.md", kind: "good", pause: 120 },
    { text: "written    flows/checkout.md", kind: "good", pause: 120 },
    { text: "written    system/overview.md", kind: "good", pause: 180 },
    { text: "summary    14 knowledge files changed", kind: "accent", pause: 0 },
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
