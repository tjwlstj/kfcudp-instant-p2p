# B01 · WebRTC 콜백 대기와 게스트별 factory

**상태: PLANNED.** [원래 조사](../feature-role-optimization.md)에서 분리한 독립 작업이다. [공통 검증 규칙](README.md)을 적용한다.

- **확인·추정:** [`BatchPipe`](../../../src/client/java/kfc/udp/client/webrtc/BatchPipe.java)는 writer 큐가 차면 콜백에서 반복 대기한다. [`WebRtcHost`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcHost.java)는 factory를 공유한다. 다른 게스트 콜백까지 지연된다는 것은 미측정이다.
- **선행·최소 변경:** 우선 콜백 대기 시간과 게스트별 영향만 계측한다. 교차 지연이 재현될 때 게스트별 factory 격리를 별도 변경한다.
- **검증·되돌리기:** 정적 검토는 콜백 스레드·factory 수명을, 빌드는 공유 대상 둘을, 실행은 느린 한 게스트와 정상 게스트의 RTT·CPU·네이티브 스레드를 비교한다. 비용이 크거나 효과가 없으면 계측만 남기고 격리는 원복한다.
