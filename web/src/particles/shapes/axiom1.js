export default function axiom1({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const order = addControl("order", "Constraint Strength", 0, 1, 0);
  const size = addControl("size", "Scale", 15, 50, 30);

  const seed = i * 2654435761;
  const rx = ((seed >> 0) & 0xFFFF) / 0xFFFF - 0.5;
  const ry = ((seed >> 4) & 0xFFFF) / 0xFFFF - 0.5;
  const rz = ((seed >> 8) & 0xFFFF) / 0xFFFF - 0.5;
  const noiseX = rx * 80;
  const noiseY = ry * 80;
  const noiseZ = rz * 80;

  const phi = Math.acos(-1 + (2 * i) / count);
  const theta = Math.sqrt(count * Math.PI) * phi;
  const sphereX = size * Math.cos(theta) * Math.sin(phi);
  const sphereY = size * Math.sin(theta) * Math.sin(phi);
  const sphereZ = size * Math.cos(phi);

  const t = order;
  target.set(
    noiseX * (1 - t) + sphereX * t,
    noiseY * (1 - t) + sphereY * t,
    noiseZ * (1 - t) + sphereZ * t
  );

  const noiseHue = ((seed >> 12) & 0xFFFF) / 0xFFFF;
  const h = noiseHue * (1 - t) + 0.38 * t;
  const s = 0.5 * (1 - t) + 1.0 * t;
  const l = 0.5 * (1 - t) + 0.55 * t;
  color.setHSL(h, s, l);

  if (i === 0) {
    if (order < 0.3) setInfo("AXIOM 1: NOISE", "No constraints applied. Drag Constraint Strength \u2192");
    else if (order < 0.7) setInfo("AXIOM 1: EMERGING", "Constraints creating distinguishable structure...");
    else setInfo("AXIOM 1: INFORMATION", "\u2200i \u2208 I : \u2203c \u2208 C such that c defines i");
  }
}
