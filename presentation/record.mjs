import { execFileSync, spawn } from "node:child_process"
import { existsSync } from "node:fs"
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises"
import { createServer } from "node:http"
import { tmpdir } from "node:os"
import { basename, dirname, extname, join, relative, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { chromium } from "playwright-core"

const width = 1280
const height = 720
const slideDurations = [4000, 4000, 4000, 2500, 6500, 4000, 7000, 4000, 4000, 4000, 4000, 4000, 4000, 5000]
const fragmentDuration = 1200
const presentation = dirname(fileURLToPath(import.meta.url))
const output = resolve(presentation, process.argv[2] ?? "Akashic_Reveal_Preview.mp4")
const contentTypes = new Map([
  [".css", "text/css"],
  [".html", "text/html"],
  [".js", "text/javascript"],
  [".ttf", "font/ttf"],
])

const findCommand = (command) => {
  try {
    return execFileSync("which", [command], { encoding: "utf8" }).trim()
  } catch {
    return undefined
  }
}

const chromeCandidates = [
  process.env.CHROME_PATH,
  findCommand("google-chrome"),
  findCommand("chromium"),
  findCommand("chromium-browser"),
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
].filter((candidate) => candidate && existsSync(candidate))
const chrome = chromeCandidates[0]
const ffmpeg = process.env.FFMPEG_PATH ?? findCommand("ffmpeg")

if (!chrome) throw new Error("Chrome or Chromium was not found. Set CHROME_PATH to its executable.")
if (!ffmpeg) throw new Error("ffmpeg was not found. Install it or set FFMPEG_PATH to its executable.")

const temporary = await mkdtemp(join(tmpdir(), "akashic-presentation-"))
const frames = join(temporary, "frames")
await mkdir(frames)
await mkdir(dirname(output), { recursive: true })

const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url ?? "/", "http://127.0.0.1")
    const pathname = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname)
    const filePath = resolve(presentation, `.${pathname}`)
    if (relative(presentation, filePath).startsWith("..")) throw new Error("Not found")
    const contents = await readFile(filePath)
    response.writeHead(200, { "Content-Type": contentTypes.get(extname(filePath)) ?? "application/octet-stream" })
    response.end(contents)
  } catch {
    response.writeHead(404)
    response.end("Not found")
  }
})

await new Promise((resolveListening) => server.listen(0, "127.0.0.1", resolveListening))
const address = server.address()
if (!address || typeof address === "string") throw new Error("The presentation server did not start.")

const browser = await chromium.launch({ executablePath: chrome, headless: true })

try {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 })
  await page.goto(`http://127.0.0.1:${address.port}`, { waitUntil: "networkidle" })
  await page.waitForFunction(() => Reflect.get(globalThis, "Reveal")?.isReady())
  const slideCount = await page.locator(".slides > section").count()
  const durations = []
  for (let index = 0; index < slideCount; index += 1) {
    durations.push(slideDurations[index] ?? 4000)
    const fragments = await page.locator(`.slides > section:nth-child(${index + 1}) .fragment`).count()
    durations.push(...Array.from({ length: fragments }, () => fragmentDuration))
  }
  const captureDuration = durations.reduce((total, duration) => total + duration, 0) / 1000
  const session = await page.context().newCDPSession(page)
  const captured = []
  const writes = []

  session.on("Page.screencastFrame", (event) => {
    const path = join(frames, `${String(captured.length).padStart(6, "0")}.jpg`)
    captured.push({ path, timestamp: event.metadata.timestamp ?? performance.now() / 1000 })
    writes.push(writeFile(path, event.data, "base64"))
    void session.send("Page.screencastFrameAck", { sessionId: event.sessionId })
  })

  await session.send("Page.startScreencast", {
    format: "jpeg",
    quality: 92,
    maxWidth: width,
    maxHeight: height,
    everyNthFrame: 1,
  })

  for (const [index, duration] of durations.entries()) {
    await page.waitForTimeout(duration)
    if (index < durations.length - 1) await page.evaluate(() => Reflect.get(globalThis, "Reveal").next())
  }

  await session.send("Page.stopScreencast")
  await Promise.all(writes)
  if (captured.length < 2) throw new Error(`Chrome captured only ${captured.length} frame(s).`)

  const timing = captured
    .map((frame, index) => {
      const next = captured[index + 1]
      const elapsed = frame.timestamp - captured[0].timestamp
      const duration = next
        ? Math.max(0.001, next.timestamp - frame.timestamp)
        : Math.max(0.04, captureDuration - elapsed)
      return `file '${frame.path.replaceAll("'", "'\\''")}'\nduration ${duration.toFixed(6)}`
    })
    .join("\n")
  const manifest = join(temporary, "frames.txt")
  await writeFile(manifest, `${timing}\nfile '${captured.at(-1).path.replaceAll("'", "'\\''")}'\n`)

  const encoder = spawn(
    ffmpeg,
    [
      "-y",
      "-f",
      "concat",
      "-safe",
      "0",
      "-i",
      manifest,
      "-vf",
      `fps=25,scale=${width}:${height}:flags=lanczos:in_range=full:out_range=tv,format=yuv420p`,
      "-c:v",
      "libx264",
      "-preset",
      "medium",
      "-crf",
      "21",
      "-movflags",
      "+faststart",
      output,
    ],
    { stdio: "inherit" },
  )
  const exitCode = await new Promise((resolveExit, rejectExit) => {
    encoder.on("error", rejectExit)
    encoder.on("close", resolveExit)
  })
  if (exitCode !== 0) throw new Error(`ffmpeg exited with status ${exitCode}.`)
  console.log(`Recorded ${captured.length} frames to ${basename(output)}`)
} finally {
  await browser.close()
  await new Promise((resolveClosing) => server.close(resolveClosing))
  await rm(temporary, { recursive: true, force: true })
}
