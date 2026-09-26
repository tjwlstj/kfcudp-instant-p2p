# Instant P2P 코드 트리와 분리 지도

이 문서는 포크의 코드를 찾고 작은 단위로 분리하기 위한 지도다. 기준은 포크 커밋 `684508b`의 **Java 50개·15,961행** 인벤토리이며, 이번 첫 분리로 추가한 `ChannelRules`는 아래 현재 트리에 포함했다. 줄 수는 빈 줄·주석과 Stonecutter 조건 분기를 포함한다. 이 트리는 소스 구조의 설명이며 Minecraft에서의 동작 검증 결과가 아니다.

## 물리적 파일 트리

```text
.
├─ .github/workflows/build.yml             17개 Minecraft 대상의 CI 빌드
├─ build.gradle.kts                         1.21.x Yarn/remap/Java 21
├─ build-26x.gradle.kts                     26.x Mojang 매핑/no-remap/Java 25
├─ settings.gradle.kts                      Stonecutter 버전 노드
├─ stonecutter.gradle.kts                   빌드·JAR 수집 태스크
├─ stonecutter.properties.toml             공통 모드 버전·대상별 의존성
├─ gradle.properties                        Loader·빌드 설정
├─ gradle/wrapper/                           Gradle wrapper
├─ .agents/skills/instant-p2p-maintainer/   이 포크의 AI 유지보수 스킬
│  └─ SKILL.md
└─ src/
   ├─ main/resources/
   │  ├─ fabric.mod.json                    진입점·대상별 필수 의존성
   │  └─ assets/instant-p2p/
   │     ├─ icon.png
   │     ├─ lang/{ko_kr,en_us}.json         화면·메시지 번역
   │     └─ textures/gui/sprites/
   │        ├─ chzzk.png
   │        ├─ cime.png
   │        ├─ twitch.png
   │        └─ youtube.png
   └─ client/
      ├─ resources/instant-p2p.client.mixins.json
      └─ java/kfc/udp/client/
         ├─ KfcudpClient.java               Fabric 진입점·방 생명주기·이벤트 등록
         ├─ ChatHideSync.java               채팅 숨김 동기화
         ├─ DevBadge.java                   역할/배지 표시
         ├─ gui/                             게임 화면 7개
         │  ├─ BlockedPlayersScreen.java    차단·온라인 목록
         │  ├─ ChannelScreen.java           채널 설정
         │  ├─ ChzzkLinkScreen.java         치지직 연동
         │  ├─ ConfirmPopup.java            방 목록 내 확인 팝업
         │  ├─ CustomRoomScreen.java        방 생성·설정
         │  ├─ RoomListScreen.java          목록·필터·입장
         │  └─ SafetyWarningScreen.java     연결 전 안내
         ├─ kcp/                             WebRTC 초대방과 별도인 KCP 접속 경로 6개
         │  ├─ KcpAddressRegistry.java
         │  ├─ KcpChannel.java
         │  ├─ KcpCore.java
         │  ├─ KcpException.java
         │  ├─ KcpExceptionHandler.java
         │  └─ KcpOutput.java
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
         └─ webrtc/                          연결·정책·공개 방 20개 + 첫 추출 1개
            ├─ BatchPipe.java              DataChannel → TCP 배칭·배압
            ├─ ChannelRules.java           채널 파싱·조합·공개 방 표시 규칙 [추출]
            ├─ ChzzkLink.java              외부 계정 연동
            ├─ ExpelManager.java           추방·강퇴
            ├─ IceConfig.java              ICE 후보·TURN 정책
            ├─ P2PBanManager.java          차단 저장·입장 판정·명령어·터널 IP
            ├─ P2PConfig.java              주소·버전·사용자 설정·로비 ID
            ├─ P2PNet.java                 게임 내 Fabric 페이로드
            ├─ P2PWhitelistManager.java    화이트리스트
            ├─ PublicRoomAnnouncer.java    공개 방 공지
            ├─ PublicRoomBrowser.java      공개 방 구독·목록 데이터
            ├─ Roles.java                  서명된 역할 조회
            ├─ RoomMembersProbe.java       입장 전 방 참가자 조회
            ├─ RoomRoles.java              방 역할·상태
            ├─ SignalingRtt.java           시그널링 왕복 시간
            ├─ VillasMsg.java              시그널링 JSON 형식
            ├─ WebRtcBridge.java           호스트·게스트·공지 생명주기
            ├─ WebRtcClient.java           게스트 RTC·로컬 TCP 터널
            ├─ WebRtcHost.java             호스트 RTC·통합 서버 TCP 터널
            ├─ WebRtcStats.java            직결/중계 진단
            └─ WebSocketClient.java        시그널링 WebSocket 전송
```

