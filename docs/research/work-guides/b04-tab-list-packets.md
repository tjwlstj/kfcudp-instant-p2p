# B04 · 탭 목록 갱신 N² 패킷 축소

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`KfcudpClient.kfcudp$refreshTabList`](../../../src/client/java/kfc/udp/client/KfcudpClient.java)는 플레이어마다 전원 대상 패킷을 보낸다.
- **선행·최소 변경:** 현행 수신 의미와 순서를 기록한 뒤 전체 목록 패킷 한 번으로 모은다.
- **검증·되돌리기:** 플레이어 0/1/여러 명과 역할 변경 시 목록을 정적 검토·빌드·실게임 확인하고, 패킷 수를 세어 비교한다. 누락이 있으면 전송 루프를 원복한다.

## 공개 로비와 시그널링 확장
