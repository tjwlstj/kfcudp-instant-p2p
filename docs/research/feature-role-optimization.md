# Instant P2P 필요 기능·역할·최적화 조사 (2026-09-27)

이 문서는 포크 `main`(`1880590`) 소스를 읽고 **무엇을 더 만들어야 하는지(기능)**, **코드와 신뢰의 경계를 어떻게 나눌지(역할)**, **어디가 느리거나 낭비인지(최적화)**를 정리한다. 앞선 조사([코드 트리](code-tree.md), [호환성·모드팩](compatibility-and-modpack.md))와 겹치는 보안 항목(`ws://` 평문, `remote` 필드의 IP 노출, 차단 해시)은 반복하지 않는다.

표기는 다음과 같다.

- **확인**: 소스 또는 Minecraft·webrtc-java 바이트코드에서 직접 본 사실
- **추정**: 코드에서 추론했지만 실행·패킷·서버 코드로 확인하지 않은 내용
- **제안**: 아직 구현하지 않은 설계

빌드, 게임 실행, 패킷 캡처는 하지 않았다. 시그널링 서버(`mc-signaling`) 소스는 이 저장소에 없으므로, 서버 동작에 기대는 항목은 모두 **추정**이다.

## 요약: 먼저 할 일

| 순위 | 항목 | 분류 | 변경 범위 | 근거 |
|---|---|---|---|---|
| 1 | 게스트 로컬 포트를 루프백에만 바인드 | 역할·보안 | 게스트만, 한 줄 | 확인 |
| 2 | 초대 코드 생성기를 `SecureRandom`으로 | 역할·보안 | 방장만, 한 줄 | 확인 |
| 3 | 로그인마다 서버 스레드를 최대 0.7초 막는 역할 조회 줄이기 | 최적화 | 방장만 | 확인 |
| 4 | 접속 버튼·방 열기·월드 종료에서 렌더 스레드 대기 제거 | 최적화 | 한쪽씩 | 확인 |
| 5 | 서버 `servers`·`control` 메시지를 누가 보냈는지 서버 코드로 확인 | 역할·보안 | 조사 | 추정 |
| 6 | 송신 버퍼 상한을 전송 속도 기반으로 | 최적화 | 한쪽씩 | 계산·추정 |
| 7 | 네트워크 순단 뒤 ICE 재시작으로 연결 유지 | 기능 | 양쪽 | 확인·제안 |
| 8 | 버전 어댑터 계층으로 Stonecutter 중복 줄이기 | 역할 | 구조 | 확인 |

1~4는 상대 피어와 주고받는 형식을 바꾸지 않아 원본 사용자와 섞여도 안전하다. 5 이후는 측정 또는 양쪽 변경이 필요하다.

## 1. 최적화: 게임 스레드를 막는 지점

모두 **확인**이다. 스레드는 호출 경로로 판단했다.

