# Instant P2P 호환성과 모드팩 공유 조사 (2026-09-26)

이 문서는 이 포크에서 작성한 **독립 조사 기록**이다. 원 제작자의 공식 기능 설명이나 구현 완료 선언이 아니다. Instant P2P 소스는 [`0c8e26d`](https://github.com/KITE2459/kfcudp-instant-p2p/tree/0c8e26db5d43e9bd2774ee0202dce1ae579233c1), 비교 대상 AutoModpack은 [`v4.0.6`](https://github.com/Skidamek/AutoModpack/releases/tag/v4.0.6)에 고정했다. `확인`은 해당 소스·메타데이터 또는 로컬 빌드에서 관찰한 내용이고, `제안`은 아직 구현하거나 게임에서 검증하지 않은 내용이다.

## 확인: 소스와 실행 파일의 범위

- Instant P2P는 호스트의 싱글플레이 월드가 연 LAN TCP 서버와 게스트의 로컬 Minecraft 연결 사이를 WebRTC 데이터 채널로 잇는다. 방 찾기와 연결 수립에는 별도 시그널링 서비스가 필요하며, 연결 상황에 따라 STUN/TURN을 이용한다. 관련 경로는 [`KfcudpClient`](../../src/client/java/kfc/udp/client/KfcudpClient.java), [`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java), [`WebRtcHost`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)다.
- 저장소는 CC0-1.0이고, [`settings.gradle.kts`](../../settings.gradle.kts)에는 Minecraft 1.21~1.21.11과 26.1~26.3의 **17개 개별 빌드 대상**이 있다. [`stonecutter.properties.toml`](../../stonecutter.properties.toml)의 공통 모드 버전은 1.2.3이다. 이는 빌드 설정의 목록이며 모든 대상의 실행 성공을 뜻하지 않는다.
- 제공받은 Minecraft 1.21 / Instant P2P 1.2.3 JAR을 정적으로 검사하고, 같은 소스 커밋을 JDK 25로 `:1.21:build` 했다. 두 JAR에 포함된 `.class` 223개(모드 자체 91개와 번들된 `webrtc-java` 132개)는 바이트 단위로 일치했지만 JAR 전체 해시는 같지 않았다. 이는 **클래스 파일의 일치 범위**에 관한 관찰이며, 공식 배포 출처·네이티브 라이브러리의 동일성·실행 안전성을 인증하지 않는다. 저장소에 테스트 소스는 확인되지 않았으며, 실제 Minecraft 접속 시험은 수행하지 않았다.
- 공개 저장소에서 시그널링 및 TURN 서버 구현은 확인되지 않았다. 클라이언트 코드만 바꿔도 되는 기능과 서버 프로토콜·운영이 필요한 기능을 구분해야 한다.

## 확인: 두 가지 버전의 현재 처리

| 대상 | 현재 소스에서 확인한 처리 | 입장 준비에 남는 정보 |
|---|---|---|
| Minecraft 버전 | [`P2PConfig.MC_VERSION`](../../src/client/java/kfc/udp/client/webrtc/P2PConfig.java)은 실행 중인 게임의 버전을 읽는다. 공개 방 공지는 이 값을 보낸다. 다른 버전의 방은 기본 설정에서 회색으로 표시되고 클릭 입장이 막히며, `hideOtherVersions`를 켜면 목록에서 제외된다. | 호스트의 정확한 버전과 해당 버전으로 실행할 프로필 |
| Instant P2P 버전 | [`P2PConfig.MOD_VERSION`](../../src/client/java/kfc/udp/client/webrtc/P2PConfig.java)을 해시하여 공개 방 로비 ID에 넣는다. 다른 모드 버전의 방은 같은 공개 목록에서 발견되지 않는다. | 호스트의 모드 버전과 **그 Minecraft 버전용** JAR |
| 초대 코드 직접 입력 | [`joinRoomByCode`](../../src/client/java/kfc/udp/client/KfcudpClient.java)는 입장 전에 차단 유저 확인 절차를 호출하지만 버전 쌍을 질의하지 않는다. [`RoomMembersProbe`](../../src/client/java/kfc/udp/client/webrtc/RoomMembersProbe.java)의 현재 응답에도 버전 정보가 없다. | 코드와 별도인 버전 메타데이터 또는 조회 수단 |

[`fabric.mod.json`](../../src/main/resources/fabric.mod.json)의 Minecraft 의존성은 [`build.gradle.kts`](../../build.gradle.kts)와 [`build-26x.gradle.kts`](../../build-26x.gradle.kts)에서 빌드 대상의 **정확한 게임 버전**으로 채워진다. 따라서 모드 버전 `1.2.3`이 같아도 `1.21`용 JAR과 `1.21.1`용 JAR은 별도로 선택해야 한다. Fabric Loader는 필수 의존성이 맞지 않으면 모드 진입점 실행 전에 로딩을 중단한다([Fabric 메타데이터 명세](https://docs.fabricmc.net/develop/loader/fabric-mod-json)). 현재 P2P 소스에는 Minecraft 프로필 전환이나 자체 자동 업데이트 흐름이 없다.

## 제안: 한 번의 입장 준비로 두 버전 맞추기

사용자에게는 하나의 초대·준비 과정으로 제공하되, 실제 작업은 **실행 전 프로필 선택·설치 → 게임 시작 → 방 입장** 순서로 둔다. 호스트가 쓰는 버전 쌍을 기준으로 맞추며, 두 항목을 무조건 최신으로 올리는 정책은 사용하지 않는다.

초대 메타데이터의 최소 후보는 다음과 같다.

```text
roomCode
minecraftVersion
loaderType / loaderVersion
instantP2PVersion / artifact URL / artifact SHA-256
wireProtocolVersion
expiresAt
optional modpack reference
```

`wireProtocolVersion`은 모드 출시 버전과 별도로 둔다. 같은 통신 규약을 쓰는 패치 버전을 언젠가 허용할 수 있고, 반대로 같은 모드 버전의 다른 빌드가 실제로 호환된다고 가정해서도 안 되기 때문이다. 메타데이터의 출처와 파일 해시를 검증하고, 모드 설치 전 파일 목록·게시자·변경 사항을 사용자에게 보여 주어야 한다. 해시는 파일 일치 확인에 쓰이며 게시자 자체의 신뢰를 대신하지 않는다.

현재처럼 **모드 버전별로 갈라진 공개 로비**만 조회하면 다른 버전의 방을 발견해 업그레이드를 안내할 수 없다. 공개 방까지 통합하려면 기존 로비와 양립하는 별도 버전 독립 검색 인덱스가 필요하다. 비공개 초대는 코드 자체에 버전 정보가 없으므로, 초대 링크에 메타데이터를 함께 담거나 안정적인 코드→메타데이터 조회 경로를 추가해야 한다. 기존 10자 코드 입력은 계속 지원하되 버전 정보가 없다는 사실을 명확히 표시하는 방향이 가능하다.

**작은 시제품:** 이미 설치된 런처의 인스턴스 공유 기능을 활용하고, 호스트가 인스턴스 링크와 방 코드를 함께 보낸다. [Modrinth App의 공유 인스턴스](https://modrinth.com/news/article/shared-instances/)는 Minecraft·로더·모드 구성의 변경을 초대받은 사람에게 전달한다. P2P 전용 초대 도우미나 자동 입장은 이 조사에서 구현·검증하지 않았다. 처음부터 자체 런처를 만들면 Minecraft 설치·계정 인증·Java·업데이트 관리까지 범위가 커진다.

## 확인 및 제안: AutoModpack 연결

AutoModpack v4.0.6은 호스트의 모드팩 파일을 클라이언트와 동기화한다. 공개 배포처에서 일치하는 파일을 찾으면 해당 출처를 사용할 수 있고, 그렇지 않은 파일은 호스트에서 받는다. **호스트의 개별 모드를 자동으로 최신판으로 올리는 기능은 아니다**([v4.0.6 FAQ](https://github.com/Skidamek/AutoModpack/blob/v4.0.6/docs/faq.mdx)). 호스트 모드팩에 Instant P2P JAR이 포함되면 그 파일 역시 동기화 후보가 된다. 첫 설치에는 사용자 확인과 재시작이 필요하다([빠른 시작](https://github.com/Skidamek/AutoModpack/blob/v4.0.6/docs/quick-start.mdx)). 게스트가 처음 P2P 방에 접속하려면 그 전에 호환되는 Minecraft·Fabric·Instant P2P가 설치되어 있어야 하므로 AutoModpack을 P2P의 최초 설치 수단으로 사용할 수는 없다.

AutoModpack의 [다운로드 클라이언트](https://github.com/Skidamek/AutoModpack/blob/v4.0.6/core/src/main/java/pl/skidam/automodpack_core/protocol/DownloadClient.java)는 Minecraft 로그인 연결과 별도의 TCP 연결을 연다. 현재 Instant P2P의 [`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)는 로컬 Minecraft TCP 연결 하나를 수락해 WebRTC 세션에 묶고, 그 연결이 끝나면 세션을 닫는다. 따라서 **AutoModpack과 P2P의 동시 실행만으로 모드팩 다운로드까지 통과한다고 가정할 수 없다.** 추가 연결마다 독립적인 터널과 호스트 LAN 포트 라우팅, 접속 취소·재시작 처리, 호스트별 신뢰 식별을 검토해야 한다. 이 연동은 현재 **제안 단계**이며 양쪽 모드를 설치한 호스트·게스트의 실제 접속 시험은 수행하지 않았다.

AutoModpack v4.0.6의 [런처 버전 변경 코드](https://github.com/Skidamek/AutoModpack/blob/v4.0.6/core/src/main/java/pl/skidam/automodpack_core/utils/launchers/LauncherVersionSwapper.java)는 지원되는 런처에서 로더 버전 메타데이터를 다룬다. Minecraft 게임 버전 전환은 확인되지 않았다. 따라서 게임 버전과 P2P JAR 준비는 실행 전 단계에서 해결하고, AutoModpack을 통한 나머지 모드팩 동기화는 이후의 별도 실험으로 남긴다.

호스트별 인증서 신뢰도 검증해야 한다. P2P 접속은 게스트에서 로컬 주소로 연결을 바꾸지만, AutoModpack의 [인증서 지문 저장 코드](https://github.com/Skidamek/AutoModpack/blob/v4.0.6/loader/core/src/main/java/pl/skidam/automodpack_loader_core/client/ModpackUtils.java#L604-L625)는 주소의 **호스트 문자열**을 키로 사용한다. 서로 다른 방이 같은 루프백 호스트 문자열로 보이면 신뢰 기록이 충돌할 가능성이 있다. 실제 동시 실행으로 확인한 결과는 아니며, 연동 설계에서 방별 식별과 재시작 후 주소 복원을 시험해야 한다.

사용자가 기억한 Google Drive 방식은 [AutoModpack v2.4.1](https://github.com/Skidamek/AutoModpack/blob/v2.4.1/README.md)의 외부 호스팅 기능과 부합한다. 당시에는 호스트가 만든 파일을 Google Drive에 **직접 올리고** 링크를 설정하는 구조였다. 현 v4.0.6 설계를 설명하는 근거로 구판의 업로드 절차를 사용하지 않는다.

## 확인 및 제안: 개인 PC 중계 서버

Minecraft 통합 서버, 시그널링, STUN/TURN은 서로 다른 역할이다. 호스트 PC가 Minecraft LAN 서버를 실행할 수는 있지만, 외부 게스트가 방을 발견·연결하려면 모두에게 도달 가능한 시그널링 경로가 필요하다. 직접 연결이 실패하거나 중계를 강제하면 TURN이 게임 트래픽을 전달한다. 개인 PC에 해당 서비스를 두려면 접근 가능한 주소, 방화벽·포트 설정, 서비스 운영과 클라이언트 설정 변경이 필요하다([WebRTC TURN 개요](https://webrtc.org/getting-started/turn-server)). 이 저장소만으로 제작자의 현재 시그널링 서비스를 그대로 복제하거나 개인 PC 운영의 성능을 보증할 수 없다. 자체 서버 실험도 아직 없다.

[`P2PConfig`](../../src/client/java/kfc/udp/client/webrtc/P2PConfig.java)의 기본 시그널링 주소는 `ws://`이고, 여기서 파생하는 REST 주소는 `http://`이다. 이는 **클라이언트 기본 설정의 관찰**이다. 실제 운영 서버의 암호화·프록시 구성과 중계 사용 시 상대에게 보이는 주소 정보는 서버 구현 및 네트워크 관찰 없이 확정하지 않았다.

## 검증 상태와 다음 실험

| 항목 | 현재 상태 | 다음 검증 |
|---|---|---|
| 1.21 소스 빌드와 제공 JAR의 클래스 대조 | **확인**: 모드 자체·번들 클래스를 포함한 223/223개 `.class` 일치. 전체 JAR 동일성은 확인되지 않음. | 공식 게시 파일의 해시·배포 출처와 대조 |
| 17개 Minecraft 대상 | **설정 확인**: 빌드 매트릭스에 열거됨. | 대상별 빌드 및 실제 게임 시작·방 입장 |
| 다른 Minecraft/P2P 버전의 공개 방·코드 입장 | **소스 확인**: 공개 목록 필터와 코드 입장 경로가 다름. | 두 프로필로 목록·초대 코드 동작 비교 |
| 한 번의 버전 준비 | **제안**: 실행 전 프로필과 버전별 JAR 선택. | 격리된 인스턴스로 버전 변경·재시작·재입장 시험 |
| AutoModpack v4 연동 | **제안**: 다중 TCP 연결과 신뢰·재시작 처리가 필요. | 호스트·게스트 각각 별도 인스턴스에서 첫 설치·재시작·재접속 시험 |
| 개인 PC 시그널링/TURN | **제안**: 서버 구현·운영 경로 추가 필요. | 소유한 시험 서버에서 도달성·직결·TURN 중계 확인 |

이 기록에는 모드 실행, 실제 P2P 연결, 서버 패킷 관찰, 네이티브 라이브러리 내부 감사가 포함되지 않는다. 공개 클라이언트 소스만으로 운영 서버의 보안·프라이버시 성질을 확정하지 않는다.
