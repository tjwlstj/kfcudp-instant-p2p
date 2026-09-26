# 05 · 시그널링 메시지 발신자와 신뢰 경계 확인

**상태: PLANNED.** 01~04보다 먼저 수정할 필요는 없지만, 서버 의존 변경의 선행 조사다. 현재 저장소에는 `mc-signaling` 서버 소스가 없다.

- **소스 확인:** [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)와 [`WebRtcClient`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)는 수신 JSON에 `servers`가 있으면 ICE 서버 설정으로 사용한다. [`PublicRoomAnnouncer`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java)는 `room_update`가 peer 메시지 중계를 이용한다고 설명한다.
- **추정:** peer가 `servers`·`control.peers`까지 주입할 수 있는지, 서버가 발신자를 구분하는지, peer 이름 문자·길이 제한은 서버 코드와 운영 환경에서 미확인이다. 이것을 실제 취약점으로 단정하지 않는다.
- **제안·최소 변경:** 먼저 서버의 join/broadcast/필터 코드와 메시지 샘플을 확보해 각 키의 발신 주체를 표로 만든다. 그 결과에 따라 `servers`를 서버 최초 메시지에만 허용하거나, 신뢰할 호스트 제한과 동시 세션 상한을 각각 작은 변경으로 적용한다.
- **정적 게이트:** 공격 주장이 실제 서버 분기와 일치하는지, 예외·재연결 때 첫 메시지 판정이 안전한지 확인한다. JSON 필드·서버 호환성을 유지하거나 버전 협상을 설계한다.
- **빌드 게이트:** 클라이언트 수정이 생기면 1.21.x·26.x 대표 빌드와 메시지 계약 시험. 서버 수정은 서버 자체의 별도 테스트가 필요하다.
- **실행 게이트:** 통제된 서버에서 정상 발급·재연결·잘못된 peer 메시지를 시험하고, 유효 ICE 서버를 거부하지 않는지 확인한다. 운영 서버에 공격성 시험을 보내지 않는다.
- **되돌리기:** 발신자 제한·상한을 각기 독립적으로 원복 가능하게 한다. 서버 스키마를 바꾼 경우 양쪽 배포 순서를 문서화한다.
