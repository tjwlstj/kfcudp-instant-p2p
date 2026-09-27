package kfc.udp.client.webrtc;

/**
 * Reproduces edge cases of VillasMsg's hand-written JSON reader (review R01, R06).
 *
 * <p>Compile it together with the fork's VillasMsg into a temporary directory:
 * <pre>
 * javac -encoding UTF-8 -d OUT src/client/java/kfc/udp/client/webrtc/VillasMsg.java \
 *       docs/review/2026-09-27/evidence/VillasMsgProbe.java
 * java -cp OUT kfc.udp.client.webrtc.VillasMsgProbe
 * </pre>
 * Each line prints the parsed value next to the value the sender wrote. A line
 * whose two values differ is a parser defect, not a signaling-server behaviour.
 */
public final class VillasMsgProbe {
    private VillasMsgProbe() {}

    public static void main(String[] args) {
        String backslash = "C:" + (char) 92;

        // R06: a title ending in a backslash, produced by this mod's own builder.
        String f1 = VillasMsg.roomUpdate("ABCDEFGHJK", backslash, "nick", "normal", false,
                1, 8, "1.21", "u", "", 10, 1);
        String r1 = VillasMsg.object(f1, "room_update");
        report("R06 title ending in backslash", backslash, VillasMsg.field(r1, "title"));

        // R06: unicode and tab escapes as emitted by common JSON encoders.
        String f2 = "{\"room_update\":{\"code\":\"X\",\"title\":\"A " + (char) 92 + "u0026 B"
                + (char) 92 + "tC\"}}";
        report("R06 unicode and tab escapes", "A & B\tC",
                VillasMsg.field(VillasMsg.object(f2, "room_update"), "title"));

        // R01: a closing brace inside the title truncates the room_update object,
        // so every field written after the title disappears on the receiving side.
        String f3 = VillasMsg.roomUpdate("K", "a}b", "n", "redstone", false,
                1, 8, "1.21", "host-uuid", "hash1,hash2", 1, 1);
        String r3 = VillasMsg.object(f3, "room_update");
        report("R01 nickname after '}' title", "n", VillasMsg.field(r3, "nickname"));
        report("R01 version after '}' title", "1.21", VillasMsg.field(r3, "version"));
        report("R01 host_uuid after '}' title", "host-uuid", VillasMsg.field(r3, "host_uuid"));
        report("R01 banned_hashes after '}' title", "hash1,hash2", VillasMsg.field(r3, "banned_hashes"));
    }

    private static void report(String name, String sent, String parsed) {
        String verdict = sent.equals(parsed) ? "OK  " : "DIFF";
        System.out.println(verdict + " " + name + ": sent=[" + sent + "] parsed=[" + parsed + "]");
    }
}
