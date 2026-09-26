# 저장소 검증 도구

이 포크의 PR을 같은 기준으로 점검하기 위한 작은 도구 모음이다. [코드 트리](code-tree.md)는 소스 책임을 찾는 지도이고, 아래 도구는 그 지도와 일부 설정·프로토콜 계약이 실제 파일에서 어긋났는지 검사한다. 모두 저장소에 포함되며 GitHub Actions의 `verify repository`에서도 실행한다.

```text
tools/
├─ verify/
│  ├─ check_tree.py              Java 파일 목록 ↔ README·코드 트리
│  ├─ check_links.py             로컬 Markdown 링크·소스 줄 번호
│  ├─ check_project_contract.py  Stonecutter·CI·의존성 버전, AI 스킬 경로
│  └─ run_contracts.py           JDK로 순수 Java 계약 검사 실행
└─ tests/java/kfc/udp/client/webrtc/
   ├─ ContractCheck.java        채널·시그널링 계약 검사
   ├─ LocalSecurityCheck.java   루프백 소켓·초대 코드 검사
   └─ RoleRefreshCheck.java     역할 조회 동시성·시간 제한 검사
.github/workflows/verify-repository.yml
docs/research/verification-tools.md
```

## 로컬 실행

저장소 루트에서 Python 3.11 이상과 JDK 21 이상으로 실행한다. Python 도구에는 외부 패키지가 필요 없다. Windows에서는 `python` 명령이 Store 별칭일 수 있으므로 `py -3`을 사용한다.

```powershell
py -3 tools/verify/check_tree.py
py -3 tools/verify/check_links.py
py -3 tools/verify/check_project_contract.py
py -3 tools/verify/run_contracts.py --java-home 'C:\path\to\jdk-21'
```

JDK가 `PATH` 또는 `JAVA_HOME`에 있으면 `--java-home`을 생략할 수 있다. Java 실행기는 컴파일 산출물을 임시 디렉터리에 만들고 제거하며, 프로젝트의 `build/`나 소스에 쓰지 않는다. Gradle, 게임 클라이언트, 시그널링 서비스, 외부 네트워크는 필요하지 않다.

각 도구는 성공 시 `PASS`, 대상 체크아웃에 없는 선택 기능이면 `SKIP`, 불일치 시 `FAIL`과 종료 코드 1을 반환한다. `run_contracts.py`의 기본 채널·시그널링 묶음은 필수이며 로컬 보안·역할 조회 묶음은 대상 소스가 모두 없을 때만 `SKIP`한다. 선택 묶음의 소스가 일부만 있으면 `FAIL`한다. `--repo PATH`를 주면 현재 도구를 다른 체크아웃의 소스에 적용할 수 있다. 병합 전 PR 기준 커밋이나 별도 개발 브랜치를 비교할 때 유용하다.

```powershell
py -3 tools/verify/check_project_contract.py --repo 'C:\path\to\pr-1' --require-claude
py -3 tools/verify/check_tree.py --repo 'C:\path\to\pr-2'
py -3 tools/verify/check_links.py --repo 'C:\path\to\pr-2'
py -3 tools/verify/run_contracts.py --repo 'C:\path\to\pr-2' --java-home 'C:\path\to\jdk-21'
```

`--require-claude`는 PR #1의 병합 전 후보처럼 `.claude/skills/` 진입점이 필수인 체크아웃을 명시적으로 검사할 때 사용한다. 이 옵션이 없어도 진입점 파일이 있으면 내용과 무시 규칙을 검사하고, 파일이 Git 무시 대상이 아니면 누락을 `FAIL`로 처리한다. PR #1 병합 전의 기준 커밋처럼 해당 경로가 없고 무시 대상이었던 체크아웃만 `SKIP`이었다. 현재 포크 `main`에는 PR #1의 진입점이 있어 일반 검사에서도 `PASS`가 요구된다. CI에서는 실행 중인 브랜치의 소스와 문서를 검사한다.

## 각 검사가 말해 주는 것

