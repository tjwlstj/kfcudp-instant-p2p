# 2026-09-27 전수 검수

- **기준:** 포크 `main` [`c677b47`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/c677b47c0b86b74898765a16b47ae839bcf1e071). PR #1·#2·#3·#5 병합 뒤의 상태다.
- **별도 검토:** 열린 PR #4(`feat/pr2-priority-improvements` → `beta`, [`774e684`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/774e6849136b521e8df620dd7d73b0041acaec19)).
- **범위:** 추적 파일 123개 전부다. Java 소스 53개, 빌드·CI·메타데이터, 검증 도구, 연구 문서·작업 가이드, AI 스킬이 포함된다.
- **하지 않은 것:** Minecraft 실게임 실행, 두 클라이언트 연결, 패킷 캡처, 시그널링·TURN 서버 관찰. 서버 소스는 이 저장소에 없다.

## 한눈에 보기

| 심각도 | 개수 | 대표 항목 |
|---|---|---|
| 높음 | 0 | — |
| 중간 | 5 | 방 제목의 `}` 한 글자로 공개 방 정보가 깨짐(R01), 외부 URL 무검증 열기(R02), 미지원 CPU에서 방장 크래시(R03), LAN 열기 실패 무시(R04), 모든 서버에 전용 패킷 전송(R05) |
| 낮음 | 15 | 파서 이스케이프, 패킷 증폭, 서버 객체 유지, 입력 정규화, 저장 파일 원자성 등 |
| 정보 | 7 | 설계 메모, 오래된 주석·문서 상태, 테스트 공백 |

자세한 내용은 [발견 목록](findings.md)에 있다. 각 항목에 위치, 근거, 영향, 제안, 관련 [작업 가이드](../../research/work-guides/README.md)를 적었다.

### 문제없음으로 확인한 것

- **검증 도구:** 저장소 [검증 도구](../../research/verification-tools.md) 네 개가 모두 PASS다(트리 53개, 링크 213개, 17개 버전 계약, 순수 Java 계약).
- **로컬 빌드:** `:1.21:build`와 `:26.2:build`가 성공했다. 생성 JAR의 `fabric.mod.json` 의존성(Minecraft·Loader·Java)이 대상 버전과 일치한다.
- **CI:** `main` 병합 커밋의 17개 대상 빌드가 모두 성공했다([실행 기록](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36261763350)).
- **버전 분기:** 1.21.x와 26.x 분기 쌍 161개를 대조했다. 남은 차이는 API 이름 차이였고, 행동이 갈라진 곳은 찾지 못했다(휴리스틱).
- **PR #5 수정:** 게스트 루프백 바인드와 보안 난수 초대 코드는 의도대로 구현됐고 계약 검사도 통과했다(실게임 미검증).
- **전송 계층:** `BatchPipe` 배압, ICE 후보 대기열, 직결→TURN 재시도, 클라이언트 종료 시 네이티브 해제 순서에서 새 결함은 없었다.
- **명령어 권한:** 바닐라 명령어 노드의 권한 덮어쓰기와 커스텀 페이로드 전환(채팅 마커 위조 제거)은 의도대로 동작한다.

검증 명령과 출력은 [검증 기록](verification.md)에 있다.

## 먼저 고칠 순서

1. **R01 + R06: `VillasMsg`를 Gson 파싱으로 교체한다.** 이미 계획된 [b09](../../research/work-guides/b09-villas-gson.md)와 같은 작업이다. [재현 하네스](evidence/VillasMsgProbe.java)를 계약 검사에 옮겨 회귀를 막는다. 전송 형식은 바뀌지 않는다.
2. **R03 + R04: 방 열기 실패를 삼키지 않는다.** 네이티브 로드 실패(`Error`)와 LAN 열기 실패(반환값)를 잡아 안내하고 방을 열지 않는다. 한쪽 변경으로 끝나고 전송 형식은 바뀌지 않는다.
3. **R05 + R07: 방 상태 요청을 좁힌다.** 요청은 instant-p2p 세션일 때만 보내고, 방장은 요청한 사람에게만 답한다.
4. **R02: 치지직 로그인 URL을 검증한다.** 스킴과 호스트 허용 목록을 두고, 확인 화면을 거쳐 연다.
5. 나머지 낮음 항목은 관련 작업 가이드에 붙여 처리한다. PR #4의 남은 항목은 [PR #4 검토](pr-4.md)에 정리했다.

## 기존 조사 항목 재확인

[기능·역할·최적화 조사](../../research/feature-role-optimization.md)가 제안한 항목의 `c677b47` 기준 상태다.

| 항목 | 상태 | 비고 |
|---|---|---|
| 01 게스트 루프백 바인드 | 해결(`main`) | [`LocalGuestListener`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/LocalGuestListener.java). 계약 검사 PASS, 실게임 미검증 |
| 02 초대 코드 난수 | 해결(`main`) | [`InviteCodes`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/InviteCodes.java). 형식 호환 유지 |
| 03 로그인 역할 조회 대기 | PR #4 진행 중 | [PR #4 검토](pr-4.md) |
| 04a 게스트 시그널링 동기 연결 | 남음 | [`WebRtcClient.start`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/webrtc/WebRtcClient.java#L136)가 여전히 렌더 스레드에서 `connectPairSignaling`을 부른다 |
| 04b 방장 네이티브 첫 로드 | 남음 | R03과 함께 처리하면 좋다 |
| 04c 월드 종료 고정 1.5초 | 남음 | [`kfcudp$delayedStopHost`](https://github.com/tjwlstj/kfcudp-instant-p2p/blob/c677b47c0b86b74898765a16b47ae839bcf1e071/src/client/java/kfc/udp/client/KfcudpClient.java#L1821) |
| 05 `servers`·`control` 발신자 | 남음 | 서버 소스가 필요하다 |
| 06~08 | 남음 | 코드 변화 없음 |

## 이 폴더

```text
2026-09-27/
├─ README.md          이 요약
├─ findings.md        발견 27개의 위치·근거·영향·제안
├─ verification.md    실행한 명령·출력·재현 방법
├─ coverage.md        추적 파일 123개의 검토 범위
├─ pr-4.md            열린 PR #4 검토
└─ evidence/
   ├─ branch_parity.py      1.21.x ↔ 26.x 분기 대조 스크립트
   └─ VillasMsgProbe.java   VillasMsg 파서 결함 재현 하네스
```
