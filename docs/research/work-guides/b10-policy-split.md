# B10 · `P2PBanManager` 책임 분리

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`P2PBanManager`](../../../src/client/java/kfc/udp/client/webrtc/P2PBanManager.java)는 저장·명령·터널 매핑·연결 종류·접속자 해시·로그인 판정을 함께 맡는다.
- **선행·최소 변경:** 먼저 포트→IP 매핑만 내부 클래스로 추출하고 기존 공개 메서드가 위임하게 한다. 입장 판정은 마지막에 분리한다.
- **검증·되돌리기:** IP 매핑과 정책 판단을 혼동하지 않는지 정적 검토하고 빌드·차단/해제/재접속을 실게임 확인한다. 작은 추출 단위별로 원복한다.
