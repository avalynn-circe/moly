# Roadmap

In order.

1. **Readable Errors 0.1 on Agensi.** The pack in this repository, as a paid skill. Creator mode on, payouts connected, listing submitted from `agensi.yml`.
2. **Mechanical extractors.** Python and TypeScript first: find string literals in raise, throw, error-level log calls, and tool return paths, and emit units with file, line, and a guessed reader. This makes gate mode run in a workflow with no agent. Go and Rust after.
3. **Gate workflow template.** A reusable GitHub Actions workflow: extract, scan, upload SARIF. Readable Errors as a check on every pull request, the way Vale is on circe-docs.
4. **Tell.** Second pack. Units are sentences and paragraphs of the user's own draft. Rules name the tells (the negate-then-elevate, the trailing contrast, the tricolon with a twist, the hollow intensifier) and explain why each reads as machine-made. Plain voice; the explanation is the product. Several rules begin as ports of the Circe Vale style with explanations added. Written to run on the user's own text; the pack says so in its listing and its voice.
5. **Tía Jo.** Third pack. Units are sentences that carry a number. Rules name the shapes of bad math that are detectable from the sentence alone: a relative change with no base, "up to", a missing denominator, a correlation verb carrying a causal claim. Every finding ends with the figure the reader would need to check the claim. First pack with a persona voice, which is why the voice layer exists before it does.
6. **Judged rules in gate mode.** Once a pack has run in review mode on enough codebases to know which judged `block` rules hold, the pack's next major version lets a workflow with a model fail on them.
7. **Engine as a service.** Not yet. The engine is a library and a CLI until two packs are live and someone asks.
