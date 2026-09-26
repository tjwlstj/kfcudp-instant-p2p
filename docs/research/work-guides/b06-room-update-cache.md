# B06 · 서버의 `room_update` 캐시

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인·추정:** [`PublicRoomAnnouncer`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java)는 관전자 입장 delta에 방 정보를 다시 보낸다. R×(R+V−1) 전달량은 계산값이며 실제 서버 부하는 미측정이다.
- **선행·최소 변경:** 서버 구현을 확인하고 `r` peer별 마지막 업데이트를 새 입장자에게만 보내는 서버 변경을 설계한다.
- **검증·되돌리기:** 캐시 소유자·퇴장·만료를 정적 검토하고 서버 시험을 실행한다. 다수 공개 방 부하와 새 관전자 목록의 완전성을 측정한다. 이전 브로드캐스트 경로를 릴리스 전환 동안 유지한다.