| 도구 | 자동으로 확인하는 것 | 확인하지 못하는 것 |
|---|---|---|
| `check_tree.py` | 현재 Java 파일과 README·코드 트리의 물리적 파일 목록, 이 문서의 도구 파일 목록 | 각 클래스의 책임이 문서 설명과 같은지 |
| `check_links.py` | 저장소 내부 Markdown 상대 링크와 `#L번호`의 존재 | 외부 웹페이지 상태, 인용한 주장의 진위 |
| `check_project_contract.py` | Stonecutter·CI 매트릭스·의존성 대상 일치, 스킬 위치·메타데이터·무시 규칙 | 각 Minecraft 버전의 실제 컴파일·실행 |
| `run_contracts.py` | Minecraft에 의존하지 않는 채널·시그널링 계약, 로컬 소켓의 루프백 바인드·대체 포트, 초대 코드 형식, 역할 조회 조정기의 동시 요청·시간 제한 | Fabric Mixins, 초대 코드의 예측 저항성 증명, 실제 HTTP 서명·재생 방지, 실게임 접속·입장 정책·역할 배지 표시, 외부 시그널링 서버 동작 |

위의 검사는 포크 `main`에 병합된 PR #1·#2의 스킬·연구 문서와 [순차 작업 01·02](work-guides/README.md)에 적용할 수 있다. PR #4의 작업 03에는 역할 조회 조정기 순수 Java 검사를 추가했다. 나머지 제안은 PLANNED다. 로컬 소켓 검사와 역할 조회 조정기 검사만으로 Minecraft 접속이나 서버 틱 지연 감소를 `PASS`로 표시하지 않는다. 역할 응답 서명 검증에는 nonce·시각 확인이 없어 과거의 정상 서명 응답 재생 가능성도 별도 과제로 남는다.

## 빌드와 실제 접속 기록

공유 Java 소스를 고친 PR은 프로젝트 스킬에 따라 최소 1.21.x와 26.x 대표 대상을 빌드한다. 릴리스 범위 주장은 기존 `.github/workflows/build.yml`의 17개 대상이 모두 통과한 결과를 사용한다. 컴파일과 위 도구를 통과해도 두 게임 인스턴스 사이의 P2P 연결은 별도로 관찰해야 한다.

03 역할 변경을 포함한 개발 체크아웃에서는 JDK 25·Gradle 9.7.1로 `:1.21:build`와 `:26.2:build`가 각각 성공했다(`--configure-on-demand --offline --no-daemon`). 두 대표 JAR의 `fabric.mod.json`은 각각 Minecraft `1.21`·Java `>=21`, Minecraft `26.2`·Java `>=25`를 요구하며 `InviteCodes.class`가 포함됐다. 03 소스 커밋 [`7542df6`](https://github.com/tjwlstj/kfcudp-instant-p2p/commit/7542df60e8b570d5ccff5ee237dad305dfbec87e)의 [PR CI](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36259045553)와 [push CI](https://github.com/tjwlstj/kfcudp-instant-p2p/actions/runs/36259041290)는 각각 17/17 대상 빌드에 성공했다. 이후 문서 변경 HEAD의 CI 결과로 이 실행을 대신하지 않는다. 두 클라이언트 연결과 사용 가능한 서명 역할 서비스의 응답을 통한 실제 정책 검증은 미실행이다.

런타임 확인이 필요한 변경에는 아래 항목을 PR 설명이나 별도 기록에 남긴다. 미실행 항목은 `미실행`으로 둔다.

| 항목 | 기록할 값 |
|---|---|
| 기준 | 테스트한 커밋 SHA, 방장·게스트 Minecraft/모드 버전, OS |
| 연결 | 초대 코드 또는 공개 방, 직결 또는 TURN, 접속 성공/실패와 소요 시간 |
| 수명 주기 | 첫 접속, 재접속, 강퇴·차단, 월드 종료, 재개설 결과 |
| 장애 | 시그널링 불가, 직결 실패 후 TURN, 네트워크 순단 후 복구 여부 |
| 증거 | 양쪽 로그의 시각과 관련 부분, 필요한 경우 패킷·서버 관찰 위치 |
| 판정 | 관찰한 결과, 기대 결과, 재현 단계, 미실행·불명확한 범위 |

PR #2에서 제안한 `servers`·`control` 중계 검증은 이 저장소에 없는 시그널링 서버 소스 또는 실제 서버 관찰이 필요하다. ICE 재시작과 버전 협상 역시 구현 후 방장·게스트 양쪽에서 확인해야 한다. AutoModpack 같은 추가 모드의 배포·두 번째 TCP 연결은 호환 게임과 P2P 모드가 먼저 실행된 상태에서 별도로 시험한다.
