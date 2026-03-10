export default function axiom2({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const push = addControl("push", "Agent Force", 0, 5, 1);
  const breathe = addControl("breathe", "Oscillation", 0, 2, 0.5);

  const innerCount = Math.floor(count * 0.7);
  const outerCount = count - innerCount;
  const outerR = 35;
  const innerR = 20;

  if (i < innerCount) {
    const phi = Math.acos(-1 + (2 * i) / innerCount);
    const theta = Math.sqrt(innerCount * Math.PI) * phi;

    const expandR = innerR + push * 5 + Math.sin(time * breathe + i * 0.01) * 3;
    const clampedR = Math.min(expandR, outerR - 1.5);

    target.set(
      clampedR * Math.cos(theta) * Math.sin(phi),
      clampedR * Math.sin(theta) * Math.sin(phi),
      clampedR * Math.cos(phi)
    );

    const pressure = (expandR - clampedR) / (expandR - outerR + 2);
    const hue = 0.33 * (1 - Math.min(pressure * 3, 1)) + 0.0 * Math.min(pressure * 3, 1);
    color.setHSL(hue, 1.0, 0.5 + pressure * 0.2);
  } else {
    const j = i - innerCount;
    const phi = Math.acos(-1 + (2 * j) / outerCount);
    const theta = Math.sqrt(outerCount * Math.PI) * phi;

    target.set(
      outerR * Math.cos(theta) * Math.sin(phi),
      outerR * Math.sin(theta) * Math.sin(phi),
      outerR * Math.cos(phi)
    );

    const glow = push > 2 ? 0.3 + Math.sin(time * 4) * 0.15 : 0.3;
    color.setHSL(0.0, 0.8, glow);
  }

  if (i === 0) {
    setInfo("AXIOM 2: HIERARCHY", "A system cannot modify its own boundary conditions. Crank Agent Force \u2192");
    annotate("boundary", new THREE.Vector3(outerR + 3, 0, 0), "CEILING");
    annotate("agent", new THREE.Vector3(0, 0, 0), "AGENT");
  }
}
