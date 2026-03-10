export default function theorem1({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const depth = addControl("depth", "Recursion Depth", 1, 5, 3);
  const decay = addControl("decay", "Coherence Decay", 0, 1, 0.5);

  const layers = Math.floor(depth);
  const perLayer = Math.floor(count / layers);
  const myLayer = Math.min(Math.floor(i / perLayer), layers - 1);
  const j = i - myLayer * perLayer;
  const layerCount = perLayer;

  const baseR = 35 - myLayer * 7;
  const phi = Math.acos(-1 + (2 * j) / layerCount);
  const theta = Math.sqrt(layerCount * Math.PI) * phi;

  const noiseLevel = myLayer * decay * 8;
  const seed = i * 2654435761;
  const nx = ((seed >> 0) & 0xFFF) / 0xFFF - 0.5;
  const ny = ((seed >> 4) & 0xFFF) / 0xFFF - 0.5;
  const nz = ((seed >> 8) & 0xFFF) / 0xFFF - 0.5;

  target.set(
    baseR * Math.cos(theta) * Math.sin(phi) + nx * noiseLevel,
    baseR * Math.sin(theta) * Math.sin(phi) + ny * noiseLevel,
    baseR * Math.cos(phi) + nz * noiseLevel
  );

  const coherence = 1 - (myLayer / layers) * decay;
  const hue = 0.75 - myLayer * 0.15;
  color.setHSL(hue, coherence, 0.2 + coherence * 0.4);

  if (i === 0) {
    setInfo("THEOREM 1: SELF-GROUNDING LIMIT", "Each layer attempts to verify the one inside it. Coherence degrades.");
    annotate("v1", new THREE.Vector3(38, 0, 0), "V\u2081 verify");
    if (layers >= 2) annotate("v2", new THREE.Vector3(28, 0, 0), "V\u2082 verify");
    if (layers >= 3) annotate("v3", new THREE.Vector3(21, 0, 0), "V\u2083 noise");
  }
}
