# B13 · 공개 방 정보 위조 방지

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인·추정:** [`PublicRoomBrowser`](../../../src/client/java/kfc/udp/client/webrtc/PublicRoomBrowser.java)는 본문의 `code`로 정보를 갱신한다. 다른 peer가 이를 덮을 수 있는지는 서버 중계 방식에 달렸다.
- **선행·최소 변경:** [05 발신자 조사](05-signaling-provenance.md) 후 서버에서 발신 peer를 붙이고 `code` 소유자와 대조하는 방식을 먼저 검토한다. 서명 키는 서버 변경이 불가할 때의 대안이다.
- **검증·되돌리기:** 서버 출처 확인·정상 방 갱신·가짜 peer 격리를 정적·서버 시험하고 공개 로비 실행으로 확인한다. 구버전 서버와 호환 경로를 두고 전환한다.