## 실행·의존 관계

```mermaid
flowchart TD
    Entry["fabric.mod.json → KfcudpClient"] --> Host["방 생성·수정·종료"]
    Entry --> List["RoomListScreen"]
    Host --> Bridge["WebRtcBridge"]
    Bridge --> RTC["WebRtcHost / WebRtcClient"]
    Bridge --> Announce["PublicRoomAnnouncer"]
    List --> Browser["PublicRoomBrowser"]
    List --> Probe["RoomMembersProbe"]
    List --> Join["joinRoomByCode → ConnectScreenMixin"]
    Join --> Bridge
    RTC --> Signal["WebSocketClient + VillasMsg"]
    RTC --> Pipe["IceConfig + BatchPipe + WebRtcStats"]
    Announce --> Signal
    Browser --> Signal
    Host --> Policy["P2PBanManager / Whitelist / Expel / Roles"]
    Policy --> GameWire["P2PNet: Fabric payload"]
    Host --> Config["P2PConfig → ChannelRules"]
    Config --> Announce
    Config --> Browser
    Entry --> KCP["ConnectScreenMixin → kcp/"]
```

`VillasMsg`는 **시그널링 서버와 교환하는 JSON**, `P2PNet`은 **게임 내부 Fabric 페이로드**다. 공개 방 목록의 차단 해시 필터와 실제 호스트의 `P2PBanManager.checkCanJoin`도 역할이 다르다. `kcp/`는 Netty에 의존하지만 일반 WebRTC 초대방의 터널은 아니다. 시그널링/TURN 서버 구현은 이 저장소 밖에 있다.

## 분리 현황과 다음 경계

아래는 **제안하는 책임 트리**다. 실제 패키지 이름이나 모듈 경계로 확정된 것은 `ChannelRules`뿐이며, 나머지는 기존 파일을 어느 방향으로 나눌지 가리키는 작업 단위다. 버전별 Java 소스를 복제하기 전에 공통 규칙과 Minecraft API 접점을 분리한다.

```text
Instant P2P
├─ 진입·Minecraft 연동       KfcudpClient, mixin/, P2PNet
├─ 화면·입력                gui/
│  └─ 목록 표시 상태        RoomListScreen에서 분리 후보
├─ 방 설정·발견
│  ├─ 채널 규칙              ChannelRules [완료]
│  ├─ 설정 저장·로비 ID      P2PConfig에서 분리 후보
│  └─ 공개 방 공지·조회      PublicRoomAnnouncer / PublicRoomBrowser / RoomMembersProbe
├─ 시그널링·전송
│  ├─ JSON 계약·WebSocket   VillasMsg / WebSocketClient / SignalingRtt
│  ├─ 세션 생명주기          WebRtcBridge / WebRtcHost / WebRtcClient
│  └─ 데이터·ICE 진단       BatchPipe / IceConfig / WebRtcStats
├─ 입장 정책·역할           P2PBanManager / P2PWhitelistManager / ExpelManager / Roles / RoomRoles
└─ 별도 KCP 경로            kcp/
```

