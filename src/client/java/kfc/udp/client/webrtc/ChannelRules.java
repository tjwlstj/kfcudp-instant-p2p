package kfc.udp.client.webrtc;

import java.util.ArrayList;
import java.util.List;

/** Pure channel parsing and matching rules shared by room announcements and the room list. */
final class ChannelRules {
    static final int MAX_CHANNELS = 5;
    static final int MAX_CHANNEL_LENGTH = 24;

    /** An untypeable separator keeps an AND group distinct from a user entered channel name. */
    private static final char AND_SEPARATOR = '\u001F';
    private static final String DEFAULT_CHANNEL = "normal";

    private ChannelRules() {}

    static List<String> parseChannels(String text) {
        List<String> out = new ArrayList<>();
        String[] parts = (text == null ? "" : text).split(",", -1);
        int n = parts.length;
        if (n > 1 && parts[n - 1].isBlank()) n--;
        for (int i = 0; i < n; i++) {
            String t = parts[i].trim();
            if (t.isEmpty()) t = DEFAULT_CHANNEL;
            if (t.length() > MAX_CHANNEL_LENGTH) t = t.substring(0, MAX_CHANNEL_LENGTH);
            if (out.stream().anyMatch(t::equalsIgnoreCase)) continue;
            if (out.size() >= MAX_CHANNELS) break;
            out.add(t);
        }
        return List.copyOf(out);
    }

    static List<String> effectiveChannels(List<String> channels, boolean and) {
        if (!and || channels.size() <= 1) return channels;
        return List.of(channels.stream().map(c -> c.toLowerCase(java.util.Locale.ROOT)).sorted()
                .collect(java.util.stream.Collectors.joining(String.valueOf(AND_SEPARATOR))));
    }

    static boolean roomVisible(String hostChannels, boolean hostAnd, List<String> mine, boolean mineAnd) {
        List<String> host = effectiveChannels(parseChannels(hostChannels), hostAnd);
        List<String> me = effectiveChannels(mine, mineAnd);
        return host.stream().anyMatch(h -> me.stream().anyMatch(h::equalsIgnoreCase));
    }
}
