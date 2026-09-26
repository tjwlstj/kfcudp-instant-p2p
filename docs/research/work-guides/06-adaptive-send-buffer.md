# 06 · 송신 버퍼 상한을 전송 속도에 맞추기

**상태: PLANNED.** 먼저 기준선 계측을 끝낸다. 한쪽부터 적용할 수 있으며 현재 페이로드 형식은 보존한다.

- **소스 확인:** [`WebRtcClient`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)와 [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)의 DataChannel 송신은 `bufferedAmount`를 감시하며 현재 상한은 1MiB다. 터널은 로그인 뒤 암호화된 Minecraft 바이트를 보내므로 패킷 종류별 우선순위를 알 수 없다.
- **계산·추정:** 1MiB 대기 시간은 실효 10Mbps에서 약 0.8초, 2Mbps에서 약 4.2초다. 실제 청크 로딩·TURN 경로의 keepalive 지연은 측정되지 않았다.
- **제안·최소 변경:** `onBufferedAmountChange` 간격의 배출량을 계측해 먼저 로그만 남긴다. 이후 목표 큐 지연 100~200ms에 맞춰 상한을 계산하되 64KiB~1MiB로 제한하고, 갑작스런 추정치 변동을 완화한다.
- **정적 게이트:** 음수·0 배출량, 이벤트 누락, 재연결, overflow, sender 깨우기, 기존 backpressure·close 소유권을 검토한다. 페이로드 ID와 순서는 바꾸지 않는다.
- **빌드 게이트:** 1.21.x·26.x 대표 빌드. 계산을 순수 클래스로 분리해 상한·속도·경계값 계약 시험을 둔다.
- **실행 게이트:** 직결과 TURN에서 청크 로딩 동안 RTT·keepalive·처리량·버퍼·중단 횟수를 변경 전후 비교한다. 느린 링크에서 단순히 처리량을 희생한 효과인지 확인한다.
- **되돌리기:** 고정 1MiB 상한으로 즉시 돌아갈 수 있게 정책을 한 지점에 둔다.