각 작업 단위는 공개 API, 저장 형식, 상대 피어와 주고받는 형식을 먼저 확인한 뒤 이동한다. 특히 방 목록 표시 상태를 분리해도 호스트 입장 판정의 소유자는 바뀌지 않는다.

| 상태 | 경계 | 이유와 유지할 계약 |
|---|---|---|
| **EXTRACTED** | `P2PConfig` → `ChannelRules` | 순수 채널 파싱·AND/OR 판정을 별도 클래스로 옮기고 기존 공개 API는 위임해 호출자를 유지한다. |
| **PLANNED** | `P2PConfig`의 설정 저장과 공개 로비 ID 계산 | 설정 파일 갱신은 하나의 소유자로 두고, 로비 ID의 모드 버전 해시·채널 해시·샤드 계산은 기존 경로와 바이트 단위로 같아야 한다. |
| **PLANNED** | `RoomListScreen`의 표시 목록 상태 | 목록 스냅샷·정렬·삭제 유예를 화면 렌더와 분리한다. 현재 1.5초 유예와 `hideOtherVersions` 동작을 보존한다. |
| **PLANNED** | `KfcudpClient`의 방 생명주기와 Minecraft API 어댑터 | 1.21.x/26.x 분기가 많은 진입점이다. 이벤트 등록 순서와 방 종료·재접속 경로를 먼저 고정한다. |
| **PLANNED** | `WebRtcHost`·`WebRtcClient`의 시그널링 세션과 데이터 터널 | 조기 Minecraft 바이트, 대기 ICE, 직결→TURN 재시도, 배압 및 종료 소유권을 보존한다. |
| **PLANNED** | `P2PBanManager`의 저장·실제 입장 판정·명령어 | 하나의 차단 데이터 원천을 유지하고 서버 입장 판정을 화면 필터로 대체하지 않는다. |

기준 인벤토리에서 가장 큰 파일은 `KfcudpClient` 1,897행, `RoomListScreen` 1,568행, `P2PBanManager` 1,027행, `CustomRoomScreen` 982행, `BlockedPlayersScreen` 930행이다. Java 파일 30개에는 Stonecutter 조건 분기가 있고, 분기 지점 282곳 중 다섯 파일에 약 57%가 모여 있다. 이 수치는 분리 우선순위를 고르는 참고값이며 변경 후 최신 값은 다시 측정해야 한다.

`WebRtcBridge → PublicRoomAnnouncer → P2PBanManager → WebRtcBridge`와 `WebSocketClient ↔ SignalingRtt`의 호출 순환이 있다. 파일을 더 나눌 때 이 순환을 새 패키지 간 양방향 의존으로 그대로 옮기지 말고 이벤트·좁은 인터페이스 경계를 검토한다. 공개 로비 ID, `VillasMsg`의 필드명·delta 처리, Fabric payload ID는 외부/버전 간 계약이므로 겉으로 보이는 구조 변경을 별도로 검증해야 한다.

## 검증 경계

[`settings.gradle.kts`](../../settings.gradle.kts)와 [CI 매트릭스](../../.github/workflows/build.yml)는 17개 대상 목록을 각각 가진다. 새 Minecraft 버전을 추가할 때 둘을 함께 갱신한다. 공통 Java 코드의 분리에서는 적어도 1.21.x와 26.x의 대표 빌드를 확인하고, 배포 수준의 호환성 주장은 전체 빌드와 실제 호스트·게스트 실행 근거를 따로 요구한다. 저장소에는 테스트 소스와 Minecraft 런타임 연결 검증이 없다.

이번 `ChannelRules` 추출에서는 로컬 `:1.21:build`와 `:26.2:build`가 성공했다. 1.21 빌드에는 기존 `CommandNodeAccessor` 매핑 경고가 있었고, 26.2 빌드에는 deprecated API·Gradle 기능 경고가 있었다. 이 결과는 두 대표 대상의 빌드 확인이며 전체 17개 대상이나 실제 P2P 연결 검증을 뜻하지 않는다.
