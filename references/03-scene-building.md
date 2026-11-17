# Building scenes: code, assets, physics, cameras

## Code for structure, real assets for surfaces

Community advice relayed mid-project: "never let the model build a chair from scratch". It held up.

- **Procedural materials plateaued.** Four rounds of node-graph materials scored 66 -> 73 -> 71 -> 72 on realism.
  Scanned PBR textures and HDRIs from Poly Haven and ambientCG moved the needle at once.
- **Code is good at:** layout in real metres, rigs, cameras, timing, physics setup, glue, and specific hero objects
  that no library has.
- **The single most expensive agent ($58)** built a set that included a hand modelled from scratch. The story later
  dropped humans entirely.

## What free libraries actually cover

A scout agent with a shopping list for three builders found 7 usable models in ~6 minutes, all from Poly Haven (CC0):
an overhead crane, scrap filler, a concrete barrier, a roller-shutter door, a duct kit, a wall lamp. Not found
anywhere allowed: a lifting electromagnet, a vault door, server racks, a modern monitor or kiosk, stack lights.
ambientCG had textures but no matching models. Store items marked $0 needed a signed-in account the agent was not
allowed to use, so the scout returned a shortlist for the human instead.

**Plan for hero props to be procedural and dressing to be downloaded.** And decide framing first: the builder skipped
the downloaded crane because its trolley was never in shot.

Scout pattern:
- Run it in parallel with builders. Builders start with proxies behind **one swap function** (`build_kiosk()`,
  `magnet_meshes()`), so a model drops in later without restarting.
- Give it a shopping list grouped by builder, the allowed sources and licences, and a fallback ("if blocked, return a
  shortlist for the human, not a workaround").
- Require per asset: `SOURCE.md` (URL, author, licence, date), real-world size, polycount, and a **test render on the
  actual render machine** (catches missing textures). Gotchas seen: five LODs stacked in one file (import LOD0),
  a graffiti variant with painted text, a hook fused into one mesh with its winch.

**Measure "used in the film", not "downloaded".** A librarian gathered 64 assets; 2 were in the film when the director
asked, because the integrating agents had been stopped for a render. A dedicated integration pass then reached ~87
uses. Pair every gather step with an integrate step and report usage counts by grepping the modules.

## Module structure

- One Python module per owner, each with `build(ctx)`. Shared libraries first (materials, hero prop factory,
  building), then one module per set, then cameras/markers, then a realism pass.
- Each set is an ordered module list saved as its own .blend, rebuildable headless from code at any time.
- Deterministic randomness (`random.Random(seed)`), data API + bmesh, never `bpy.context.object`, modules never touch
  render settings.
- **Keep modules small.** Set modules grew to 3-4.6k lines. 60% of agent code reads were re-reads of a file already
  read, median context per call hit ~180k tokens, and a fixer stopped mid-edit left an undefined material that
  crashed a full build. Split into layout / lighting / animation / materials files with a short outline each.
- **Shared modules need an owner** who receives cross-cutting critic findings, and they must be judged in film
  frames, not their own test scene.

## Physics

- **Simulate anything that falls, tips, spills or collides** (rigid body, Bullet: ~25 substeps, 20 iterations,
  convex hull per link, colliders padded ~10 mm). Then record world matrices per frame, write them as plain keyframes,
  and delete the simulation. Renders never re-simulate, and every build gives identical motion.
- **Lock timing before simulating.** Every retime meant re-timing impacts to music hits; parameterise sim start frames
  from named events.
- **Settled piles jitter.** Parts on a table moved up to 2 mm and 10 degrees per frame after "settling", visible in a
  locked 85 mm shot. Fix as a post-bake pass ("rest hold"): once a body's net motion over the next 8 frames is under
  ~2.5 mm/frame, hold its pose exactly; release only when something moving within contact range hits it faster than
  ~10 mm/frame, then blend over a few frames. Tune it offline by replaying the recorded tracks in numpy. Result:
  0.000 mm/frame on every visible part, intended motion kept.
- **Run an interpenetration check.** After the director spotted clipping, a script (moving objects vs other
  hierarchies, bbox then `BVHTree.overlap`, filtered to the camera frustum) found 115 overlapping pairs in view in one
  set. After the physics pass: 0. Make visible clipping a "major" issue in any rubric.
- **Chaotic landings won't hit your beat.** Report measured landing times and move the sound, not the physics.

## Cameras

- **Match cuts by construction:** export the outgoing camera's last pose and lens as JSON; the next set's camera
  starts there at the same exit velocity. Verify with a 50% overlay of the two frames plus luma stats.
- **Continuity across shots of one take:** build one analytic path and bake it into the separate cameras so each
  starts at the previous one's end pose *and velocity*.
- **Leftover keys cause "random pans".** When fixing, preserve tangents at the boundary key so every later frame stays
  identical (verified frame by frame), and the re-render stays small.
- **A camera replay tool that runs without Blender** (positions and look-at per frame -> image speed, direction
  reversals) makes camera checks nearly free.

## Legibility and motion speed

- **Readable text needs time and slow edges.** Rule of thumb: ~0.5-1 s to take in a new shot plus ~0.3 s per word;
  a short word ≥ 0.5 s, a label ≥ 0.8 s, text edges moving < ~1.5% of frame width per frame. A stamp was readable
  for 0.2 s until a decelerating push made it 11 frames. Measure it with a script, not by eye.
- **Size details in screen pixels at delivery resolution.** A 0.2-degree simulated gate rattle and wires thinner than a
  pixel were invisible work.
- **Motion blur exposes fast moves.** After adding vector blur, an arm whipping at 16 deg/frame became a ghost;
  spreading the move over 16 frames (9.2 deg/frame peak) made it solid. Scan rigs for > ~10 deg/frame before enabling
  blur.
- **Brighter is not more dramatic.** A "modern" set lit 1-1.5 stops brighter read as sterile. Describe looks in
  lighting terms (key/fill ratio, pools of light, falloff) and check frames on both sides of a cut after any global
  lighting change.
- **Generated-scene bugs to check every cut:** a logo going blank after a material change, a hero object edge-on at
  its key cut, labels outside the frame, on-screen text duplicating the subtitle.
