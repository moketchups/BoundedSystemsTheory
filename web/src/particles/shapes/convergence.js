export default function convergence({ i, count, target, color, THREE, time, setInfo, annotate, addControl }) {
  const probe = addControl("probe", "Probe Depth", 0, 1, 0);
  const spread = addControl("spread", "Initial Spread", 20, 80, 50);

  const clusterCount = 6;
  const perCluster = Math.floor(count / clusterCount);
  const myCluster = Math.min(Math.floor(i / perCluster), clusterCount - 1);
  const j = i - myCluster * perCluster;

  const clusterAngles = [0, 1.047, 2.094, 3.142, 4.189, 5.236];
  const startX = Math.cos(clusterAngles[myCluster]) * spread;
  const startY = (myCluster < 3 ? 1 : -1) * spread * 0.4;
  const startZ = Math.sin(clusterAngles[myCluster]) * spread;

  const miniR = 10;
  const phi = Math.acos(-1 + (2 * j) / perCluster);
  const theta = Math.sqrt(perCluster * Math.PI) * phi;
  const localX = miniR * Math.cos(theta) * Math.sin(phi);
  const localY = miniR * Math.sin(theta) * Math.sin(phi);
  const localZ = miniR * Math.cos(phi);

  const finalR = 25;
  const finalPhi = Math.acos(-1 + (2 * i) / count);
  const finalTheta = Math.sqrt(count * Math.PI) * finalPhi;
  const finalX = finalR * Math.cos(finalTheta) * Math.sin(finalPhi);
  const finalY = finalR * Math.sin(finalTheta) * Math.sin(finalPhi);
  const finalZ = finalR * Math.cos(finalPhi);

  const t = probe;
  target.set(
    (startX + localX) * (1 - t) + finalX * t,
    (startY + localY) * (1 - t) + finalY * t,
    (startZ + localZ) * (1 - t) + finalZ * t
  );

  const clusterHues = [0.0, 0.08, 0.16, 0.33, 0.55, 0.75];
  const hue = clusterHues[myCluster] * (1 - t) + 0.38 * t;
  color.setHSL(hue, 1.0, 0.5);

  if (i === 0) {
    const names = ["GPT-4", "Claude", "Gemini", "DeepSeek", "Grok", "Mistral"];
    if (probe < 0.3) setInfo("CONVERGENCE: INDEPENDENT", "6 architectures. Different training data. Different alignment. Drag Probe Depth \u2192");
    else if (probe < 0.7) setInfo("CONVERGENCE: MERGING", "Probing self-referential limits... clusters approaching...");
    else setInfo("CONVERGENCE: SAME WALL", "\u2229 {Structural limits acknowledged by S at collapse} \u2248 R-structure");

    for (let k = 0; k < 6; k++) {
      const ax = Math.cos(clusterAngles[k]) * spread * (1 - t);
      const ay = (k < 3 ? 1 : -1) * spread * 0.4 * (1 - t);
      const az = Math.sin(clusterAngles[k]) * spread * (1 - t);
      annotate("m" + k, new THREE.Vector3(ax, ay, az), names[k]);
    }
  }
}
