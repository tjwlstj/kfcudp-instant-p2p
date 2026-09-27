# 발견 목록 — 2026-09-27

기준 커밋은 [`c677b47`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/c677b47c0b86b74898765a16b47ae839bcf1e071)이다. 줄 번호 링크는 그 커밋에 고정돼 있다. 심각도와 근거 표기는 [검수 기록 안내](../README.md#읽는-법)를 따른다. "관련"은 이미 있는 [작업 가이드](../../research/work-guides/README.md) 번호다.

## 요약표

| ID | 심각도 | 영역 | 한 줄 요약 | 근거 | 관련 |
|---|---|---|---|---|---|
| [R01](#r01) | 중간 | 시그널링 | 방 제목의 `}` 뒤 필드가 모두 사라짐 | 확인(실행) | b09 |
| [R02](#r02) | 중간 | 보안 | 치지직 로그인 URL을 검증 없이 OS로 엶 | 확인(소스) | b18 |
| [R03](#r03) | 중간 | 수명 주기 | 네이티브 미지원 CPU에서 방장 크래시·게스트 무응답 | 확인(소스) | 04b |
| [R04](#r04) | 중간 | 수명 주기 | LAN 열기 실패를 무시하고 방을 엶 | 확인(소스) | — |
| [R05](#r05) | 중간 | 네트워크 예절 | 모든 서버 접속마다 전용 패킷 전송 | 확인(소스) | — |
| [R06](#r06) | 낮음 | 시그널링 | 백슬래시·유니코드 이스케이프 오판독 | 확인(실행) | b09 |
| [R07](#r07) | 낮음 | 정책 | 방 상태 요청 1건이 전원 방송으로 증폭 | 확인(소스) | — |
| [R08](#r08) | 낮음 | 수명 주기 | 닫힌 통합 서버 객체를 정적 필드가 유지 | 확인(소스) | — |
| [R09](#r09) | 낮음 | 프라이버시 | 서버 목록 핑이 방 코드를 호스트 이름으로 조회 | 확인(소스) | — |
| [R10](#r10) | 낮음 | UI | 원격 제목·닉네임의 § 서식을 그대로 표시 | 확인(소스) | b13 |
| [R11](#r11) | 낮음 | UI | 초대 코드 입력 미정규화·미검증 | 확인(소스) | 02 |
| [R12](#r12) | 낮음 | 저장 | 설정·차단 파일 비원자적 쓰기, 형식 오류에 취약 | 확인(소스) | b10 |
| [R13](#r13) | 낮음 | 명령어 | 이름 없는 화이트리스트 항목에서 NPE | 확인(소스) | — |
| [R14](#r14) | 낮음 | 명령어 | `/ban-ip <오프라인 이름>`이 이름을 IP로 저장 | 확인(소스) | — |
| [R15](#r15) | 낮음 | 정책 설계 | OP의 `/ban`이 방장 개인 차단 목록에 영구 기록 | 확인(소스) | b10 |
| [R16](#r16) | 낮음 | 호환성 | 참여 메시지 `@Redirect`의 모드 충돌 위험 | 확인(소스) | — |
| [R17](#r17) | 낮음 | 정책 | 터널 IP 매핑을 포트 번호만으로 조회 | 확인(소스) | b08 |
| [R18](#r18) | 낮음 | 빌드·CI | SNAPSHOT Loom, 미사용 속성, 워크플로 권한·캐시 | 확인(소스) | — |
| [R19](#r19) | 낮음 | 문서 | 연구 문서 줄 번호 링크 6개가 어긋남 | 확인(실행) | — |
| [R20](#r20) | 낮음 | PR #4 | 만실 로그인마다 새 조회·최대 0.7초 대기 | 확인(소스) | 03 |
| [R21](#r21) | 정보 | 정책 설계 | 바닐라 "채팅 숨기기" = 영구 차단 + 강퇴 | 확인(소스) | — |
| [R22](#r22) | 정보 | 프라이버시 | 실제 IP 기록을 게임 종료까지 보관 | 확인(소스) | — |
| [R23](#r23) | 정보 | 배포 | `environment: "*"`, 포크 배포 시 원본 식별 정보 | 확인(소스) | b12 |
| [R24](#r24) | 정보 | KCP | 미사용 이벤트 루프 선생성, 스레드 이름 의존 | 확인(소스) | b11 |
| [R25](#r25) | 정보 | 주석 | `P2PConfig`의 오래된 주석 2곳 | 확인(소스) | — |
| [R26](#r26) | 정보 | 문서 | 17개 대상 CI 성공이 상태 표에 기록되지 않음 | 확인(CI) | — |
| [R27](#r27) | 정보 | 테스트 | 계약 검사에 비정상 입력 사례 없음 | 확인(소스) | b09 |

---

## 중간

<a id="r01"></a>
### R01 — 방 제목에 `}`가 있으면 공개 방 정보가 깨진다

- **근거:** 확인(실행). [재현 하네스](evidence/VillasMsgProbe.java)가 `nickname`·`version`·`host_uuid`·`banned_hashes`를 모두 `null`로 읽는다. 영향 추적은 확인(소스), 실게임 미검증.
- **위치:**
  - [`VillasMsg.object`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/VillasMsg.java#L150)
  - [`PublicRoomBrowser.updateFromRoomUpdate`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java#L268)
- **내용:**
  - `object()`는 따옴표 안인지 따지지 않고 `{`·`}`의 깊이만 센다. 그래서 제목의 `}`에서 `room_update` 객체가 끝난 것으로 판단한다.
  - 제목 뒤에 직렬화되는 필드가 전부 빠진다: `nickname`·`channel`·`channel_and`·`current`·`max`·`version`·`host_uuid`·`banned_hashes`·`host_rtt_ms`·`opened_at_ms`.
  - 방 제목 입력란은 `}`를 막지 않는다.
- **영향:** 받는 쪽 `RoomEntry`는 다음 상태가 된다.
  - 버전이 빈 문자열이라 "다른 버전"으로 회색 표시되고 입장할 수 없다.
  - 채널이 빈 문자열이라 기본 채널 `normal`로 간주된다. 그래서 사용자 지정 채널의 방은 자기 채널 관전자 목록에서 사라진다.
  - 방장의 차단 해시와 UUID가 비어 목록 필터가 적용되지 않는다. 실제 입장은 방장 `checkCanJoin`이 계속 막는다.
  - 인원은 0/0으로 보인다.
- **제안:**
  - [b09](../../research/work-guides/b09-villas-gson.md)대로 읽기만 Gson `JsonParser`로 바꾸고, 보내는 문자열 형식은 유지한다.
  - 하네스 사례를 `ContractCheck`에 옮겨 회귀를 막는다.

<a id="r02"></a>
### R02 — 치지직 로그인 URL을 검증 없이 OS로 연다

- **근거:** 확인(소스). 공격 경로는 추정이다.
- **위치:**
  - [`ChzzkLinkScreen.onLoginClicked`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/gui/ChzzkLinkScreen.java#L329)
  - [`ChzzkLink.requestAuthUrl`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/ChzzkLink.java#L48)
  - [`SIGNALING_HTTP_URL`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L65)
- **내용:**
  - 응답의 `authUrl`을 `Util.getOperatingSystem().open(URI.create(url))`로 곧장 연다. 스킴·호스트 검사가 없다.
  - 기본 REST 경로는 평문 `http://`다.
  - 바닐라 채팅 링크는 허용 프로토콜 검사와 확인 화면을 거친다.
- **영향(추정):** 같은 네트워크의 중간자가 응답을 바꾸면 `file:` URI나 임의 프로토콜 핸들러를 사용자 OS가 열게 할 수 있다. 사용자가 로그인 버튼을 눌러야 성립한다.
- **제안:**
  - `https`와 예상 인증 도메인만 허용한다.
  - 바닐라 링크 확인 화면을 거친다.
  - 시그널링 HTTPS 전환은 [b18](../../research/work-guides/b18-custom-signaling-turn.md)과 함께 검토한다.

<a id="r03"></a>
### R03 — 네이티브가 없는 CPU에서 방장은 크래시, 게스트는 응답 없음

- **근거:** 확인(소스·바이트코드). 해당 플랫폼 실행은 미검증이다.
- **위치:**
  - [`WebRtcHost.start`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/WebRtcHost.java#L112)
  - [`openRoomNow`의 `catch (Exception)`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/KfcudpClient.java#L1094)
  - [`WebRtcClient` 팩토리 생성](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L685)
  - [`acceptAndBridge`의 `catch (Exception)`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L227)
- **내용:**
  - 번들된 네이티브는 네 가지뿐이다: `webrtc-java-windows-x86_64.dll`, `libwebrtc-java-linux-x86_64.so`, `libwebrtc-java-macos-x86_64.dylib`, `libwebrtc-java-macos-aarch64.dylib`(생성 JAR 확인).
  - `AudioDeviceModuleBase`와 `PeerConnectionFactory`의 정적 초기화가 `NativeLoader.loadLibrary`를 부른다. 실패하면 `ExceptionInInitializerError`가 된다.
  - 이것은 `Error`라서 호출부의 `catch (Exception)`에 잡히지 않는다.
- **영향:**
  - **방장:** Linux·Windows arm64 네이티브 JVM에서 방을 열면 렌더 스레드로 오류가 전파된다(게임 크래시 추정).
  - **게스트:** `webrtc-accept` 스레드가 실패 화면 없이 끝나고, Minecraft 접속 타임아웃까지 기다린다.
- **제안:**
  - 초기화 때 지원 플랫폼을 판정해 버튼을 비활성화하고 이유를 보여 준다.
  - 또는 팩토리 생성부에서 `LinkageError`까지 잡아 기존 실패 메시지로 잇는다.
  - [04b](../../research/work-guides/04b-host-native-load.md)의 선로드와 같이 처리한다.

<a id="r04"></a>
### R04 — LAN 열기가 실패해도 초대 코드를 발급한다

- **근거:** 확인(소스)
- **위치:**
  - [`openRoomNow`의 `kfcudp$publishServer` 호출](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/KfcudpClient.java#L1065)
  - [1.21.x 래퍼(반환값 버림)](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/KfcudpClient.java#L550)
- **내용:**
  - `openToLan`/`publishServer`는 포트 바인드에 실패하면 `false`를 돌려준다.
  - 1.21.x 래퍼는 그 값을 버린다. 26.x 래퍼는 `boolean`을 돌려주지만 호출부가 확인하지 않는다.
  - 이어서 열리지 않은 포트를 대상으로 `WebRtcHost`를 시작하고 공개 목록에 올린다.
- **영향:**
  - 방장은 초대 코드와 공개 안내를 받는다.
  - 조인마다 `probeTarget`이 실패해 요청이 무시되고, 게스트는 5초 뒤 "호스트를 찾을 수 없음"을 본다.
  - 방장에게는 아무 경고도 없다.
- **제안:** 반환값 또는 `isRemote()`를 확인한다. 실패하면 `host_failed`를 안내하고, 정원 게이트 같은 부분 상태를 되돌린다.

<a id="r05"></a>
### R05 — 모든 서버 접속마다 전용 패킷을 보낸다

- **근거:** 확인(소스). 서버 쪽 반응은 추정이다.
- **위치:** [`RoomRoles.register`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/RoomRoles.java#L87)
- **내용:**
  - `ClientPlayConnectionEvents.JOIN`에서 조건 없이 `instant-p2p:moderation`(REQUEST_STATE)을 보낸다. 싱글플레이와 일반 멀티 서버도 포함된다.
  - 같은 이벤트의 `ExpelManager` 재요청은 `DevBadge.isP2pSessionActive()`로 거른다.
  - 저장소 어디에도 `ClientPlayNetworking.canSend` 확인이 없다.
- **영향(추정):** 이 모드를 모르는 서버에 알 수 없는 채널 패킷이 간다. 대부분은 무시하지만, 엄격한 서버·플러그인은 경고하거나 차단할 수 있고 모드 설치 사실도 드러난다.
- **제안:** `ClientPlayNetworking.canSend(P2PNet.Moderation.ID)`가 참이거나 instant-p2p 세션일 때만 보낸다.

## 낮음

<a id="r06"></a>
### R06 — `VillasMsg.field()`가 이스케이프를 잘못 읽는다

- **근거:** 확인(실행). [재현 하네스](evidence/VillasMsgProbe.java)에서 `C:\` → `C:\",`, `A \u0026 B\tC`가 그대로 나왔다.
- **위치:** [`VillasMsg.field`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/VillasMsg.java#L167)
- **내용:**
  - 끝 따옴표를 "바로 앞 글자가 `\`인가"로만 판정해서, 백슬래시로 끝나는 값을 잘못 자른다.
  - `\uXXXX`·`\t`는 풀지 않는다.
- **제안:** R01과 같은 교체.

<a id="r07"></a>
### R07 — 방 상태 요청 1건이 방 전원 방송으로 증폭된다

- **근거:** 확인(소스)
- **위치:** [`ExpelManager.handleRequest`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/ExpelManager.java#L295)
- **내용:** 등급과 무관한 REQUEST_STATE를 받으면 `RoomRoles.broadcast(server)`로 방장 외 전원에게 보낸다. 빈도 제한이 없다.
- **영향:** 게스트 한 명이 요청을 반복하면 요청마다 접속자 수만큼 패킷이 나간다.
- **제안:** 요청자에게만 답하고, 플레이어별 최소 간격을 둔다. 구성 변경 방송은 기존 JOIN 경로가 이미 맡는다.

<a id="r08"></a>
### R08 — 닫힌 통합 서버 객체를 정적 필드가 계속 잡고 있다

- **근거:** 확인(소스). 메모리 영향은 추정이다.
- **위치:** [`ExpelManager.activeServer`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/ExpelManager.java#L259), [갱신 위치](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/ExpelManager.java#L272)
- **내용:** 일반 싱글플레이를 포함한 모든 서버 JOIN에서 값을 덮어쓰고, 지우는 곳이 없다.
- **영향:** 월드를 나간 뒤에도 다음 월드에 들어갈 때까지 멈춘 서버와 그 월드 객체가 수거되지 않는다.
- **제안:** `SERVER_STOPPED`에서 비우거나, 서버를 인자로 받는다.

<a id="r09"></a>
### R09 — 서버 목록 핑이 방 코드를 호스트 이름으로 조회한다

- **근거:** 확인(소스)
- **위치:** [`ServerAddressMixin`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/mixin/ServerAddressMixin.java#L102). 다른 버전 분기도 같다.
- **내용:** 저장된 서버 주소가 `webrtc.<코드>`면 `<코드>`라는 호스트로 핑을 보낸다.
- **영향:**
  - 비공개 방 코드가 DNS 질의로 흘러간다.
  - 와일드카드 DNS가 있는 망에서는 무관한 호스트로 접속을 시도한다.
  - 목록 표시는 어차피 실패한다.
- **제안:** `webrtc.` 항목은 핑을 건너뛰고 고정 상태를 표시한다.

<a id="r10"></a>
### R10 — 원격 제목·닉네임의 § 서식을 그대로 그린다

- **근거:** 확인(소스)
- **위치:** [`RoomListScreen` 제목 그리기](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/gui/RoomListScreen.java#L1327), [닉네임](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/gui/RoomListScreen.java#L1334)
- **내용:** 게임 입력란은 §를 막지만, 수정된 클라이언트가 보낸 `room_update`는 색·난독(§k) 서식이 적용된 채 보인다.
- **제안:** 받을 때 서식 코드를 제거한다. 공지 위조 전반은 [b13](../../research/work-guides/b13-room-provenance.md) 범위다.

<a id="r11"></a>
### R11 — 초대 코드 입력을 정규화·검증하지 않는다

- **근거:** 확인(소스)
- **위치:** [`RoomListScreen.onJoinByCode`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/gui/RoomListScreen.java#L844), [`WebRtcBridge.start`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/WebRtcBridge.java#L55)
- **내용:**
  - 공백만 잘라 시그널링 URL 경로에 그대로 넣는다.
  - 코드는 대문자라서, 소문자로 입력하면 다른 세션으로 가 "호스트를 찾을 수 없음"이 된다.
  - `/`·`?` 같은 문자도 경로에 들어간다(자기 클라이언트 범위).
- **제안:** 대문자로 바꾼 뒤 [`InviteCodes`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/InviteCodes.java) 형식(10자, 32자 알파벳)을 검사하고, 실패하면 바로 안내한다. `webrtc.` 주소 파싱에도 적용한다.

<a id="r12"></a>
### R12 — 설정·차단 파일을 원자적으로 쓰지 않고, 값 형식 오류에 약하다

- **근거:** 확인(소스). 손실 시나리오는 추정이다.
- **위치:**
  - [`P2PConfig.updateSettingsFile`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L322)
  - [`loadRelayOnly` 등 정적 로드](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L111)
  - [`P2PBanManager.save`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L426)·[`loadMap`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L412)
  - `ExpelManager`·`P2PWhitelistManager`도 같다.
- **내용:**
  - `FileWriter`로 원본을 바로 덮어쓴다.
  - 읽기 실패는 예외를 삼키고 빈 목록으로 시작한다.
  - `settings.json` 값이 배열·객체·`null`이면 정적 초기화 중 `getAsBoolean`/`getAsString`이 예외를 던져 클래스 로드가 실패한다.
- **영향(추정):**
  - 쓰는 도중 게임이 종료되면 파일이 잘린다.
  - 차단 목록은 빈 목록으로 읽힌 뒤, 다음 저장에서 영구히 사라질 수 있다.
  - `settings.json`이 깨지면 `chzzkViewToken`이 새로 만들어져 기존 치지직 연동 조회가 막힌다.
- **제안:**
  - 임시 파일에 쓴 뒤 `ATOMIC_MOVE`로 바꿔치기한다.
  - 읽기에 실패하면 원본을 `.bak`으로 보존한다.
  - 값 읽기는 형식을 검사하는 도우미로 통일한다.

<a id="r13"></a>
### R13 — 이름 없는 화이트리스트 항목에서 명령어가 NPE로 끝난다

- **근거:** 확인(소스)
- **위치:** [`P2PWhitelistManager.removePlayer`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PWhitelistManager.java#L140), `executeList`
- **내용:** `get("name").getAsString()`을 null 검사 없이 부른다. 차단 목록 쪽 `pardonPlayer`는 같은 경우를 이미 막아 두었다.
- **제안:** 같은 방어 코드를 적용한다.

<a id="r14"></a>
### R14 — `/ban-ip <오프라인 이름>`이 이름을 IP로 저장한다

- **근거:** 확인(소스)
- **위치:** [`executeBanIp`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L910)
- **내용:** 입력이 온라인 플레이어 이름이 아니면 그대로 IP 문자열로 저장하고 "Banned IP: 이름"이라고 성공을 알린다.
- **제안:** IP 형식이 아니면 거부하고 안내한다.

<a id="r15"></a>
### R15 — OP의 `/ban`이 방장 개인 차단 목록에 영구 기록된다

- **근거:** 확인(소스). 설계 사항이다.
- **위치:** [`P2PBanManager.banPlayer`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L443)
- **내용:** 방 명령어 차단과 방장의 개인 차단이 같은 파일이다. 개인 차단은 방 목록 숨김, 채팅 숨김, 앞으로 여는 모든 방의 입장 거부를 뜻한다. 방장이 OP를 준 게스트가 `/ban`하면 방장의 영구 목록과 바닐라 채팅 숨김이 함께 바뀐다.
- **제안:** 방 범위 차단과 개인 차단을 나누거나, OP의 차단은 이번 세션 범위로 두고 방장에게 알린다. 정책 분리는 [b10](../../research/work-guides/b10-policy-split.md) 범위다.

<a id="r16"></a>
### R16 — 참여 메시지 `@Redirect`가 다른 모드와 충돌하기 쉽다

- **근거:** 확인(소스). 충돌은 추정이다.
- **위치:** [`PlayerJoinMessageMixin`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/mixin/PlayerJoinMessageMixin.java#L45)
- **내용:** 접속 메시지 방송 호출 자체를 `@Redirect`로 바꾼다. 같은 호출을 가로채는 모드가 있으면 믹스인 적용이 실패한다(`required: true`).
- **제안:** 메시지 인자만 바꾸는 `@ModifyArg`를 쓴다.

<a id="r17"></a>
### R17 — 터널 IP 매핑을 포트 번호만으로 찾는다

- **근거:** 확인(소스)
- **위치:** [`P2PBanManager.resolveRealIp`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L629)
- **내용:** 바닐라 LAN으로 직접 들어온 원격 클라이언트의 출발 포트가 우연히 터널 포트와 같으면, 그 클라이언트가 터널 IP로 판정된다.
- **제안:** 주소가 루프백일 때만 매핑을 쓴다. 터널 정보 전달 구조는 [b08](../../research/work-guides/b08-tunnel-listener.md) 범위다.

<a id="r18"></a>
### R18 — 빌드 재현성과 워크플로 설정

- **근거:** 확인(소스)
- **위치:** [`build.gradle.kts`](../../../build.gradle.kts), [`build-26x.gradle.kts`](../../../build-26x.gradle.kts), [`gradle.properties`](../../../gradle.properties), [`.github/workflows/build.yml`](../../../.github/workflows/build.yml)
- **내용:**
  - Loom 플러그인이 `1.16-SNAPSHOT`(1.21.x)과 `1.17-SNAPSHOT`(26.x)이다. 같은 커밋이라도 빌드 시점에 따라 플러그인이 달라질 수 있다.
  - `gradle.properties`의 `loom_version`은 어디서도 읽지 않는다. 버전이 `plugins` 블록에 직접 적혀 있다.
  - 빌드 워크플로에 `permissions:`가 없어 저장소 기본 토큰 권한을 따른다. 검증 워크플로는 `contents: read`로 제한돼 있다.
  - Gradle 캐시가 없어 17개 작업이 각각 약 4~10분 걸린다.
- **제안:**
  - 릴리스용 빌드는 고정된 Loom 버전을 쓰고, 쓰지 않는 속성은 지운다.
  - `permissions: contents: read`를 명시하고, `gradle/actions/setup-gradle`로 캐시한다.

<a id="r19"></a>
### R19 — 연구 문서의 줄 번호 링크 6개가 어긋났다

- **근거:** 확인(실행). 링크 줄을 현재 소스와 대조했다.
- **위치:** [`feature-role-optimization.md`](../../research/feature-role-optimization.md)
- **내용:** PR #5가 줄을 밀어서 다음 링크가 다른 줄을 가리킨다.

  | 링크 | 원래 가리키던 코드 | 지금 줄 |
  |---|---|---|
  | `WebRtcClient.java#L492` | `servers` 채택 | 504 |
  | `WebRtcClient.java#L695` | ICE `FAILED` 처리 | 707 |
  | `WebRtcClient.java#L708` | 순서 보장 채널 | 721 |
  | `KfcudpClient.java#L1096` | `startHost` | 1093 |
  | `KfcudpClient.java#L1824` | `kfcudp$delayedStopHost` | 1821 |
  | `KfcudpClient.java#L997` | `kfcudp$refreshTabList` | 994 |

  `check_links.py`는 그 줄이 존재하는지만 검사한다.
- **제안:**
  - 시점 기록 문서는 커밋 고정 링크를 쓴다.
  - 현재 코드를 가리키는 링크는 링크 글자의 식별자가 그 줄 근처에 있는지까지 `check_links.py`가 보도록 보강한다.

<a id="r20"></a>
### R20 — PR #4: 만실 로그인마다 새 조회와 최대 0.7초 대기

- **근거:** 확인(소스). [PR #4 검토](pr-4.md)에 정리했다.

## 정보

<a id="r21"></a>
### R21 — 바닐라 "채팅에서 숨기기"가 영구 차단과 강퇴로 이어진다

- **위치:** [`SocialHideMixin`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/mixin/SocialHideMixin.java#L30)
- **내용:** 의도된 연동이지만 바닐라의 가벼운 숨기기와 결과가 다르다. 방장이면 그 자리에서 내보내고, 차단이 파일에 남는다.
- **제안:** 안내 문구나 설정 스위치를 검토한다.

<a id="r22"></a>
### R22 — 실제 IP 기록을 게임 종료까지 보관한다

- **위치:** [`uuidToRealIp`·`connectionTypeByIp`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PBanManager.java#L95)
- **내용:** 지우는 코드가 없다. 방이 바뀌어도 메모리에 남는다.
- **제안:** 방을 닫을 때 비운다.

<a id="r23"></a>
### R23 — 배포 메타데이터

- **위치:** [`fabric.mod.json`](../../../src/main/resources/fabric.mod.json)
- **내용:**
  - 클라이언트 전용 모드인데 `environment`가 `"*"`다.
  - 포크에서 JAR을 배포한다면 모드 id·이름·연락처가 원본(KITE2459, Modrinth)을 가리킨다.
  - 모드 버전은 공개 방 로비 ID를 가른다.
- **제안:** 배포 전에 식별 정보와 [b12](../../research/work-guides/b12-protocol-capabilities.md)의 버전 정책을 함께 정한다.

<a id="r24"></a>
### R24 — KCP 경로의 부수 비용

- **위치:** [`ClientConnectionMixin`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/mixin/ClientConnectionMixin.java#L44), [`KcpAddressRegistry`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/kcp/KcpAddressRegistry.java#L20)
- **내용:**
  - 2스레드 Netty 이벤트 루프가 `ClientConnection` 클래스 초기화 때 만들어진다. KCP를 쓰지 않아도 생긴다.
  - KCP 플래그 소비가 바닐라 스레드 이름 `Server Pinger`에 기대고 있다.
- **제안:** [b11](../../research/work-guides/b11-kcp-decision.md) 결정 때 함께 정리한다.

<a id="r25"></a>
### R25 — `P2PConfig`의 오래된 주석

- **위치:** [`MOD_VERSION` 주석](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L47), [채널 주석](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/P2PConfig.java#L347)
- **내용:**
  - `RoomEntry.sameVersion`이 모드 버전도 본다고 적혀 있지만, 실제로는 Minecraft 버전만 본다.
  - 방 목록이 모든 채널을 받는다고 적혀 있지만, 지금은 채널별 로비만 구독한다.

<a id="r26"></a>
### R26 — 17개 대상 CI 성공이 상태 표에 기록되지 않았다

- **내용:**
  - [작업 가이드](../../research/work-guides/README.md), [검증 도구](../../research/verification-tools.md), 루트 README는 01·02 변경의 전체 17개 대상 빌드를 "로컬에서 실행하지 않았으니 PR CI에서 별도 확인한다"로만 남겨 두었다.
  - `main` 병합 커밋의 [CI](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36261763350)에서는 17개 작업이 모두 성공했다. 이 결과를 상태 표에 기록하면 된다.
  - 실게임 미검증 표기는 그대로 유지해야 한다.

<a id="r27"></a>
### R27 — 계약 검사에 비정상 입력 사례가 없다

- **위치:** [`ContractCheck`](../../../tools/tests/java/kfc/udp/client/webrtc/ContractCheck.java)
- **내용:** 정상 경로만 다룬다.
- **제안:** R01·R06의 재현 사례, 잘못된 JSON, 매우 긴 값을 추가한다.
