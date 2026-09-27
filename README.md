# Instant P2P — 연구용 포크

이 저장소는 [KITE2459의 Instant P2P](https://github.com/KITE2459/kfcudp-instant-p2p)를 분석하고 구조 분리와 호환성 아이디어를 실험하는 **비공식 연구용 포크**로만 유지한다. 이 첫 화면은 코드의 위치와 연구 범위를 안내한다. 모드 사용 안내와 원 제작자의 설명은 [원본 저장소](https://github.com/KITE2459/kfcudp-instant-p2p)를 참고한다.

> **검수 기록:** 커밋을 고정해 포크 전체를 점검한 결과는 [`docs/review/`](docs/review/README.md)에 날짜별로 남긴다. 최근 검수는 [2026-09-27 전수 검수](docs/review/2026-09-27/README.md)다.

## 코드 트리

현재 Java 소스는 **53개**다. `ChannelRules.java`를 분리하기 전 기준은 50개였으며, Stonecutter 빌드 대상은 **17개 Minecraft 버전**이다. 아래 트리는 실제 소스 파일의 위치를 보여 준다. 파일의 책임과 호출 관계는 [상세 코드 트리·분리 지도](docs/research/code-tree.md)에 기록했다.

```text
.
├─ .github/workflows/                     버전별 빌드·저장소 검증 CI
│  ├─ build.yml
│  └─ verify-repository.yml
├─ build.gradle.kts                         1.21.x 빌드
├─ build-26x.gradle.kts                     26.x 빌드
├─ settings.gradle.kts                      Stonecutter 대상 버전
├─ stonecutter.gradle.kts                   JAR 수집
├─ stonecutter.properties.toml             공통 버전·대상별 의존성
├─ gradle.properties                        Loader·빌드 설정
├─ .agents/skills/instant-p2p-maintainer/   프로젝트 AI 스킬(원본)
│  └─ SKILL.md
├─ .claude/skills/instant-p2p-maintainer/   Claude Code용 스킬 진입점
│  └─ SKILL.md
├─ docs/research/                           연구 기록
│  ├─ code-tree.md
│  ├─ compatibility-and-modpack.md
│  ├─ feature-role-optimization.md
│  ├─ verification-tools.md
│  └─ work-guides/                         제안별 독립 작업 가이드
├─ tools/                                   저장소 검증 도구
│  ├─ verify/
│  └─ tests/
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
         ├─ webrtc/                          방 발견·전송·정책 23개
         │  ├─ BatchPipe.java
         │  ├─ ChannelRules.java
         │  ├─ ChzzkLink.java
         │  ├─ ExpelManager.java
         │  ├─ IceConfig.java
         │  ├─ InviteCodes.java
         │  ├─ LocalGuestListener.java
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
| **부분 구현** | 게스트 루프백 리스너와 보안 난수 초대 코드를 각각 독립 작업으로 구현하고 순수 Java 검사를 추가했다. [작업 가이드](docs/research/work-guides/README.md)에 구현·검증 경계를 기록했다. |
| **계획** | 방 목록 표시 상태, 방 생명주기, WebRTC 세션·터널, 입장 정책의 추가 분리를 단계별로 검토한다. |
| **현재 대표 빌드 확인** | 01·02 부분 구현을 포함한 이 브랜치에서 JDK 25·Gradle 9.7.1로 `:1.21:build`와 `:26.2:build`가 각각 성공했다. 명령과 남은 경계는 [작업 가이드](docs/research/work-guides/README.md)에 기록했다. |
| **남은 실행 검증** | 이 로컬 체크아웃에서는 01·02 변경의 전체 17개 대상 빌드를 실행하지 않았다. 해당 결과는 PR CI에서 별도 확인한다. 실제 Minecraft 방장·게스트 연결도 아직 확인하지 않았다. 로그인 역할 조회 03은 이 브랜치에서 PLANNED다. |

- [코드 트리·분리 지도](docs/research/code-tree.md): 전체 파일 역할, 의존 관계, 분리 후보와 유지할 계약
- [호환성·모드팩 공유 조사](docs/research/compatibility-and-modpack.md): 확인한 사실과 아직 제안 단계인 아이디어
- [필요 기능·역할·최적화 조사](docs/research/feature-role-optimization.md): 게임 스레드 대기, 데이터 경로, 신뢰 경계, 추가 기능 후보와 우선순위
- [순차 작업 가이드](docs/research/work-guides/README.md): 조사 제안을 개별 작업·검증 단계로 분리하고 01·02의 부분 구현을 추적
- [프로젝트 검증 도구](docs/research/verification-tools.md): 트리·링크·설정과 순수 Java 계약 검사, 실게임 검증 경계
- [프로젝트 AI 스킬](.agents/skills/instant-p2p-maintainer/SKILL.md): 이 포크에서 코드 변경을 검토할 때의 경계와 검증 기준. Claude Code용 프로젝트 [진입점 파일](.claude/skills/instant-p2p-maintainer/SKILL.md)은 이 원본을 가리킨다.

연구 문서와 실험 결과는 원 제작자의 공식 기능 설명이 아니다.
