export default function noise({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const spread = addControl("spread", "Spread", 10, 100, 50);
  const drift = addControl("drift", "Drift Speed", 0, 3, 1);

  const seed = i * 2654435761;
  const rx = ((seed >> 0) & 0xFFFF) / 0xFFFF - 0.5;
  const ry = ((seed >> 4) & 0xFFFF) / 0xFFFF - 0.5;
  const rz = ((seed >> 8) & 0xFFFF) / 0xFFFF - 0.5;

  const dx = Math.sin(time * drift * 0.7 + i * 0.01) * 5;
  const dy = Math.cos(time * drift * 0.5 + i * 0.02) * 5;
  const dz = Math.sin(time * drift * 0.3 + i * 0.015) * 5;

  target.set(
    rx * spread * 2 + dx,
    ry * spread * 2 + dy,
    rz * spread * 2 + dz
  );

  const hue = ((seed >> 12) & 0xFFFF) / 0xFFFF;
  color.setHSL(hue, 0.5, 0.5);

  if (i === 0) setInfo("NO CONSTRAINTS", "Without constraints, information is indistinguishable noise. \u2014 BST Axiom 1");
}
