# B09 · `VillasMsg` 파서에 Gson 사용

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인:** [`VillasMsg.field`](../../../src/client/java/kfc/udp/client/webrtc/VillasMsg.java)는 일부 escape만 해제하고 후행 백슬래시 처리에 한계가 있다. Gson은 다른 설정 코드에서 이미 사용한다.
- **선행·최소 변경:** 기존 실제 메시지와 `\uXXXX`, `\t`, 후행 백슬래시를 계약 fixture로 고정한 뒤 **파싱만** 교체한다.
- **검증·되돌리기:** `description.spd`, `candidate.spd`, delta 교체와 알 수 없는 필드 동작을 정적·계약 시험하고 빌드·원본 모드 접속을 확인한다. 생성 JSON은 유지하며 파서만 원복할 수 있게 둔다.
