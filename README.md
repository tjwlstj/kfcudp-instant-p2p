# Instant P2P — 연구용 포크

이 저장소는 [KITE2459의 Instant P2P](https://github.com/KITE2459/kfcudp-instant-p2p)를 분석하고 구조 분리와 호환성 아이디어를 실험하는 **비공식 연구용 포크**로만 유지한다. 이 첫 화면은 코드의 위치와 연구 범위를 안내한다. 모드 사용 안내와 원 제작자의 설명은 [원본 저장소](https://github.com/KITE2459/kfcudp-instant-p2p)를 참고한다.

## 코드 트리

현재 Java 소스는 **51개**다. `ChannelRules.java`를 분리하기 전 기준은 50개였으며, Stonecutter 빌드 대상은 **17개 Minecraft 버전**이다. 아래 트리는 실제 소스 파일의 위치를 보여 준다. 파일의 책임과 호출 관계는 [상세 코드 트리·분리 지도](docs/research/code-tree.md)에 기록했다.

```text
.
├─ .github/workflows/build.yml             버전별 CI 빌드
├─ build.gradle.kts                         1.21.x 빌드
├─ build-26x.gradle.kts                     26.x 빌드
├─ settings.gradle.kts                      Stonecutter 대상 버전
├─ stonecutter.gradle.kts                   JAR 수집
├─ stonecutter.properties.toml             공통 버전·대상별 의존성
├─ gradle.properties                        Loader·빌드 설정
├─ .agents/skills/instant-p2p-maintainer/   프로젝트 AI 스킬
│  └─ SKILL.md
├─ docs/research/                           연구 기록
│  ├─ code-tree.md
│  └─ compatibility-and-modpack.md
└─ src/
   ├─ main/resources/
   │  ├─ fabric.mod.json                    모드 진입점·의존성
   │  └─ assets/instant-p2p/                아이콘·언어·GUI 리소스
   └─ client/
      ├─ resources/instant-p2p.client.mixins.json
      └─ java/kfc/udp/client/
         ├─ KfcudpClient.java               클라이언트 진입점·방 생명주기
         ├─ ChatHideSync.java
         ├─ DevBadge.java
         ├─ gui/                             화면 7개
         │  ├─ BlockedPlayersScreen.java
         │  ├─ ChannelScreen.java
         │  ├─ ChzzkLinkScreen.java
         │  ├─ ConfirmPopup.java
         │  ├─ CustomRoomScreen.java
         │  ├─ RoomListScreen.java
         │  └─ SafetyWarningScreen.java
         ├─ mixin/                           Minecraft 접점 14개
         │  ├─ ClientConnectionMixin.java
         │  ├─ CommandNodeAccessor.java
         │  ├─ ConnectScreenMixin.java
         │  ├─ DevBadgeMixin.java
         │  ├─ DevNameMixin.java
         │  ├─ IntegratedServerAccessor.java
         │  ├─ IntegratedServerMaxPlayersMixin.java
         │  ├─ IntegratedServerStopMixin.java
         │  ├─ PlayerJoinMessageMixin.java
         │  ├─ PlayerManagerAccessor.java
         │  ├─ PlayerManagerMixin.java
         │  ├─ ServerAddressMixin.java
         │  ├─ ServerDisconnectStopMixin.java
         │  └─ SocialHideMixin.java
         ├─ webrtc/                          방 발견·전송·정책 21개
         │  ├─ BatchPipe.java
         │  ├─ ChannelRules.java
         │  ├─ ChzzkLink.java
         │  ├─ ExpelManager.java
         │  ├─ IceConfig.java
         │  ├─ P2PBanManager.java
         │  ├─ P2PConfig.java
         │  ├─ P2PNet.java
         │  ├─ P2PWhitelistManager.java
         │  ├─ PublicRoomAnnouncer.java
         │  ├─ PublicRoomBrowser.java
         │  ├─ Roles.java
         │  ├─ RoomMembersProbe.java
         │  ├─ RoomRoles.java
         │  ├─ SignalingRtt.java
         │  ├─ VillasMsg.java
         │  ├─ WebRtcBridge.java
         │  ├─ WebRtcClient.java
         │  ├─ WebRtcHost.java
         │  ├─ WebRtcStats.java
         │  └─ WebSocketClient.java
         └─ kcp/                             별도 KCP 접속 경로 6개
            ├─ KcpAddressRegistry.java
            ├─ KcpChannel.java
            ├─ KcpCore.java
            ├─ KcpException.java
            ├─ KcpExceptionHandler.java
            └─ KcpOutput.java
```

## 소스에서 읽은 연결 흐름

```text
방 생성: KfcudpClient → WebRtcBridge → WebRtcHost → 통합 서버 TCP
방 입장: RoomListScreen → PublicRoomBrowser / RoomMembersProbe
         → ConnectScreenMixin → WebRtcClient
시그널링: VillasMsg(JSON) ↔ WebSocketClient ↔ 외부 시그널링 서버
게임 패킷: P2PNet(Fabric payload) ↔ 호스트 입장 정책·방 상태
```

시그널링·TURN 서버 구현은 이 저장소 밖에 있다. 위 흐름은 소스 구조를 요약한 것으로 실제 연결 시험 결과는 아니다.

## 연구 및 분리 현황

| 상태 | 내용 |
|---|---|
| **분리 완료** | 채널 파싱·조합·방 표시 규칙을 `P2PConfig`에서 `ChannelRules`로 추출하고 기존 공개 호출 경로를 유지했다. |
| **계획** | 방 목록 표시 상태, 방 생명주기, WebRTC 세션·터널, 입장 정책의 경계를 단계별로 검토한다. |
| **로컬 빌드 확인** | 위 코드 분리 후 `:1.21:build`와 `:26.2:build`가 성공했다. |
| **미검증** | 전체 17개 대상 빌드와 실제 Minecraft 호스트·게스트 연결. |

- [코드 트리·분리 지도](docs/research/code-tree.md): 전체 파일 역할, 의존 관계, 분리 후보와 유지할 계약
- [호환성·모드팩 공유 조사](docs/research/compatibility-and-modpack.md): 확인한 사실과 아직 제안 단계인 아이디어
- [필요 기능·역할·최적화 조사](docs/research/feature-role-optimization.md): 게임 스레드 대기, 데이터 경로, 신뢰 경계, 추가 기능 후보와 우선순위
- [프로젝트 AI 스킬](.agents/skills/instant-p2p-maintainer/SKILL.md): 이 포크에서 코드 변경을 검토할 때의 경계와 검증 기준

연구 문서와 실험 결과는 원 제작자의 공식 기능 설명이 아니다.
