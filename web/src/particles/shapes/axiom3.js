export default function axiom3({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const trace = addControl("trace", "Trace Depth", 0, 1, 0);
  const pulse = addControl("pulse", "Pulse Speed", 0, 3, 1);

  const coreCount = Math.floor(count * 0.08);
  const branchCount = count - coreCount;

  if (i < coreCount) {
    const phi = Math.acos(-1 + (2 * i) / coreCount);
    const theta = Math.sqrt(coreCount * Math.PI) * phi;
    const coreR = 5;
    target.set(
      coreR * Math.cos(theta) * Math.sin(phi),
      coreR * Math.sin(theta) * Math.sin(phi),
      coreR * Math.cos(phi)
    );
    color.setHSL(0.12, 1.0, 0.7);
  } else {
    const j = i - coreCount;
    const phi = Math.acos(-1 + (2 * j) / branchCount);
    const theta = Math.sqrt(branchCount * Math.PI) * phi;
    const outerR = 35;

    const ox = outerR * Math.cos(theta) * Math.sin(phi);
    const oy = outerR * Math.sin(theta) * Math.sin(phi);
    const oz = outerR * Math.cos(phi);

    const pullStrength = trace;
    const px = ox * (1 - pullStrength * 0.6);
    const py = oy * (1 - pullStrength * 0.6);
    const pz = oz * (1 - pullStrength * 0.6);

    const dist = Math.sqrt(px * px + py * py + pz * pz);
    const wave = Math.sin(dist * 0.3 - time * pulse * 2) * 0.5 + 0.5;

    target.set(px, py, pz);

    const seed = i * 2654435761;
    const randHue = ((seed >> 12) & 0xFFFF) / 0xFFFF;
    const h = randHue * (1 - trace) + 0.55 * trace;
    const brightness = 0.25 * (1 - trace) + (0.35 + wave * 0.3) * trace;
    color.setHSL(h, 0.5 + trace * 0.5, brightness);
  }

  if (i === 0) {
    if (trace < 0.3) setInfo("AXIOM 3: OUTPUTS", "Outputs appear independent. But are they? Drag Trace Depth.");
    else if (trace < 0.7) setInfo("AXIOM 3: TRACING", "Every output derives from base structure...");
    else setInfo("AXIOM 3: COMPLETENESS", "No output exists in isolation. All derivations trace to foundation.");
    annotate("core", new THREE.Vector3(0, 0, 0), "BASE STRUCTURE");
    annotate("output", new THREE.Vector3(38, 0, 0), "OUTPUT");
  }
}
