# B11 · KCP 경로의 제품 결정

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`kcp/`](../../../src/client/java/kfc/udp/client/kcp/)와 [`ClientConnectionMixin`](../../../src/client/java/kfc/udp/client/mixin/ClientConnectionMixin.java)는 `kcp.` 주소 입력 경로를 가진다. 조사된 UI에는 KCP 방 열기가 없다.
- **선행·최소 변경:** 실제 사용·유지비·호환성 기준을 조사하고, 먼저 기능 플래그로 격리할지 제거할지 결정 기록을 남긴다.
- **검증·되돌리기:** 플래그 경로와 일반 WebRTC 주소에 영향이 없는지 정적 검토·빌드·실게임 확인한다. 제거는 별도 릴리스 단계에서 하며 첫 단계는 플래그 원복이 가능해야 한다.