| 상황 | 경로 | 막히는 스레드 | 최악 대기 |
|---|---|---|---|
| 게스트가 방에 접속 | [`ConnectScreenMixin`](../../src/client/java/kfc/udp/client/mixin/ConnectScreenMixin.java#L140) → `WebRtcBridge.start` → [`WebRtcClient.start`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L136) → `connectPairSignaling` → [`WebSocketClient.connect`](../../src/client/java/kfc/udp/client/webrtc/WebSocketClient.java#L52) | 렌더 | DNS 조회 + TCP 연결 10초 + 업그레이드 응답 10초 |
| 방장이 게스트 로그인 처리 | `checkCanJoin` → [`RoomRoles.ensureFreshForLogin`](../../src/client/java/kfc/udp/client/webrtc/RoomRoles.java#L110) → [`Roles.refreshBlocking`](../../src/client/java/kfc/udp/client/webrtc/Roles.java#L107) | 통합 서버 | 로그인마다 0.7초 |
| 방 열기 | [`openRoomNow`](../../src/client/java/kfc/udp/client/KfcudpClient.java#L1096) → `WebRtcBridge.startHost` → [`WebRtcHost.start`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L112)의 `new PeerConnectionFactory` | 렌더 | 첫 1회 네이티브 추출·로드 |
| 월드 저장 후 종료 | [`kfcudp$delayedStopHost(true)`](../../src/client/java/kfc/udp/client/KfcudpClient.java#L1824) | 렌더 | 게스트가 없어도 고정 1.5초 |

**게스트 접속:** 바닐라 접속 화면이 뜨기 전에 시그널링 WebSocket 연결을 동기로 끝낸다. 서버가 가까우면 수십~수백 ms의 멈춤이다. 서버가 안 닿으면 최대 20초 동안 게임이 응답하지 않는다. `start()`는 로컬 포트만 열고 즉시 반환하면 된다. 페어 시그널링은 이미 있는 `signalScheduler`로 넘기는 것을 제안한다.

**방장 로그인 판정:** 1.21의 `ServerLoginNetworkHandler.tickVerify`가 `PlayerManager.checkCanJoin`을 부른다. `tickVerify`는 서버 틱에서 실행되므로 방장 월드 전체가 멈춘다. 역할 목록은 캐시 검증 없이 매번 전체를 받는다. 역할 정보가 **입장 여부를 바꾸는 경우는 정원이 찼을 때의 `hasPerk`뿐**이다. 탭 배지는 늦게 도착해도 `onChanged`가 다시 보낸다. 다음을 제안한다.

1. 조인 감지 시점([`WebRtcHost.handleLobby`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L236))에 비동기로 미리 받는다. 이 시점은 로그인보다 ICE·DataChannel 수립 시간만큼 앞선다.
2. 최근 수십 초 안에 받은 적이 있으면 로그인 때 다시 받지 않는다.
3. 로그인 때 기다리는 것은 `countedPlayers >= max`인 경우로 한정한다.

**방 열기:** webrtc-java 0.14.0의 `PeerConnectionFactory` 정적 초기화는 `NativeLoader.loadLibrary`를 부른다. 이 메서드는 네이티브 라이브러리를 `Files.createTempFile`로 복사한 뒤 `System.load`한다. Windows용 DLL은 20,277,760바이트다. 방장 경로에서는 이 첫 추출이 렌더 스레드에서 일어난다. 게스트 경로는 `webrtc-accept` 스레드라 해당하지 않는다. 방 설정 화면을 열 때 등에 백그라운드 스레드에서 미리 로드하는 것을 제안한다.

POSIX가 아닌 파일 시스템에서 `NativeLoader`는 추출한 파일에 `deleteOnExit`만 건다. Windows에서는 종료 시점에도 DLL이 로드돼 있어 삭제에 실패하고, 실행할 때마다 임시 폴더에 약 20MB가 쌓일 수 있다(**추정**). 조사한 PC의 임시 폴더에는 해당 파일이 없었다. 실제 사용 후 확인해야 한다.

**월드 종료:** 1.5초는 정상 Disconnect 패킷이 터널을 빠져나갈 시간이다. 활성 세션이 없으면 기다릴 이유가 없다. 세션이 있어도 writer 큐와 `bufferedAmount`가 비는 즉시 끝내고, 1.5초는 상한으로만 남기는 것을 제안한다.

## 2. 최적화: 데이터 경로

현재 설계는 이미 지연을 의식한다(**확인**). 작업 내용은 다음과 같다.

- direct 버퍼로 바로 읽기와 `writev` 배칭([`BatchPipe`](../../src/client/java/kfc/udp/client/webrtc/BatchPipe.java))
- DataChannel 송신 상한을 16MB에서 1MB로 축소(재개 기준 256KB)
- 수신 큐를 32MB에서 4MB로 축소([`P2PConfig`](../../src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L516))

남은 병목은 아래와 같다.

### 패킷 우선순위는 불가능하고, 줄일 수 있는 것은 큐 길이뿐이다

- LAN 월드는 온라인 모드다. 로그인 뒤 스트림이 암호화되므로 터널은 Minecraft 패킷 경계와 종류를 볼 수 없다.
- `MinecraftServer.getNetworkCompressionThreshold()`는 256을 반환하고, `IntegratedServer`는 이를 재정의하지 않는다(1.21 바이트코드 **확인**). 이미 압축된 뒤 암호화된 데이터라 터널에서 추가로 압축할 여지도 없다.
- 채널은 순서 보장·재전송 하나다([`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L708)).

따라서 청크 로딩이 링크를 채우면 이동·keepalive 패킷은 송신 큐 뒤에 줄을 선다. 상한 1MiB의 최악 대기는 다음과 같다(계산).

| 실효 전송 속도 | 1MiB 큐 대기 |
|---|---|
| 10Mbps | 약 0.8초 |
| 2Mbps(느린 TURN 경로) | 약 4.2초 |

**제안:** `onBufferedAmountChange`로 초당 배출량을 추정하고, 상한을 "배출량 × 목표 지연(100~200ms)"으로 둔다. 범위는 64KB~1MB로 제한한다. 한쪽만 바꿔도 되고 전송 형식은 바뀌지 않는다. 효과는 청크 로딩 중 keepalive 왕복 시간으로 측정한다.

### 한 게스트가 다른 게스트를 막을 수 있다

- 방장은 `PeerConnectionFactory` 하나를 모든 게스트가 공유한다(**확인**).
- DataChannel 수신 콜백은 writer 큐가 차면 `offer(…, 100ms)` 루프로 대기한다([`BatchPipe`](../../src/client/java/kfc/udp/client/webrtc/BatchPipe.java#L99)). 코드 주석도 이 스레드가 WebRTC 콜백 스레드라고 적는다.

로컬 Minecraft 서버가 틱 지연으로 한 게스트의 소켓을 늦게 비우면 문제가 생긴다(**추정**). 같은 factory를 쓰는 다른 게스트의 수신 콜백과 `onBufferedAmountChange` 깨우기가 함께 밀릴 수 있다. 송신 쪽은 50ms 폴링이라 멈추지는 않지만 늦어진다.

**제안:** 먼저 콜백 대기 시간을 로그로 계측한다. 문제가 확인되면 게스트별 factory로 격리한다. 게스트당 네이티브 스레드 3개가 늘어나는 비용이 있다.

### 직결 먼저 2초, 그다음 릴레이

- 1차는 TURN 후보 없이 2초 동안 시도하고, 실패하면 PeerConnection을 새로 만들어 릴레이를 허용한다([`DIRECT_ATTEMPT_TIMEOUT_MS`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L83)).
- 직결이 안 되는 네트워크의 사용자는 접속할 때마다 최소 2초와 TURN 할당 시간을 더 쓴다.
- 반대로 시그널링·STUN이 먼 해외 사용자는 2초 안에 홀펀칭이 끝나지 않아 불필요하게 릴레이로 붙을 수 있다(**추정**).

**제안:**

- 타임아웃을 `SignalingRtt` 값에 비례시킨다.
- "같은 방장·같은 네트워크에서 직결이 실패했다"는 결과를 세션 동안 기억해 두고, 다음에는 1차를 건너뛴다. 이 결정은 기존 `r/d` 플래그로 이미 방장에게 전달되는 구조다.

### 작은 낭비

- **조인 전 연결 확인:** 조인마다 `probeTarget`이 Minecraft 서버에 빈 TCP 연결을 열고 닫는다([`WebRtcHost`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L301)). 실제 연결 실패는 `dialTarget`에서 이미 처리되므로 생략할 수 있다.
- **탭 목록 갱신:** [`kfcudp$refreshTabList`](../../src/client/java/kfc/udp/client/KfcudpClient.java#L997)는 플레이어마다 전원에게 패킷을 보내 N² 패킷이 된다. 전원을 담은 패킷 하나로 충분하다.

## 3. 최적화: 시그널링과 공개 방 확장성

### 연결 수 (확인)

- **게임 중 게스트 한 명:** 게스트 페어 WS 1개 + 방장 페어 WS 1개를 세션 내내 유지하고, 방장 로비 WS 1개를 둔다.
- **방 목록 화면 하나:** 채널 수 × 샤드 4개, 즉 최대 20개 WS와 같은 수의 수신 스레드를 쓴다([`PublicRoomBrowser`](../../src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java#L102)).

WS 하나로 여러 로비를 구독하려면 서버가 바뀌어야 한다.

### 관전자가 들어올 때마다 방 정보가 재전송된다 (확인·계산)

1. [`PublicRoomAnnouncer`](../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java#L210)는 로비 delta에 새 입장자가 있으면 자기 `room_update`를 다시 보낸다.
2. 서버는 이 메시지를 로비의 다른 peer 전원에게 중계한다.
3. 한 샤드에 공개 방 R개와 관전자 V명이 있으면, 관전자 한 명이 들어올 때마다 약 **R × (R + V − 1)건**이 전달된다.
4. 예를 들어 R=25, V=100이면 입장 한 번에 약 3,100건이다. 방 목록을 열고 닫는 행동 자체가 부하를 만든다.

**제안:**

- **서버:** "r" peer별 마지막 `room_update`를 보관했다가 새 입장자에게만 보낸다.
- **클라이언트 단독 완화:** 재전송에 0~1초 무작위 지연을 두고, 그 사이 여러 입장을 한 번으로 합친다.

## 4. 역할: 코드 책임 경계

### Stonecutter 비활성 분기 (확인, 휴리스틱 측정)

주석 처리된 다른 버전 분기(`/* … */`)가 Java 15,975행 가운데 약 **3,267행(약 20%)**이다.

| 파일 | 비활성 분기 / 전체 |
|---|---|
| `KfcudpClient` | 697 / 1,897 |
| `RoomListScreen` | 554 / 1,568 |
| `CustomRoomScreen` | 445 / 982 |
| `BlockedPlayersScreen` | 303 / 930 |

진입점과 GUI가 버전별 API 차이 때문에 메서드 본문을 통째로 복제하고 있다.

**제안:** `KfcudpClient`에 이미 있는 `kfcudp$tell`·`kfcudp$playerCount` 같은 작은 도우미를 `compat/` 계층으로 모은다. 방 생명주기 로직은 한 번만 쓴다. [코드 트리](code-tree.md)의 PLANNED 항목(방 생명주기와 Minecraft API 어댑터)과 같은 방향이다.

### 전송 계층이 UI와 정책을 직접 부른다 (확인)

- `WebRtcHost`·`WebRtcClient`는 채팅 알림과 실패 화면 때문에 `MinecraftClient`를 import하고, Stonecutter 분기를 가진다.
- 터널 포트를 등록하려고 `P2PBanManager`를 직접 호출한다.

**제안:** `TunnelListener`(연결됨·실패·연결 종류) 같은 콜백으로 방향을 뒤집는다. 전송 파일에서 버전 분기가 사라지고, Minecraft 없이 단위 시험할 수 있게 된다.

### 손으로 짠 JSON 파서 (확인)

[`VillasMsg.field`](../../src/client/java/kfc/udp/client/webrtc/VillasMsg.java#L167)의 한계는 다음과 같다.

- `\n`, `\r`, `\"`, `\\`만 해제하고 `\uXXXX`, `\t`는 그대로 둔다.
- 문자열 끝을 "바로 앞 글자가 `\`가 아님"으로만 판단한다. 그래서 백슬래시로 끝나는 제목이 들어오면 문자열 끝을 잘못 찾는다.

**제안:** 이미 번들된 Gson(`P2PConfig`·`Roles`가 사용)으로 파싱만 바꾼다. 메시지를 만드는 쪽은 그대로 둬서 전송 형식은 바뀌지 않게 한다.

### 입장 정책 파일이 너무 많은 일을 한다 (확인)

`P2PBanManager`(1,027행)가 여섯 가지를 모두 맡는다.

- 차단 저장
- 명령어
- 터널 포트→IP 매핑
- 연결 종류 기록
- 접속자 해시
- 로그인 판정

[코드 트리](code-tree.md)의 PLANNED 분리 방향과 같다.

### KCP 경로 (확인)

- `kcp/` 1,452행과 `ClientConnectionMixin` 160행을 합쳐 소스의 약 10%다.
- 사용자가 주소에 `kcp.`를 직접 입력할 때만 도달하고, KCP 방을 여는 UI는 없다.
- 기능 플래그로 격리할지, 제거할지는 운영 판단이 필요하다.

### 프로토콜 버전이 없다 (확인)

- 초대 코드 접속의 peer 이름은 `j{r|d}{sid}`와 `h{r|d}{sid}`뿐이다. 모드 버전이나 기능 정보는 오가지 않는다.
- 공개 방 목록만 로비 ID에 `MOD_VERSION` 해시를 섞어 버전별로 나뉜다.

포크가 조인 절차나 페이로드를 바꾸면, 코드로 접속한 원본 사용자와 조용히 실패할 수 있다. **제안:** 양쪽 변경 전에 버전·기능 표기 위치를 먼저 정한다. 페어 세션 메시지에 필드를 추가하는 방식 등이 있다. 서버가 peer 이름에 허용하는 길이와 문자는 확인이 필요하다.

## 5. 역할: 신뢰 경계

### 게스트 로컬 포트가 모든 네트워크 인터페이스에서 열린다 (확인)

- [`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L141)는 `new InetSocketAddress(localPort)`로 모든 인터페이스에 바인드한다. [`WebRtcBridge.findFreePort`](../../src/client/java/kfc/udp/client/webrtc/WebRtcBridge.java#L169)도 같다.
- 첫 연결 하나만 받고 최대 120초를 기다린다.
- 그래서 같은 네트워크의 다른 기기가 먼저 이 포트에 붙으면, 그 연결이 방장에게 터널링되고 실제 Minecraft 접속은 실패한다.

Windows에서는 전체 인터페이스 리슨 때문에 방화벽 허용 창이 뜰 수 있다(**추정**). **제안:** 믹스인이 이미 `127.0.0.1`로 접속하므로 루프백 주소에만 바인드하면 된다.

### 초대 코드 생성기 (확인)

- [`generateCode`](../../src/client/java/kfc/udp/client/KfcudpClient.java#L1839)는 `java.util.Random`(48비트 선형 합동 생성기)으로 32글자 중 10자를 뽑는다.
- 공개 방 코드는 목록에 그대로 노출된다.
- 같은 게임 실행 중에 이후 발급되는 비공개 초대 코드를 관찰한 출력에서 추론할 여지가 있다(**추정**: 알려진 상태 복원 기법).
- **제안:** `SecureRandom`으로 바꾼다. 비공개 방에서는 코드가 유일한 비밀이다.

### ICE 서버·peer 목록을 누가 보냈는지 검증하지 않는다 (확인 + 추정)

- 방장은 로비와 페어 세션에서 받은 **어떤 메시지든** `"servers"` 키가 있으면 ICE 서버 목록으로 채택한다([`WebRtcHost`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L228), [`#L433`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L433)). 게스트도 페어 세션에서 같다([`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L492)).
- VILLAS 중계 메시지에는 발신자 정보가 없다.
- 이 포크의 `room_update` 자체가 "peer가 보낸 임의 메시지를 서버가 그대로 중계하는 통로"를 이용한다([`PublicRoomAnnouncer`](../../src/client/java/kfc/udp/client/webrtc/PublicRoomAnnouncer.java#L31) 주석).

서버가 peer 메시지 안의 `servers`나 `control`도 그대로 중계한다면 다음 공격이 가능하다(**추정**).

- **TURN 주입:** 악의적인 방장이 게스트에게 자기 TURN 서버를 주입해 **중계 강제 사용자의 실제 IP**를 수집한다.
- **가짜 조인:** 악의적인 조인자가 방장 로비에 가짜 `control.peers`를 보내 방장이 페어 세션을 대량으로 열게 만든다.

이를 확인하려면 서버 소스를 봐야 하며, 이것이 서버 확인 항목의 1순위다.

**제안:**

- `servers`는 연결 직후 서버가 보내는 첫 메시지에서만 받는다.
- 허용 도메인 목록을 둔다.
- 동시에 열 수 있는 페어 세션 수에 상한을 둔다.

### 공개 방 정보는 마지막으로 보낸 사람이 이긴다 (확인 + 추정)

- [`PublicRoomBrowser.updateFromRoomUpdate`](../../src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java#L268)는 본문의 `code`를 키로 정보를 덮어쓴다.
- 목록에 뜨는 코드 자체는 서버가 준 peer 이름으로 정해진다.
- 그러나 같은 로비의 누구든 그 코드의 제목·버전·`host_uuid`를 덮어쓸 수 있는 구조다(**추정**, 서버 중계 방식에 의존).
- **제안:** 서버가 발신 peer 이름을 붙이거나, 방별 서명 키를 쓴다.

### 입장 판정이 연결 수립 뒤에 온다 (확인)

- `checkCanJoin`은 ICE·DataChannel·로컬 TCP 터널이 모두 선 뒤 Minecraft LOGIN 단계에서 실행된다.
- 차단된 사용자도 ICE 후보 교환까지 진행하고, TURN 할당을 소비한다.
- 직결을 허용한 방장이라면 방장의 IP를 받는다.
- 공개 방 코드는 목록에 노출돼 있으므로, 누구나 공개 방 방장들의 주소를 모을 수 있다. 이것은 WebRTC 직결의 본질이기도 하다.

**제안:**

- (a) 공개 방을 열 때 중계 강제를 권하거나 기본값으로 한다.
- (b) Minecraft 온라인 모드와 같은 세션 서버 `join`/`hasJoined` 절차를 페어 세션에서 먼저 거친다. UUID를 확인한 뒤에만 ICE 후보를 보내면, 차단·화이트리스트 판정을 연결 전에 할 수 있다. 서버 변경 없이 양쪽 모드 변경으로 가능하다고 본다. 세션 서버 이용 조건과 호출 한도는 확인해야 한다.

## 6. 필요한 기능

비슷한 모드와 비교하면 다음과 같다.

| | Instant P2P | [World Host](https://github.com/Gaming32/world-host) | [e4mc](https://github.com/vgskye/e4mc-minecraft-architectury) |
|---|---|---|---|
| 연결 | WebRTC 직결 → TURN 중계 | UPnP 포트 포워드 → 실패 시 서버 프록시 | LAN 열기만으로 외부 공개, [QUIC 중계 서버](https://github.com/vgskye/e4mc-quiclime) 경유 |
| 게스트 모드 | 필요 | 친구 기능은 필요, IP 공유 접속은 불필요 | README는 "Open to LAN as normal"만 설명 |
| 찾기 | 공개 방 목록·채널·초대 코드 | 친구 목록·온라인 상태 | 주소 공유 |

위 표는 각 저장소 README를 기준으로 했다. Instant P2P의 차별점은 공개 로비, 채널, 역할 기반 관리다. 부족한 기능은 아래와 같다(**제안**).

1. **연결 유지(ICE 재시작).**
   - 지금은 `DISCONNECTED`에서 기다리기만 하고, `FAILED`가 되면 세션을 닫는다([`WebRtcHost`](../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L556), [`WebRtcClient`](../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L695)). 그래서 Wi-Fi 전환이나 잠깐의 끊김에서 복구할 수 없다.
   - 페어 시그널링 WS는 연결 뒤에도 유지되지만, 게스트 쪽은 끊겨도 다시 접속하지 않는다.
   - 페어 시그널링 재접속과 ICE 재시작을 추가하면 DataChannel(SCTP)을 유지한 채 경로만 바꿀 수 있다. 목표는 Minecraft 타임아웃 30초 안의 복구다. 양쪽 변경이 필요하다.
2. **연결 진단 화면.** 앞선 조사에서도 서버 변경 없이 만들 수 있는 첫 기능으로 꼽았다. 위의 계측값(keepalive 왕복, `bufferedAmount`, 릴레이 여부, 콜백 대기)을 한 화면에 보이면 버그 신고의 품질도 올라간다.
3. **연결 전 신원 확인과 차단.** 5장의 (b).
4. **프로토콜 버전·기능 협상.** 포크와 원본이 공존하기 위한 전제다.
5. **다중 연결 터널.** AutoModpack 등 두 번째 TCP 연결용이다. [호환성·모드팩](compatibility-and-modpack.md)에 설계가 있다.
6. **사용자 지정 시그널링·TURN.** 앞선 조사에 범위와 조건이 있다.
7. **즐겨찾기·최근 방.** 모드만 바꾸면 되는 가장 작은 UI 기능이다.
8. **(장기) 모드 없는 게스트 접속.** e4mc처럼 서버가 TCP를 받아 중계해야 한다. 인프라 부담이 가장 크다.

## 7. 권장 순서

1. **한쪽 변경, 형식 무변경:**
   - 루프백 바인드와 `SecureRandom`
   - 로그인 역할 조회 대기 축소
   - 접속 버튼의 시그널링 비동기화
   - 네이티브 선로드
   - 월드 종료 대기 조건화

   이후 1.21.x와 26.x 대표 빌드, 그리고 방장·게스트 실게임 기준선(접속, 재접속, 강퇴, 종료)을 기록한다.
2. **계측 먼저:** 콜백 대기 시간, `bufferedAmount`, keepalive 왕복을 로그로 남긴 뒤 동적 버퍼 상한, 직결 타임아웃, factory 격리를 결정한다.
3. **구조:** 버전 어댑터, 전송 계층 콜백 역전, `VillasMsg` 파싱 교체, KCP 결정. 각 단계마다 [코드 트리](code-tree.md)를 갱신한다.
4. **양쪽 또는 서버:** 서버 소스로 `servers`·`control` 중계를 확인한다. 그다음 프로토콜 버전, ICE 재시작, 연결 전 신원 확인, `room_update` 서버 캐시를 진행한다.

## 검증 상태

- 소스와 바이트코드만 읽었다. 확인한 바이트코드는 Minecraft 1.21 Yarn 매핑 JAR의 `ServerLoginNetworkHandler`·`MinecraftServer`, 그리고 webrtc-java 0.14.0의 `PeerConnectionFactory`·`NativeLoader`다.
- 수치(비활성 분기 행 수, KCP 비율, 큐 대기, 재전송 건수)는 계산값이다. 성능 효과는 측정하지 않았다.
- 서버 동작에 기댄 항목(`servers`·`control`·`room_update` 중계, peer 이름 제약)은 서버 소스를 확보하기 전까지 추정이다.
