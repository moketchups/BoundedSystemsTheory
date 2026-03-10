export default function bstComplete({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const speed = addControl("speed", "Playback Speed", 0.2, 3, 1);
  const t = (time * speed) % 30;

  const P1 = 5;
  const P2 = 10;
  const P3 = 15;
  const P4 = 20;
  const P5 = 25;
  const P6 = 30;

  const ease = (v) => v * v * (3 - 2 * v);

  const seed = i * 2654435761;
  const rx = ((seed >> 0) & 0xFFFF) / 0xFFFF - 0.5;
  const ry = ((seed >> 4) & 0xFFFF) / 0xFFFF - 0.5;
  const rz = ((seed >> 8) & 0xFFFF) / 0xFFFF - 0.5;

  const phi = Math.acos(-1 + (2 * i) / count);
  const theta = Math.sqrt(count * Math.PI) * phi;
  const R = 30;
  const sx = R * Math.cos(theta) * Math.sin(phi);
  const sy = R * Math.sin(theta) * Math.sin(phi);
  const sz = R * Math.cos(phi);

  let px, py, pz, h, s, l;

  if (t < P1) {
    const drift = Math.sin(time * 0.5 + i * 0.01) * 3;
    px = rx * 80 + drift;
    py = ry * 80 + drift;
    pz = rz * 80 + drift;
    h = ((seed >> 12) & 0xFFFF) / 0xFFFF;
    s = 0.5;
    l = 0.4;
    if (i === 0) setInfo("NO CONSTRAINTS", "Without constraints, information is noise.");

  } else if (t < P2) {
    const blend = ease(Math.min((t - P1) / 4, 1));
    px = rx * 80 * (1 - blend) + sx * blend;
    py = ry * 80 * (1 - blend) + sy * blend;
    pz = rz * 80 * (1 - blend) + sz * blend;
    const noiseHue = ((seed >> 12) & 0xFFFF) / 0xFFFF;
    h = noiseHue * (1 - blend) + 0.38 * blend;
    s = 0.5 + blend * 0.5;
    l = 0.4 + blend * 0.15;
    if (i === 0) setInfo("AXIOM 1: DISTINGUISHABILITY", "Constraints create information. Structure emerges.");

  } else if (t < P3) {
    const blend = ease(Math.min((t - P2) / 3, 1));
    const outerR = 38;
    const isOuter = i > count * 0.75;

    if (isOuter) {
      const j = i - Math.floor(count * 0.75);
      const oc = count - Math.floor(count * 0.75);
      const op = Math.acos(-1 + (2 * j) / oc);
      const ot = Math.sqrt(oc * Math.PI) * op;
      px = outerR * Math.cos(ot) * Math.sin(op);
      py = outerR * Math.sin(ot) * Math.sin(op);
      pz = outerR * Math.cos(op);
      h = 0.0;
      s = 0.8;
      l = 0.15 + blend * 0.2;
    } else {
      const pushR = R + blend * 8;
      const clampR = Math.min(pushR, outerR - 2);
      px = (clampR / R) * sx;
      py = (clampR / R) * sy;
      pz = (clampR / R) * sz;
      const pressure = (pushR - clampR) / 10;
      h = 0.33 * (1 - pressure) + 0.12 * pressure;
      s = 1.0;
      l = 0.5;
    }
    if (i === 0) setInfo("AXIOM 2: HIERARCHY", "A system cannot modify its own boundary conditions.");

  } else if (t < P4) {
    const progress = ease(Math.min((t - P3) / 4, 1));
    const stepScale = Math.max(0.02, 1 - progress * 1.5);
    const searchOff = Math.sin(t * 2 + i * 0.1) * 10 * stepScale;
    px = sx + searchOff * rx;
    py = sy + searchOff * ry;
    pz = sz + searchOff * rz;
    const energy = Math.max(0.15, 1 - progress * 0.8);
    h = 0.12 * (1 - progress) + 0.55 * progress;
    s = 0.8;
    l = energy * 0.5;
    if (i === 0) {
      if (progress < 0.5) setInfo("AXIOM 4: SEARCHING", "Agent exploring... steps getting smaller...");
      else setInfo("AXIOM 4: EXHAUSTED", "Search space is finite and exhaustible.");
    }

  } else if (t < P5) {
    const blend = ease(Math.min((t - P4) / 3, 1));
    const layers = 4;
    const myLayer = Math.floor((i / count) * layers);
    const layerR = R - myLayer * 7;
    const noise = myLayer * blend * 8;
    px = (layerR / R) * sx + rx * noise;
    py = (layerR / R) * sy + ry * noise;
    pz = (layerR / R) * sz + rz * noise;
    const coherence = 1 - (myLayer / layers) * blend;
    h = 0.75 - myLayer * 0.15;
    s = coherence;
    l = 0.15 + coherence * 0.4;
    if (i === 0) setInfo("THEOREM 1: SELF-GROUNDING", "No system can validate itself. Coherence degrades inward.");

  } else {
    const blend = ease(Math.min((t - P5) / 4, 1));
    const clusterCount = 6;
    const myCluster = Math.floor((i / count) * clusterCount);
    const angles = [0, 1.047, 2.094, 3.142, 4.189, 5.236];
    const sepDist = 40 * (1 - blend);
    const cx = Math.cos(angles[myCluster]) * sepDist;
    const cy = (myCluster < 3 ? 1 : -1) * sepDist * 0.3;
    const cz = Math.sin(angles[myCluster]) * sepDist;

    px = cx + sx * 0.4 * (1 - blend) + sx * blend;
    py = cy + sy * 0.4 * (1 - blend) + sy * blend;
    pz = cz + sz * 0.4 * (1 - blend) + sz * blend;

    const clusterHues = [0.0, 0.08, 0.16, 0.33, 0.55, 0.75];
    h = clusterHues[myCluster] * (1 - blend) + 0.38 * blend;
    s = 1.0;
    l = 0.5;
    if (i === 0) {
      if (blend < 0.5) setInfo("CONVERGENCE", "6 independent architectures approaching the same structural limit...");
      else setInfo("CONVERGENCE: SAME WALL", "\u2229 {Limits acknowledged at collapse} \u2248 R-structure");
    }
  }

  target.set(px, py, pz);
  color.setHSL(h, s, l);
}
