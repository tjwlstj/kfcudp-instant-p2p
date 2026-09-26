package kfc.udp.client.webrtc;

import java.io.IOException;
import java.net.BindException;
import java.net.InetSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.security.SecureRandom;
import java.util.Objects;

/** Pure Java checks for invite-code generation and the guest TCP listener. */
public final class LocalSecurityCheck {
    private static int checks;
    private static int failures;

    private LocalSecurityCheck() {}

    public static void main(String[] args) {
        check("invite-code format and secure RNG seam", LocalSecurityCheck::inviteCodes);
        check("guest listener preferred loopback port", LocalSecurityCheck::preferredLoopbackPort);
        check("guest listener fallback when 25566 is occupied", LocalSecurityCheck::occupiedLoopbackPort);

        System.out.printf("Local security checks: %d passed, %d failed%n", checks - failures, failures);
        if (failures != 0) System.exit(1);
    }

    private static void inviteCodes() {
        String generated = InviteCodes.generate();
        eq(10, generated.length(), "invite-code length");
        for (char c : generated.toCharArray()) {
            truth("ABCDEFGHJKLMNPQRSTUVWXYZ23456789".indexOf(c) >= 0,
                    "invite-code alphabet");
        }

        SecureRandom boundaryRng = new SecureRandom() {
            private int index;

            @Override public int nextInt(int bound) {
                eq(32, bound, "32-symbol alphabet bound");
                return index++ % bound;
            }
        };
        eq("ABCDEFGHJK", InviteCodes.generate(boundaryRng), "injected RNG sequence");
        eq("9999999999", InviteCodes.generate(new SecureRandom() {
            @Override public int nextInt(int bound) { return bound - 1; }
        }), "highest alphabet index");
    }

    private static void preferredLoopbackPort() {
        try (ServerSocketChannel reservation = ServerSocketChannel.open()) {
            reservation.bind(new InetSocketAddress("127.0.0.1", 0));
            int port = reservation.socket().getLocalPort();
            reservation.close();
            try (ServerSocketChannel listener = LocalGuestListener.open(port)) {
                eq(port, listener.socket().getLocalPort(), "preferred port is retained");
                eq("127.0.0.1", ((InetSocketAddress) listener.getLocalAddress())
                        .getAddress().getHostAddress(), "listener address");
            }
        } catch (IOException failure) {
            throw new AssertionError("preferred loopback bind failed", failure);
        }
    }

    private static void occupiedLoopbackPort() {
        try (ServerSocketChannel blocker = ServerSocketChannel.open()) {
            try {
                blocker.bind(new InetSocketAddress("127.0.0.1", 25566));
            } catch (BindException alreadyOccupied) {
                // Another process already occupies the preferred loopback port.
            }
            try (ServerSocketChannel listener = LocalGuestListener.open(25566)) {
                int fallbackPort = listener.socket().getLocalPort();
                truth(fallbackPort > 0 && fallbackPort != 25566, "ephemeral fallback port");
                eq("127.0.0.1", ((InetSocketAddress) listener.getLocalAddress())
                        .getAddress().getHostAddress(), "fallback listener address");
                try (SocketChannel client = SocketChannel.open(
                        new InetSocketAddress("127.0.0.1", fallbackPort));
                     SocketChannel accepted = listener.accept()) {
                    truth(client.isConnected() && accepted.isConnected(),
                            "Minecraft loopback route can connect");
                }
            }
        } catch (IOException failure) {
            throw new AssertionError("occupied loopback fallback failed", failure);
        }
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

    private static void truth(boolean value, String context) {
        if (!value) throw new AssertionError(context + ": expected true");
    }
}
