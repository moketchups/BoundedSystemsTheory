export default function axiom4({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const iterations = addControl("iter", "Search Iterations", 0, 50, 0);
  const landscape = addControl("terrain", "Landscape Scale", 10, 40, 25);

  const agentCount = Math.floor(count * 0.05);
  const terrainCount = count - agentCount;

  if (i >= agentCount) {
    const j = i - agentCount;
    const gridSize = Math.ceil(Math.sqrt(terrainCount));
    const gx = (j % gridSize) / gridSize - 0.5;
    const gz = Math.floor(j / gridSize) / gridSize - 0.5;
    const x = gx * landscape * 3;
    const z = gz * landscape * 3;
    const y = Math.sin(x * 0.3) * 5 + Math.cos(z * 0.4) * 4 + Math.sin(x * 0.15 + z * 0.15) * 8 - 10;

    target.set(x, y, z);

    const norm = (y + 20) / 25;
    color.setHSL(0.55 + norm * 0.15, 0.4, 0.2 + norm * 0.15);
  } else {
    const progress = Math.min(iterations / 50, 1);

    const pathSeed = i * 7919;
    const startX = (((pathSeed >> 0) & 0xFF) / 255 - 0.5) * landscape * 2;
    const startZ = (((pathSeed >> 8) & 0xFF) / 255 - 0.5) * landscape * 2;

    const stepScale = Math.max(0.01, 1 - progress * 1.5);
    const searchX = startX + Math.sin(iterations * 0.5 + i) * landscape * stepScale;
    const searchZ = startZ + Math.cos(iterations * 0.7 + i * 1.3) * landscape * stepScale;
    const searchY = Math.sin(searchX * 0.3) * 5 + Math.cos(searchZ * 0.4) * 4 + Math.sin(searchX * 0.15 + searchZ * 0.15) * 8 - 10;

    target.set(searchX, searchY + 2, searchZ);

    const energy = Math.max(0.15, 1 - progress);
    color.setHSL(0.12 * (1 - progress), 1.0, energy);
  }

  if (i === 0) {
    if (iterations < 10) setInfo("AXIOM 4: SEARCHING", "Agent exploring the optimization landscape...");
    else if (iterations < 30) setInfo("AXIOM 4: DIMINISHING", "Steps getting smaller. Revisiting old positions...");
    else setInfo("AXIOM 4: EXHAUSTED", "Search space is finite and exhaustible. \u00AC\u2203 infinite chain.");
    annotate("optimum", new THREE.Vector3(0, -15, 0), "GLOBAL MINIMUM");
  }
}
