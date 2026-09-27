# 검증 기록 — 2026-09-27

이번 검수에서 실제로 돌린 명령과 결과다. 모두 기준 커밋 [`c677b47`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/c677b47c0b86b74898765a16b47ae839bcf1e071)의 깨끗한 체크아웃(별도 워크트리)에서 실행했다. 로컬 경로는 적지 않는다.

## 1. 저장소 검증 도구

[검증 도구](../../research/verification-tools.md)를 Python 3와 JDK 21로 실행했다.

| 도구 | 결과 |
|---|---|
| `check_tree.py` | PASS: README와 코드 트리가 Java 53개를 모두 나열, 도구 트리 6개 |
| `check_links.py` | PASS: Markdown 40개의 링크 213개 |
| `check_project_contract.py` | PASS: Claude 스킬 진입점·무시 규칙, 17개 버전의 Stonecutter·CI·의존성 일치 |
| `run_contracts.py` | PASS: 채널·시그널링 기본 계약, 로컬 보안 3건(초대 코드 형식·난수 주입점, 루프백 선호 포트, 25566 점유 시 대체 포트) |

이 도구들은 링크 줄 번호의 **존재**만 본다. 그 줄이 여전히 같은 코드인지는 따로 대조했다([R19](findings.md#r19)).

## 2. 로컬 빌드

```text
JDK 25, Gradle 9.7.1
./gradlew :1.21:build :26.2:build --configure-on-demand --no-daemon
BUILD SUCCESSFUL in 3m 22s (24 tasks)
```

| 대상 | JAR 크기 | `depends` | 확인 내용 |
|---|---|---|---|
| 1.21 | 31,405,523 B | minecraft `1.21`, fabricloader `>=0.18.4`, java `>=21` | refmap 포함, `InviteCodes`·`LocalGuestListener` 클래스 포함 |
| 26.2 | 31,398,378 B | minecraft `26.2`, fabricloader `>=0.19.5`, java `>=25` | 리매핑 없는 빌드(refmap 없음이 정상) |

- **자체 클래스:** 두 JAR 모두 `kfc/` 클래스 94개가 들어 있다.
- **번들 네이티브:** 4개, 합계 74,249,576 B. Windows x86_64, Linux x86_64, macOS x86_64·aarch64다([R03](findings.md#r03)의 근거).
- **경고:**
  - 1.21: 기존 `CommandNodeAccessor`의 "Unable to locate obfuscation mapping"
  - deprecated API 사용 알림
  - Gradle 10 비호환 기능 사용 알림

  새 경고는 없다.

## 3. GitHub Actions

| 워크플로 | 커밋 | 결과 |
|---|---|---|
| `build`(17개 대상) | `main` 병합 `c677b47` | [성공](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36261763350) |
| `verify repository` | `main` 병합 `c677b47` | [성공](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36261763361) |
| `build` | PR #4 | [성공](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36262131996) |

컴파일 성공은 Mixin 적용이나 P2P 연결 동작을 증명하지 않는다.

## 4. 1.21.x ↔ 26.x 분기 대조

[`branch_parity.py`](evidence/branch_parity.py)는 Stonecutter 버전 분기를 두 종류로 나눠 본다.

- **if/else 쌍:** 두 본문을 같은 이름 체계(Yarn → Mojang)로 바꾼 뒤 비교한다. 대부분 26.x ↔ 1.21.x이고, 1.21.x 안에서 갈리는 쌍(`>=1.21.9` 등)도 포함한다.
- **`else` 없는 블록:** 26.3 전용 메서드나 `>=1.21.9 <26.1` 같은 구간이다. 대응 본문이 없어 쌍으로 비교할 수 없으므로, 같은 자리의 이웃 블록끼리 비교하고 홀로 있는 블록은 본문 전체를 출력한다.

```text
py -3 docs/review/2026-09-27/evidence/branch_parity.py src
pairs=163 textually-different=102 import-only=32 reported=70
blocks-without-else=111 import-only=0 listed=111 multi-way-sites=20 lone-blocks=6
```

**if/else 쌍:**

- 글자가 다른 102쌍 가운데 32쌍은 import 줄만 다르다.
- 나머지 70쌍(초안에서 6줄 미만이라 빠졌던 34쌍 포함)의 차이를 모두 읽었다.
- 대부분 다음 셋이었다.
  - API 이름·위젯 빌더·렌더링 호출 차이
  - 26.x에서 믹스인이 대신 처리하는 빈 메서드(정원·게임 모드)
  - 같은 값의 상수 표기(GLFW 키 코드 257·335·256)
- **동작이 다른 곳 1건:** 26.x의 `RoomListScreen.myUuid()`는 `getProfileId()` 결과를 null 확인 없이 `toString()`한다. 1.21.x는 `getUuidOrNull()`을 확인한다([R28](findings.md#r28)).

**`else` 없는 블록:**

- 111개를 26곳(여러 갈래 20곳, 단독 6곳)에서 모두 읽었다.
- 이웃 갈래 사이의 차이는 API 이름, 입력 이벤트 타입, 렌더링 파이프라인, 사운드 재생 호출이었다.
- 버전마다 의도적으로 다르게 동작하는 곳도 있다. 코드 주석에 이유가 적혀 있어 대조 결함으로 보지 않았다.
  - 26.2 이상: 바닐라 LAN 설정 화면 동기화
  - 26.3: 접속자 권한 판정 재정의
  - 1.21.9 미만: 정원 필드 직접 덮어쓰기

**한계:** 이름 치환표와 블록 묶기는 휴리스틱이다. 이 대조는 소스 비교일 뿐이고, 각 버전에서 게임을 실행해 동작이 같은지 확인하지는 않았다. 대조한 범위에서 한쪽에만 들어간 수정은 R28 한 건만 찾았다.

## 5. `VillasMsg` 파서 재현

[`VillasMsgProbe.java`](evidence/VillasMsgProbe.java)를 기준 커밋의 `VillasMsg.java`와 함께 임시 디렉터리에 컴파일해 실행했다.

```text
DIFF R06 title ending in backslash: sent=[C:\] parsed=[C:\",]
DIFF R06 unicode and tab escapes: sent=[A & B	C] parsed=[A \u0026 B\tC]
DIFF R01 nickname after '}' title: sent=[n] parsed=[null]
DIFF R01 version after '}' title: sent=[1.21] parsed=[null]
DIFF R01 host_uuid after '}' title: sent=[host-uuid] parsed=[null]
DIFF R01 banned_hashes after '}' title: sent=[hash1,hash2] parsed=[null]
```

사례마다 입력의 출처가 다르다.

| 사례 | 입력 출처 | 판정 |
|---|---|---|
| R01 `}` 제목 뒤 필드 소실 | 이 모드의 `VillasMsg.roomUpdate` 생성 결과 | 모드가 직접 보내는 메시지를 자기 파서가 잘못 읽는다. 서버 동작과 무관하다 |
| R06 백슬래시로 끝나는 제목 | 이 모드의 `VillasMsg.roomUpdate` 생성 결과 | 위와 같다 |
| R06 `&`·`\t` 이스케이프 | 하네스 안에서 손으로 쓴 JSON 문자열 | 파서가 표준 JSON 이스케이프를 풀지 못한다는 것만 확인했다. 이 모드의 `escape()`는 `\u`·`\t`를 만들지 않는다. 시그널링 서버나 다른 클라이언트가 이런 문자열을 실제로 보내는지는 확인하지 않았다(추정) |

## 6. webrtc-java 바이트코드 확인

Maven 아티팩트 `dev.onvoid.webrtc:webrtc-java:0.14.0`을 `javap`로 확인했다.

- `AudioDeviceModuleBase`와 `PeerConnectionFactory`의 정적 초기화가 `NativeLoader.loadLibrary("webrtc-java")`를 부른다. 실패하면 `RuntimeException`을 던진다. 정적 초기화 안의 예외이므로 호출자에게는 `ExceptionInInitializerError`로 보인다.
- `NativeLoader.getOSArch`는 `x86_64`/`x86-64`/`amd64`를 하나로 묶는다. 번들된 네이티브 목록(2절)과 합쳐 보면 Linux·Windows의 arm64는 지원되지 않는다.
- Windows 네이티브 DLL 하나의 크기는 20,277,760 B다. 첫 사용 때 임시 파일로 복사된 뒤 로드된다([04b](../../research/work-guides/04b-host-native-load.md), [b21](../../research/work-guides/b21-native-temp-files.md)).

## 7. 하지 않은 검증

- 두 Minecraft 클라이언트의 방장·게스트 연결: 직결·TURN, 재접속, 강퇴·차단, 월드 종료
- arm64 JVM에서의 실제 크래시 모양([R03](findings.md#r03))
- 이 모드를 모르는 서버·플러그인의 전용 패킷 반응([R05](findings.md#r05))
- 시그널링 서버가 `servers`·`control`·`room_update`를 발신자 확인 없이 중계하는지(서버 소스 필요)
- 1.21·26.2를 제외한 15개 대상의 로컬 빌드. CI 결과로 대신했다.
