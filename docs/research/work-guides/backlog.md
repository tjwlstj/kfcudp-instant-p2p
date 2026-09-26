# PR #2 후속 제안 백로그

[원래 조사](../feature-role-optimization.md)의 우선순위 표 밖 제안을 각각 독립 가이드로 분리했다. 모두 **PLANNED**다. 번호는 작업 순서가 아니라 추적 번호이며, 각 가이드의 선행 조건을 먼저 확인한다. 수치·위협·효과 중 서버 또는 실게임에서 확인되지 않은 것은 추정으로 남긴다.

| 번호 | 작업 가이드 |
|---|---|
| B01 | [WebRTC 콜백 대기와 게스트별 factory](b01-callback-isolation.md) |
| B02 | [직결 타임아웃과 세션 내 실패 기억](b02-direct-timeout.md) |
| B03 | [`probeTarget` 중복 연결 제거](b03-target-probe.md) |
| B04 | [탭 목록 갱신 N² 패킷 축소](b04-tab-list-packets.md) |
| B05 | [방 목록 WebSocket 다중화](b05-browser-multiplex.md) |
| B06 | [서버의 `room_update` 캐시](b06-room-update-cache.md) |
| B07 | [클라이언트 `room_update` 재전송 합치기](b07-room-update-coalesce.md) |
| B08 | [전송 계층 `TunnelListener`](b08-tunnel-listener.md) |
| B09 | [`VillasMsg` 파서에 Gson 사용](b09-villas-gson.md) |
| B10 | [`P2PBanManager` 책임 분리](b10-policy-split.md) |
| B11 | [KCP 경로의 제품 결정](b11-kcp-decision.md) |
| B12 | [프로토콜 버전·기능 협상](b12-protocol-capabilities.md) |
| B13 | [공개 방 정보 위조 방지](b13-room-provenance.md) |
| B14 | [공개 방의 릴레이 권장 또는 기본값](b14-public-relay.md) |
| B15 | [ICE 전에 사용자 신원 확인](b15-pre-ice-identity.md) |
| B16 | [연결 진단 화면](b16-connection-diagnostics.md) |
| B17 | [두 번째 TCP 연결을 위한 다중 터널](b17-multi-tunnel.md) |
| B18 | [사용자 지정 시그널링·TURN](b18-custom-signaling-turn.md) |
| B19 | [즐겨찾기·최근 방](b19-favorites.md) |
| B20 | [모드 없는 게스트 접속](b20-modless-guest.md) |
| B21 | [네이티브 DLL 임시 파일 조사](b21-native-temp-files.md) |

[우선순위 작업](README.md)과 공통 검증 규칙을 함께 따른다.
