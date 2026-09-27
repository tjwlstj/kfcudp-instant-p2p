# 파일별 검토 범위 — 2026-09-27

기준 커밋 [`c677b47`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/c677b47c0b86b74898765a16b47ae839bcf1e071)의 추적 파일 **123개 전부**를 어떤 방식으로 봤는지 기록한다. "관련"은 [발견 목록](findings.md)의 ID나 [작업 가이드](../../research/work-guides/README.md) 번호다. 이 표에 없는 파일은 이번 검수 대상이 아니다. 이번 검수가 새로 추가한 `docs/review/` 파일도 대상이 아니다.

## 검토 방식

| 방식 | 뜻 |
|---|---|
| 전문 | 파일 전체를 읽었다. Stonecutter 분기가 있으면 양쪽 분기를 모두 읽었다 |
| 활성 분기 전문 + 분기 대조 | 1.21.x 활성 분기를 전부 읽고, 26.x 분기는 [분기 대조](verification.md#4-121x--26x-분기-대조) 결과로 확인했다 |
| 주요 경로 + 분기 대조 + 위험 호출 검색 | 입력·네트워크·저장·입장 경로를 읽고, 나머지 그리기 코드는 스레드·블로킹·파싱 호출을 검색으로 확인했다 |
| 분기 대조 + 위험 호출 검색 | 화면 배치·그리기 위주의 파일이다. 분기 차이와 위험 호출 검색으로 확인했다 |
| 구조·자원 처리 훑기 | UI에서 도달할 수 없는 KCP 전송 구현이다([b11](../../research/work-guides/b11-kcp-decision.md)). 버퍼 해제·예외 경로·스레드만 확인했다 |
| 자동 검사(링크·트리) + 상태 대조 | 저장소 검증 도구의 링크·트리 검사와 작업 가이드 상태 표의 대조로 확인했다 |
| 존재·크기 확인 | 바이너리 리소스다 |

## Java 소스 (53)

| 파일 | 검토 방식 | 관련 |
|---|---|---|
| [`src/client/java/kfc/udp/client/ChatHideSync.java`](../../../src/client/java/kfc/udp/client/ChatHideSync.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/DevBadge.java`](../../../src/client/java/kfc/udp/client/DevBadge.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/KfcudpClient.java`](../../../src/client/java/kfc/udp/client/KfcudpClient.java) | 활성 분기 전문 + 분기 대조 | R03 R04 R25 |
| [`src/client/java/kfc/udp/client/gui/BlockedPlayersScreen.java`](../../../src/client/java/kfc/udp/client/gui/BlockedPlayersScreen.java) | 주요 경로 + 분기 대조 + 위험 호출 검색 | — |
| [`src/client/java/kfc/udp/client/gui/ChannelScreen.java`](../../../src/client/java/kfc/udp/client/gui/ChannelScreen.java) | 분기 대조 + 위험 호출 검색 | — |
| [`src/client/java/kfc/udp/client/gui/ChzzkLinkScreen.java`](../../../src/client/java/kfc/udp/client/gui/ChzzkLinkScreen.java) | 주요 경로 + 분기 대조 + 위험 호출 검색 | R02 |
| [`src/client/java/kfc/udp/client/gui/ConfirmPopup.java`](../../../src/client/java/kfc/udp/client/gui/ConfirmPopup.java) | 분기 대조 + 위험 호출 검색 | — |
| [`src/client/java/kfc/udp/client/gui/CustomRoomScreen.java`](../../../src/client/java/kfc/udp/client/gui/CustomRoomScreen.java) | 주요 경로 + 분기 대조 + 위험 호출 검색 | — |
| [`src/client/java/kfc/udp/client/gui/RoomListScreen.java`](../../../src/client/java/kfc/udp/client/gui/RoomListScreen.java) | 주요 경로 + 분기 대조 + 위험 호출 검색 | R10 R11 |
| [`src/client/java/kfc/udp/client/gui/SafetyWarningScreen.java`](../../../src/client/java/kfc/udp/client/gui/SafetyWarningScreen.java) | 분기 대조 + 위험 호출 검색 | — |
| [`src/client/java/kfc/udp/client/kcp/KcpAddressRegistry.java`](../../../src/client/java/kfc/udp/client/kcp/KcpAddressRegistry.java) | 전문 | R24 |
| [`src/client/java/kfc/udp/client/kcp/KcpChannel.java`](../../../src/client/java/kfc/udp/client/kcp/KcpChannel.java) | 구조·자원 처리 훑기 | — |
| [`src/client/java/kfc/udp/client/kcp/KcpCore.java`](../../../src/client/java/kfc/udp/client/kcp/KcpCore.java) | 구조·자원 처리 훑기 | — |
| [`src/client/java/kfc/udp/client/kcp/KcpException.java`](../../../src/client/java/kfc/udp/client/kcp/KcpException.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/kcp/KcpExceptionHandler.java`](../../../src/client/java/kfc/udp/client/kcp/KcpExceptionHandler.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/kcp/KcpOutput.java`](../../../src/client/java/kfc/udp/client/kcp/KcpOutput.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/ClientConnectionMixin.java`](../../../src/client/java/kfc/udp/client/mixin/ClientConnectionMixin.java) | 전문 | R24 |
| [`src/client/java/kfc/udp/client/mixin/CommandNodeAccessor.java`](../../../src/client/java/kfc/udp/client/mixin/CommandNodeAccessor.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/ConnectScreenMixin.java`](../../../src/client/java/kfc/udp/client/mixin/ConnectScreenMixin.java) | 전문 | 04a |
| [`src/client/java/kfc/udp/client/mixin/DevBadgeMixin.java`](../../../src/client/java/kfc/udp/client/mixin/DevBadgeMixin.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/DevNameMixin.java`](../../../src/client/java/kfc/udp/client/mixin/DevNameMixin.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/IntegratedServerAccessor.java`](../../../src/client/java/kfc/udp/client/mixin/IntegratedServerAccessor.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/IntegratedServerMaxPlayersMixin.java`](../../../src/client/java/kfc/udp/client/mixin/IntegratedServerMaxPlayersMixin.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/IntegratedServerStopMixin.java`](../../../src/client/java/kfc/udp/client/mixin/IntegratedServerStopMixin.java) | 전문 | 04c |
| [`src/client/java/kfc/udp/client/mixin/PlayerJoinMessageMixin.java`](../../../src/client/java/kfc/udp/client/mixin/PlayerJoinMessageMixin.java) | 전문 | R16 |
| [`src/client/java/kfc/udp/client/mixin/PlayerManagerAccessor.java`](../../../src/client/java/kfc/udp/client/mixin/PlayerManagerAccessor.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/PlayerManagerMixin.java`](../../../src/client/java/kfc/udp/client/mixin/PlayerManagerMixin.java) | 전문 | R20 |
| [`src/client/java/kfc/udp/client/mixin/ServerAddressMixin.java`](../../../src/client/java/kfc/udp/client/mixin/ServerAddressMixin.java) | 전문 | R09 |
| [`src/client/java/kfc/udp/client/mixin/ServerDisconnectStopMixin.java`](../../../src/client/java/kfc/udp/client/mixin/ServerDisconnectStopMixin.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/mixin/SocialHideMixin.java`](../../../src/client/java/kfc/udp/client/mixin/SocialHideMixin.java) | 전문 | R21 |
| [`src/client/java/kfc/udp/client/webrtc/BatchPipe.java`](../../../src/client/java/kfc/udp/client/webrtc/BatchPipe.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/ChannelRules.java`](../../../src/client/java/kfc/udp/client/webrtc/ChannelRules.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/ChzzkLink.java`](../../../src/client/java/kfc/udp/client/webrtc/ChzzkLink.java) | 전문 | R02 |
| [`src/client/java/kfc/udp/client/webrtc/ExpelManager.java`](../../../src/client/java/kfc/udp/client/webrtc/ExpelManager.java) | 전문 | R07 R08 |
| [`src/client/java/kfc/udp/client/webrtc/IceConfig.java`](../../../src/client/java/kfc/udp/client/webrtc/IceConfig.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/InviteCodes.java`](../../../src/client/java/kfc/udp/client/webrtc/InviteCodes.java) | 전문 | R11 |
| [`src/client/java/kfc/udp/client/webrtc/LocalGuestListener.java`](../../../src/client/java/kfc/udp/client/webrtc/LocalGuestListener.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/P2PBanManager.java`](../../../src/client/java/kfc/udp/client/webrtc/P2PBanManager.java) | 전문 | R12 R14 R15 R17 R22 |
| [`src/client/java/kfc/udp/client/webrtc/P2PConfig.java`](../../../src/client/java/kfc/udp/client/webrtc/P2PConfig.java) | 전문 | R12 R25 |
| [`src/client/java/kfc/udp/client/webrtc/P2PNet.java`](../../../src/client/java/kfc/udp/client/webrtc/P2PNet.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/P2PWhitelistManager.java`](../../../src/client/java/kfc/udp/client/webrtc/P2PWhitelistManager.java) | 전문 | R12 R13 |
| [`src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java) | 전문 | R01 |
| [`src/client/java/kfc/udp/client/webrtc/Roles.java`](../../../src/client/java/kfc/udp/client/webrtc/Roles.java) | 전문 | R20 |
| [`src/client/java/kfc/udp/client/webrtc/RoomMembersProbe.java`](../../../src/client/java/kfc/udp/client/webrtc/RoomMembersProbe.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/RoomRoles.java`](../../../src/client/java/kfc/udp/client/webrtc/RoomRoles.java) | 전문 | R05 |
| [`src/client/java/kfc/udp/client/webrtc/SignalingRtt.java`](../../../src/client/java/kfc/udp/client/webrtc/SignalingRtt.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/VillasMsg.java`](../../../src/client/java/kfc/udp/client/webrtc/VillasMsg.java) | 전문 | R01 R06 |
| [`src/client/java/kfc/udp/client/webrtc/WebRtcBridge.java`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcBridge.java) | 전문 | R11 |
| [`src/client/java/kfc/udp/client/webrtc/WebRtcClient.java`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java) | 전문 | R03 04a |
| [`src/client/java/kfc/udp/client/webrtc/WebRtcHost.java`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java) | 전문 | R03 05 |
| [`src/client/java/kfc/udp/client/webrtc/WebRtcStats.java`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcStats.java) | 전문 | — |
| [`src/client/java/kfc/udp/client/webrtc/WebSocketClient.java`](../../../src/client/java/kfc/udp/client/webrtc/WebSocketClient.java) | 전문 | — |

## 리소스 (9)

| 파일 | 검토 방식 | 관련 |
|---|---|---|
| [`src/client/resources/instant-p2p.client.mixins.json`](../../../src/client/resources/instant-p2p.client.mixins.json) | 전문 + 클래스 존재 대조 | — |
| [`src/main/resources/assets/instant-p2p/icon.png`](../../../src/main/resources/assets/instant-p2p/icon.png) | 존재·크기 확인 | — |
| [`src/main/resources/assets/instant-p2p/lang/en_us.json`](../../../src/main/resources/assets/instant-p2p/lang/en_us.json) | 키·자리표시자 대조 | — |
| [`src/main/resources/assets/instant-p2p/lang/ko_kr.json`](../../../src/main/resources/assets/instant-p2p/lang/ko_kr.json) | 키·자리표시자 대조 | — |
| [`src/main/resources/assets/instant-p2p/textures/gui/sprites/chzzk.png`](../../../src/main/resources/assets/instant-p2p/textures/gui/sprites/chzzk.png) | 존재·크기 확인 | — |
| [`src/main/resources/assets/instant-p2p/textures/gui/sprites/cime.png`](../../../src/main/resources/assets/instant-p2p/textures/gui/sprites/cime.png) | 존재·크기 확인 | — |
| [`src/main/resources/assets/instant-p2p/textures/gui/sprites/twitch.png`](../../../src/main/resources/assets/instant-p2p/textures/gui/sprites/twitch.png) | 존재·크기 확인 | — |
| [`src/main/resources/assets/instant-p2p/textures/gui/sprites/youtube.png`](../../../src/main/resources/assets/instant-p2p/textures/gui/sprites/youtube.png) | 존재·크기 확인 | — |
| [`src/main/resources/fabric.mod.json`](../../../src/main/resources/fabric.mod.json) | 전문 + 생성 JAR 대조 | R23 |

## 빌드·CI·저장소 설정 (15)

| 파일 | 검토 방식 | 관련 |
|---|---|---|
| [`.gitattributes`](../../../.gitattributes) | 전문 | — |
| [`.github/workflows/build.yml`](../../../.github/workflows/build.yml) | 전문 | R18 |
| [`.github/workflows/verify-repository.yml`](../../../.github/workflows/verify-repository.yml) | 전문 | — |
| [`.gitignore`](../../../.gitignore) | 전문 | — |
| [`LICENSE`](../../../LICENSE) | 머리 확인(CC0-1.0) | — |
| [`build-26x.gradle.kts`](../../../build-26x.gradle.kts) | 전문 | R18 |
| [`build.gradle.kts`](../../../build.gradle.kts) | 전문 | R18 |
| [`gradle.properties`](../../../gradle.properties) | 전문 | R18 |
| [`gradle/wrapper/gradle-wrapper.jar`](../../../gradle/wrapper/gradle-wrapper.jar) | CI 래퍼 검증 | — |
| [`gradle/wrapper/gradle-wrapper.properties`](../../../gradle/wrapper/gradle-wrapper.properties) | CI 래퍼 검증 | — |
| [`gradlew`](../../../gradlew) | 표준 래퍼 | — |
| [`gradlew.bat`](../../../gradlew.bat) | 표준 래퍼 | — |
| [`settings.gradle.kts`](../../../settings.gradle.kts) | 전문 | — |
| [`stonecutter.gradle.kts`](../../../stonecutter.gradle.kts) | 전문 | — |
| [`stonecutter.properties.toml`](../../../stonecutter.properties.toml) | 자동 계약 검사 + 표본 | — |

## 검증 도구 (6)

| 파일 | 검토 방식 | 관련 |
|---|---|---|
| [`tools/tests/java/kfc/udp/client/webrtc/ContractCheck.java`](../../../tools/tests/java/kfc/udp/client/webrtc/ContractCheck.java) | 전문 + 실행 | R27 |
| [`tools/tests/java/kfc/udp/client/webrtc/LocalSecurityCheck.java`](../../../tools/tests/java/kfc/udp/client/webrtc/LocalSecurityCheck.java) | 전문 + 실행 | — |
| [`tools/verify/check_links.py`](../../../tools/verify/check_links.py) | 범위 확인 + 실행 | R19 |
| [`tools/verify/check_project_contract.py`](../../../tools/verify/check_project_contract.py) | 범위 확인 + 실행 | — |
| [`tools/verify/check_tree.py`](../../../tools/verify/check_tree.py) | 범위 확인 + 실행 | — |
| [`tools/verify/run_contracts.py`](../../../tools/verify/run_contracts.py) | 전문 + 실행 | — |

## 문서·AI 스킬 (40)

| 파일 | 검토 방식 | 관련 |
|---|---|---|
| [`.agents/skills/instant-p2p-maintainer/SKILL.md`](../../../.agents/skills/instant-p2p-maintainer/SKILL.md) | 전문 | — |
| [`.claude/skills/instant-p2p-maintainer/SKILL.md`](../../../.claude/skills/instant-p2p-maintainer/SKILL.md) | 전문 | — |
| [`README.md`](../../../README.md) | 전문(상태 표) | R26 |
| [`docs/research/code-tree.md`](../../../docs/research/code-tree.md) | 전문(트리) + 자동 검사 | — |
| [`docs/research/compatibility-and-modpack.md`](../../../docs/research/compatibility-and-modpack.md) | 제목·결론 + 자동 검사 | — |
| [`docs/research/feature-role-optimization.md`](../../../docs/research/feature-role-optimization.md) | 줄 링크 대조 + 자동 검사 | R19 |
| [`docs/research/verification-tools.md`](../../../docs/research/verification-tools.md) | 전문 | R26 |
| [`docs/research/work-guides/01-guest-loopback.md`](../../../docs/research/work-guides/01-guest-loopback.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/02-secure-invite-code.md`](../../../docs/research/work-guides/02-secure-invite-code.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/03-login-role-refresh.md`](../../../docs/research/work-guides/03-login-role-refresh.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/04a-guest-signaling.md`](../../../docs/research/work-guides/04a-guest-signaling.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/04b-host-native-load.md`](../../../docs/research/work-guides/04b-host-native-load.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/04c-world-shutdown.md`](../../../docs/research/work-guides/04c-world-shutdown.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/05-signaling-provenance.md`](../../../docs/research/work-guides/05-signaling-provenance.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/06-adaptive-send-buffer.md`](../../../docs/research/work-guides/06-adaptive-send-buffer.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/07-ice-restart.md`](../../../docs/research/work-guides/07-ice-restart.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/08-version-adapter.md`](../../../docs/research/work-guides/08-version-adapter.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/README.md`](../../../docs/research/work-guides/README.md) | 전문 | R26 |
| [`docs/research/work-guides/b01-callback-isolation.md`](../../../docs/research/work-guides/b01-callback-isolation.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b02-direct-timeout.md`](../../../docs/research/work-guides/b02-direct-timeout.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b03-target-probe.md`](../../../docs/research/work-guides/b03-target-probe.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b04-tab-list-packets.md`](../../../docs/research/work-guides/b04-tab-list-packets.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b05-browser-multiplex.md`](../../../docs/research/work-guides/b05-browser-multiplex.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b06-room-update-cache.md`](../../../docs/research/work-guides/b06-room-update-cache.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b07-room-update-coalesce.md`](../../../docs/research/work-guides/b07-room-update-coalesce.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b08-tunnel-listener.md`](../../../docs/research/work-guides/b08-tunnel-listener.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b09-villas-gson.md`](../../../docs/research/work-guides/b09-villas-gson.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b10-policy-split.md`](../../../docs/research/work-guides/b10-policy-split.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b11-kcp-decision.md`](../../../docs/research/work-guides/b11-kcp-decision.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b12-protocol-capabilities.md`](../../../docs/research/work-guides/b12-protocol-capabilities.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b13-room-provenance.md`](../../../docs/research/work-guides/b13-room-provenance.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b14-public-relay.md`](../../../docs/research/work-guides/b14-public-relay.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b15-pre-ice-identity.md`](../../../docs/research/work-guides/b15-pre-ice-identity.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b16-connection-diagnostics.md`](../../../docs/research/work-guides/b16-connection-diagnostics.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b17-multi-tunnel.md`](../../../docs/research/work-guides/b17-multi-tunnel.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b18-custom-signaling-turn.md`](../../../docs/research/work-guides/b18-custom-signaling-turn.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b19-favorites.md`](../../../docs/research/work-guides/b19-favorites.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b20-modless-guest.md`](../../../docs/research/work-guides/b20-modless-guest.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/b21-native-temp-files.md`](../../../docs/research/work-guides/b21-native-temp-files.md) | 자동 검사(링크·트리) + 상태 대조 | — |
| [`docs/research/work-guides/backlog.md`](../../../docs/research/work-guides/backlog.md) | 자동 검사(링크·트리) + 상태 대조 | — |
