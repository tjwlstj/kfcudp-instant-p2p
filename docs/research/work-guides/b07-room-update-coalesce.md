# B07 · 클라이언트 `room_update` 재전송 합치기

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** 같은 [`PublicRoomAnnouncer`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java)가 새 입장자마다 업데이트를 전송한다.
- **선행·최소 변경:** B06의 서버 배포를 기다리지 않고 0~1초 지연 창 안의 입장 이벤트를 한 번으로 합친다. 지연값은 UX 기준선을 측정한 뒤 정한다.
- **검증·되돌리기:** coalescing timer의 close/cancel을 정적 검토하고 빌드한다. 여러 관전자의 동시 입장, 늦게 들어온 관전자, 방 닫기에서 목록 완전성과 메시지 수를 실행 측정한다. 지연이 허용 불가하면 즉시 전송으로 원복한다.

## 코드 소유 경계
