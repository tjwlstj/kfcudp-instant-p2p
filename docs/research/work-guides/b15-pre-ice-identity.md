# B15 · ICE 전에 사용자 신원 확인

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** 현재 [`P2PBanManager`](../../../src/client/java/kfc/udp/client/webrtc/P2PBanManager.java)의 입장 판정은 Minecraft LOGIN 단계다. 그 전 ICE 후보와 TURN 자원이 쓰인다.
- **제안·선행:** B12 기능 협상, 서버 API 이용 조건과 호출 한도를 확인한다. 페어 세션에서 세션 서버 `join`/`hasJoined`의 최소 증명 교환을 설계하되 UUID 신뢰와 재생 방지를 먼저 검토한다.
- **검증·되돌리기:** 위조·재전송·차단·화이트리스트 경로의 정적·계약 시험, 양쪽 빌드, 실제 인증 서비스/오프라인 환경의 입장 시험이 필요하다. 교차 버전에는 기존 LOGIN 판정을 계속 사용한다.

## 관찰성과 향후 기능
