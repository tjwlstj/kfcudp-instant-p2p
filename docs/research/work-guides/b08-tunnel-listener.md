# B08 · 전송 계층 `TunnelListener`

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)·[`WebRtcClient`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)는 UI 알림과 정책 호출 때문에 Minecraft 타입을 직접 안다.
- **선행·최소 변경:** 연결·실패·연결 종류 알림 하나만 콜백으로 추출하고 기존 엔트리포인트가 위임하게 한다.
- **검증·되돌리기:** 콜백 스레드와 실패 순서를 정적 검토하고 빌드·실게임 접속/강퇴/닫기를 확인한다. 사건이 누락되면 위임 호출만 원복한다.
