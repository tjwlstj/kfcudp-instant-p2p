# 07 · 순단 뒤 ICE 재시작

**상태: PLANNED.** [프로토콜 버전·기능 협상](b12-protocol-capabilities.md)을 먼저 설계하고 양쪽 모드 변경을 준비한다.

- **소스 확인:** [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)와 [`WebRtcClient`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)는 `DISCONNECTED`를 기다리고 `FAILED`에서 닫는다. 페어 WebSocket은 연결 후 유지된다. 게스트의 끊긴 시그널링을 다시 붙이는 경로는 현재 제한적이다.
- **추정:** ICE 재시작만으로 모든 네트워크 전환에서 기존 SCTP/DataChannel을 유지할 수 있는지는 사용 중인 webrtc-java와 실제 네트워크에서 미검증이다. 30초는 Minecraft 연결 제한을 고려한 목표다.
- **제안·최소 변경:** 먼저 시그널링 재연결과 새 offer/answer를 구분할 기능 비트를 정의한다. 실험 브랜치에서 단일 피어의 `DISCONNECTED`→재접속→ICE restart 상태만 추가하고 기존 실패 종료를 타임아웃 대안으로 유지한다.
- **정적 게이트:** 양쪽 offer 충돌, 중복 ICE candidate, 오래된 세션 메시지, 강퇴·월드 종료와 복구 경쟁을 상태도로 검토한다. 원본 모드와 섞일 때는 재시작을 시도하지 않는다.
- **빌드 게이트:** 양쪽 1.21.x·26.x 대표 빌드와 세션 상태 전이 계약 시험; 릴리스 전 전체 매트릭스.
- **실행 게이트:** 양쪽 새 모드에서 Wi-Fi 전환·짧은 끊김·시그널링 단절을 재현하고 Minecraft 로그인 세션 유지와 30초 내 복구를 확인한다. 원본↔새 모드 조합은 기존 연결 실패 처리로 안전하게 돌아가야 한다.
- **되돌리기:** 기능 비트와 재시작 타이머를 꺼서 기존 close/reconnect 동작으로 돌아간다. 메시지 스키마를 배포했다면 구버전 처리 경로를 남긴다.
