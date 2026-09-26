package kfc.udp.client.webrtc;

import java.io.IOException;
import java.net.BindException;
import java.net.InetSocketAddress;
import java.nio.channels.ServerSocketChannel;

/** Owns the guest Minecraft TCP listener on the IPv4 loopback interface. */
final class LocalGuestListener {
    private static final String LOOPBACK = "127.0.0.1";

    private LocalGuestListener() {}

    /**
     * Bind the preferred port, or let the OS choose one if that port is busy.
     * The returned channel already owns the port, so no probe/bind race exists.
     */
    static ServerSocketChannel open(int preferredPort) throws IOException {
        if (preferredPort < 1 || preferredPort > 65_535) {
            throw new IllegalArgumentException("preferredPort must be between 1 and 65535");
        }
        try {
            return bind(preferredPort);
        } catch (BindException busy) {
            return bind(0);
        }
    }

    private static ServerSocketChannel bind(int port) throws IOException {
        ServerSocketChannel channel = ServerSocketChannel.open();
        try {
            channel.bind(new InetSocketAddress(LOOPBACK, port));
            return channel;
        } catch (IOException | RuntimeException failure) {
            try { channel.close(); } catch (IOException closeFailure) { failure.addSuppressed(closeFailure); }
            throw failure;
        }
    }
}
