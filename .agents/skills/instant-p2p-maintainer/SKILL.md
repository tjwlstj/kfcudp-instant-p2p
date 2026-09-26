---
name: instant-p2p-maintainer
description: Maintain or refactor this Instant P2P Fabric fork across Stonecutter Minecraft versions, room discovery, WebRTC transport, and admission rules. Use for source or build changes in this repository.
---

# Instant P2P maintenance

Read [the code tree](../../../docs/research/code-tree.md) when deciding where a change belongs. Check the current checkout and affected source before relying on that snapshot; the tree is an index, not a substitute for code inspection.

## Choose a boundary

- Keep Minecraft/Fabric API adapters, UI, signaling JSON, game payloads, WebRTC/TCP transport, and admission policy distinguishable. Prefer a small extraction with existing public entrypoints delegating to it when callers span many files.
- Stonecutter generates 1.21.x and 26.x builds from shared files. Preserve `//? if` branches and the exact `fabric.mod.json` dependencies. A successful build for one version does not establish that another version works.
- `VillasMsg` and `P2PNet` are separate wire contracts. Preserve room IDs, peer-name prefixes, JSON field names, delta replacement behavior, and payload IDs unless both ends and compatibility handling are in scope. The signaling server source is outside this repository.
- Public-room visibility and actual admission are separate. The ban hashes used for the room list are not the server-side `checkCanJoin` decision. Keep host-side authority when reorganizing policy code.
- Preserve direct-to-TURN retry, queued ICE candidates, early Minecraft bytes, backpressure, and close/cancel ownership when changing `WebRtcHost`, `WebRtcClient`, or `WebRtcBridge`.

## Verify the affected change

Build the affected Stonecutter targets with the repository wrapper. For shared code, include a 1.21.x target and a 26.x target when those toolchains are available; use the full 17-target matrix for release-level claims. Check the produced mod metadata when dependency or version handling changes. A compilation result does not prove that Mixins apply or a P2P room works in Minecraft; state the runtime gap when it remains.

For a protocol or modpack integration change, identify the host and guest versions and test the connection, restart, and rejoin paths before claiming compatibility. AutoModpack v4 synchronization begins after a compatible game and P2P client are already running; it cannot bootstrap the first Minecraft/P2P installation.

Update the code tree when moving responsibilities. Label source observations, local build results, runtime observations, and proposed designs separately. Do not publish local paths, credentials, or unverified claims about the live signaling/TURN service.
