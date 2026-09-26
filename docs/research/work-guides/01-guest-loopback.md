# 01 · 게스트 로컬 TCP를 루프백에 바인드

**상태: PARTIAL.** 게스트의 로컬 TCP 리스너 변경과 순수 Java 소켓 검사를 구현했고 1.21·26.2 대표 빌드가 성공했다. 실제 Minecraft 연결은 아직 확인하지 않았다. 상대 피어의 전송 형식은 바꾸지 않았다.

- **기존 소스 확인:** 기준 커밋 `1880590`의 [`WebRtcClient.start`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)는 포트 번호만 지정한 `InetSocketAddress`로 리스너를 열고, `WebRtcBridge.findFreePort`가 별도 소켓으로 빈 포트를 찾았다. 게임은 `127.0.0.1`에 접속한다.
- **추정:** LAN의 다른 장치가 먼저 연결하거나 Windows 방화벽 창이 뜰 수 있다는 것은 실험으로 확인하지 않았다.
- **현재 구현:** [`LocalGuestListener.open`](../../../src/client/java/kfc/udp/client/webrtc/LocalGuestListener.java)가 기본 포트 25566을 `127.0.0.1`에 직접 바인드하고, 사용 중이면 OS가 고른 대체 포트를 같은 주소에 바인드한다. 별도 빈 포트 탐색과 그 사이의 경쟁 구간을 없앴다. [`WebRtcClient`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcClient.java)가 리스너를 소유하고 실제 바인드 포트를 [`WebRtcBridge`](../../../src/client/java/kfc/udp/client/webrtc/WebRtcBridge.java)에 전달한다. 시작 실패 시 소켓을 닫는다.
- **순수 Java 검사:** [`LocalSecurityCheck`](../../../tools/tests/java/kfc/udp/client/webrtc/LocalSecurityCheck.java)가 기본 포트 루프백 바인드와 25566 사용 중 대체 포트 경로를 실제 로컬 소켓으로 검사한다. 이 검사만으로 Minecraft 믹스인, 방장과의 WebRTC 통신, 다른 장치의 접근 차단을 입증하지 않는다.
- **대표 빌드 확인:** 현재 변경을 포함한 개발 체크아웃에서 JDK 25·Gradle 9.7.1의 `:1.21:build`와 `:26.2:build`가 `--configure-on-demand --offline --no-daemon`으로 성공했다. [공통 기록](README.md)에 시간과 경고를 적었다. 이 로컬 체크아웃에서는 전체 17개 대상 빌드를 실행하지 않았으므로 PR CI 결과를 별도로 확인한다.
- **실행 게이트:** 게스트가 정상 입장하고 재접속한다. 같은 호스트에서 `127.0.0.1:포트`는 접속되고 LAN 주소의 같은 포트는 접속되지 않는지 확인한다. 기본 포트 사용 중의 대체 포트, 초대 코드·공개 방·TURN 경로를 각각 확인한다.
- **되돌리기:** `LocalGuestListener` 사용과 실제 포트 전달을 한 변경 단위로 되돌린다. 특정 환경에서 IPv4 루프백 사용 불가가 확인되면 배포 전에 주소 선택 정책을 다시 정한다.
