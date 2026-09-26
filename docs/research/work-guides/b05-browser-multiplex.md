# B05 · 방 목록 WebSocket 다중화

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`PublicRoomBrowser`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java)는 채널×샤드당 WebSocket 하나를 사용한다. 한 연결에서 여러 로비를 구독하는 기능은 서버 계약이 필요하다.
- **선행·최소 변경:** 서버 소스와 부하 기준선을 확보한 뒤 구독 메시지 스키마를 버전 협상과 함께 설계한다.
- **검증·되돌리기:** 서버·클라이언트 스키마 시험과 빌드, 1~20 로비 구독·재접속·권한 분리 실행을 확인한다. 구버전에는 기존 WS 방식을 유지한다.
