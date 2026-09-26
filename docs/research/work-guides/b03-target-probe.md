# B03 · `probeTarget` 중복 연결 제거

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)는 조인 전에 빈 TCP probe를 열고, 실제 연결 실패는 `dialTarget`에서도 처리한다.
- **선행·최소 변경:** 두 실패가 사용자에게 같은 의미인지 확인한 뒤 probe 호출만 제거한다.
- **검증·되돌리기:** 실패 전파와 로컬 서버 준비 순서를 정적 검토하고 빌드한다. 정상 조인, 닫힌 포트, 월드 종료 경합을 실게임에서 확인한다. 진단 가치가 있었다면 probe를 되살린다.
