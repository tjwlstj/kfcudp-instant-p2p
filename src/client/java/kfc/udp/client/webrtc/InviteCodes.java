package kfc.udp.client.webrtc;

import java.security.SecureRandom;
import java.util.Objects;

/** Generates the existing ten-character invite-code format with a secure RNG. */
public final class InviteCodes {
    private static final String CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    private static final int CODE_LENGTH = 10;
    private static final SecureRandom RANDOM = new SecureRandom();

    private InviteCodes() {}

    public static String generate() {
        return generate(RANDOM);
    }

    // Package-private injection point for the pure Java contract harness.
    static String generate(SecureRandom random) {
        Objects.requireNonNull(random, "random");
        StringBuilder code = new StringBuilder(CODE_LENGTH);
        for (int i = 0; i < CODE_LENGTH; i++) {
            code.append(CODE_CHARS.charAt(random.nextInt(CODE_CHARS.length())));
        }
        return code.toString();
    }
}
