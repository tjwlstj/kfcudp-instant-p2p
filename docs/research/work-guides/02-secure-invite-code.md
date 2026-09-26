# 02 · 초대 코드에 보안 난수 사용

**상태: PARTIAL.** 초대 코드 생성 변경과 순수 Java 형식 검사를 구현했고 1.21·26.2 대표 빌드가 성공했다. 실제 Minecraft 코드 입장은 아직 확인하지 않았다. 초대 코드 길이와 문자 집합은 보존했다.

- **기존 소스 확인:** 기준 커밋 `1880590`의 [`KfcudpClient.generateCode`](../../../src/client/java/kfc/udp/client/KfcudpClient.java)는 `java.util.Random`으로 32자 문자 집합에서 10자를 골랐다. 공개 방 코드는 목록에 노출된다.
- **추정:** 공개된 코드로 같은 실행의 비공개 코드를 실제 복원할 수 있는지는 재현하지 않았다. 방 코드가 비공개 방의 실질적인 접근 비밀이라는 설계 판단이다.
- **현재 구현:** [`InviteCodes`](../../../src/client/java/kfc/udp/client/webrtc/InviteCodes.java)가 공유 `SecureRandom`으로 기존 32자 집합에서 10자를 고르고, `KfcudpClient.generateCode`가 이를 호출한다. 코드 생성 외 다른 `Random` 사용처는 이 작업 범위에 포함하지 않았다. 방 코드의 전송 형식은 바꾸지 않았다.
- **순수 Java 검사:** [`LocalSecurityCheck`](../../../tools/tests/java/kfc/udp/client/webrtc/LocalSecurityCheck.java)가 생성기의 타입 경계와 길이·허용 문자 집합을 확인한다. 샘플의 중복 여부나 형식 검사는 난수의 예측 저항성을 증명하지 않는다.
- **대표 빌드·JAR 확인:** 현재 변경을 포함한 개발 체크아웃에서 JDK 25·Gradle 9.7.1의 `:1.21:build`와 `:26.2:build`가 `--configure-on-demand --offline --no-daemon`으로 성공했다. 두 JAR에 `InviteCodes.class`가 포함됐고, `fabric.mod.json`의 Minecraft 대상은 각각 `1.21`·`26.2`, Java 하한은 각각 `21`·`25`다. [공통 기록](README.md)에 시간과 경고를 적었다. 현재 변경의 전체 17개 대상 빌드는 미실행이다.
- **실행 게이트:** 비공개 방을 두 번 열어 코드를 이용한 게스트 접속, 공개 방 표시, 방을 닫은 뒤 재개설을 확인한다.
- **되돌리기:** `KfcudpClient`의 위임과 `InviteCodes`를 한 변경 단위로 되돌린다. 이전 코드 형식과 호환성은 유지되어야 한다.
