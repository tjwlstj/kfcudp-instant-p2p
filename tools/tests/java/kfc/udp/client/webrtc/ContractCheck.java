package kfc.udp.client.webrtc;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;

/**
 * Contract checks for the Minecraft-independent channel and signaling code.
 * These assertions describe user-visible channel behavior and the existing
 * signaling wire fields. They do not claim to exercise a signaling server,
 * WebRTC peer, or the complete JSON grammar.
 */
final class ContractCheck {
    private static int checks;
    private static int failures;

    public static void main(String[] args) {
        check("channel input normalization and limits", ContractCheck::channelInput);
        check("channel OR and AND visibility", ContractCheck::channelVisibility);
        check("description and candidate wire fields", ContractCheck::descriptionAndCandidate);
        check("public room update wire fields", ContractCheck::roomUpdate);
        check("control and delta membership frames", ContractCheck::membershipFrames);
        check("ICE server list frame", ContractCheck::serverList);

        System.out.printf("Contract checks: %d passed, %d failed%n", checks - failures, failures);
        if (failures != 0) System.exit(1);
    }

    private static void channelInput() {
        eq(List.of("normal"), ChannelRules.parseChannels(null), "empty channel default");
        eq(List.of("Games"), ChannelRules.parseChannels(" Games,  "), "trailing empty field");
        eq(List.of("Games", "normal", "Redstone"),
                ChannelRules.parseChannels(" Games, ,Redstone,games"), "interior default and duplicate");
        eq(List.of("a", "b", "c", "d", "e"),
                ChannelRules.parseChannels("a,b,c,d,e,f"), "five channel limit");
        eq(List.of("abcdefghijklmnopqrstuvwx"),
                ChannelRules.parseChannels("abcdefghijklmnopqrstuvwxYZ"), "24 character limit");
    }

    private static void channelVisibility() {
        truth(ChannelRules.roomVisible("games,builders", false,
                List.of("BUILDERS", "music"), false), "OR overlap ignores case");
        falsity(ChannelRules.roomVisible("games,builders", false,
                List.of("music"), false), "unrelated channels stay hidden");
        truth(ChannelRules.roomVisible("build,redstone", true,
                List.of("REDSTONE", "BUILD"), true), "AND group ignores order and case");
        falsity(ChannelRules.roomVisible("build,redstone", true,
                List.of("build", "redstone"), false), "host AND does not match visitor OR");
        falsity(ChannelRules.roomVisible("build,redstone", false,
                List.of("build", "redstone"), true), "host OR does not match visitor AND");
    }

    private static void descriptionAndCandidate() {
        eq("{}", VillasMsg.hello(), "first signaling message");

        String sdp = "v=0\r\na=fmtp:1 \"profile\"\r\n";
        String description = VillasMsg.description("offer", sdp);
        truth(description.contains("\"spd\""), "server spelling of SDP field");
        falsity(description.contains("\"sdp\""), "alternate SDP spelling on wire");
        String body = VillasMsg.object(description, "description");
        eq("offer", VillasMsg.field(body, "type"), "description type");
        eq(sdp, VillasMsg.field(body, "spd"), "SDP line endings and quotes");

        String candidate = VillasMsg.candidate("candidate:1 1 udp 42 192.0.2.10 4000 typ host", "0");
        String candidateBody = VillasMsg.object(candidate, "candidate");
        eq("candidate:1 1 udp 42 192.0.2.10 4000 typ host",
                VillasMsg.field(candidateBody, "spd"), "ICE candidate wire field");
        eq("0", VillasMsg.field(candidateBody, "mid"), "ICE media identifier");
    }

    private static void roomUpdate() {
        String frame = VillasMsg.roomUpdate("ABC123", "길드 \"A\"", "host", "redstone,build", true,
                2, 8, "1.2.3", "test-uuid", "a,b", 17L, 123456789L);
        String room = VillasMsg.object(frame, "room_update");
        eq("ABC123", VillasMsg.field(room, "code"), "room code");
        eq("길드 \"A\"", VillasMsg.field(room, "title"), "room title quotes");
        eq("redstone,build", VillasMsg.field(room, "channel"), "room channels");
        eq("true", VillasMsg.field(room, "channel_and"), "AND flag");
        eq("2", VillasMsg.field(room, "current"), "current player count");
        eq("8", VillasMsg.field(room, "max"), "maximum player count");
        eq("1.2.3", VillasMsg.field(room, "version"), "mod version");
        eq("test-uuid", VillasMsg.field(room, "host_uuid"), "host identity field");
        eq("a,b", VillasMsg.field(room, "banned_hashes"), "advertised block hashes");
        eq("17", VillasMsg.field(room, "host_rtt_ms"), "host RTT");
        eq("123456789", VillasMsg.field(room, "opened_at_ms"), "room creation time");
    }

    private static void membershipFrames() {
        String control = "{\"control\":{\"peer_id\":17,\"peers\":["
                + "{\"name\":\"jrABC\",\"id\":4,\"remote\":\"192.0.2.1:1234\"},"
                + "{\"name\":\"hdXYZ\",\"id\":5}]}}";
        List<String[]> peers = VillasMsg.peers(control);
        eq(2, peers.size(), "control peer count");
        fields(new String[]{"jrABC", "192.0.2.1:1234"}, peers.get(0), "connected peer");
        fields(new String[]{"hdXYZ", null}, peers.get(1), "peer without remote address");

        String fullDelta = "{\"delta\":{\"full\":true,\"joined\":["
                + "{\"name\":\"r-room\",\"remote\":\"198.51.100.4:2345\"}],\"left\":[\"old-room\"]}}";
        truth(VillasMsg.isFullDelta(fullDelta), "full delta flag");
        List<String[]> joined = VillasMsg.joined(fullDelta);
        eq(1, joined.size(), "joined count");
        fields(new String[]{"r-room", "198.51.100.4:2345"}, joined.get(0), "joined peer");
        eq(List.of("old-room"), VillasMsg.left(fullDelta), "departed peer");
        falsity(VillasMsg.isFullDelta("{\"delta\":{\"full\":false,\"joined\":[]}}"),
                "incremental delta flag");
    }

    private static void serverList() {
        String frame = "{\"servers\":["
                + "{\"url\":\"stun:stun.example.test\"},"
                + "{\"url\":\"turn:turn.example.test\",\"user\":\"alice\",\"pass\":\"secret\"}]}";
        List<String[]> servers = VillasMsg.servers(frame);
        eq(2, servers.size(), "ICE server count");
        fields(new String[]{"stun:stun.example.test", null, null}, servers.get(0), "STUN server");
        fields(new String[]{"turn:turn.example.test", "alice", "secret"}, servers.get(1), "TURN server");
    }

    private static void check(String name, Runnable test) {
        checks++;
        try {
            test.run();
            System.out.println("PASS " + name);
        } catch (AssertionError | RuntimeException failure) {
            failures++;
            System.err.println("FAIL " + name + ": " + failure.getMessage());
        }
    }

    private static void eq(Object expected, Object actual, String context) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError(context + ": expected <" + expected + "> but was <" + actual + ">");
        }
    }

    private static void fields(String[] expected, String[] actual, String context) {
        if (!Arrays.equals(expected, actual)) {
            throw new AssertionError(context + ": expected " + Arrays.toString(expected)
                    + " but was " + Arrays.toString(actual));
        }
    }

    private static void truth(boolean value, String context) {
        if (!value) throw new AssertionError(context + ": expected true");
    }

    private static void falsity(boolean value, String context) {
        if (value) throw new AssertionError(context + ": expected false");
    }

    private ContractCheck() {}
}
