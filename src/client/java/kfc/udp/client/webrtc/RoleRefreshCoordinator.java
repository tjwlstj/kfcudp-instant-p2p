package kfc.udp.client.webrtc;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.function.Supplier;

/**
 * Shares one in-flight roles fetch between logins. A completed fetch is never
 * reused: a full room must get a new verified answer before granting a perk.
 * The fetch itself does not depend on Minecraft, so its timing can be tested.
 */
final class RoleRefreshCoordinator {

    record Result(boolean verified, boolean changed) {
        static Result unavailable() { return new Result(false, false); }
    }

    private final Executor executor;
    private final Supplier<Result> fetch;
    private Flight inFlight;

    /** One notification per fetch; a newer room may replace a stale room callback. */
    private static final class Flight {
        final CompletableFuture<Result> result;
        Runnable onChanged;

        Flight(CompletableFuture<Result> result, Runnable onChanged) {
            this.result = result;
            this.onChanged = onChanged;
        }
    }

    RoleRefreshCoordinator(Executor executor, Supplier<Result> fetch) {
        this.executor = executor;
        this.fetch = fetch;
    }

    synchronized CompletableFuture<Result> request(Runnable onChanged) {
        if (inFlight == null || inFlight.result.isDone()) {
            Flight flight = new Flight(CompletableFuture.supplyAsync(fetch, executor), onChanged);
            inFlight = flight;
            // Even if the fetch finishes before this registration, the callback
            // runs on the background executor, never inline on the login thread.
            flight.result.thenAcceptAsync(result -> notifyChanged(flight, result), executor);
        } else if (onChanged != null) {
            // The room that is active now must receive the eventual update.
            // This also lets a login add a callback to startHost's null callback.
            inFlight.onChanged = onChanged;
        }
        return inFlight.result;
    }

    private void notifyChanged(Flight flight, Result result) {
        if (!result.verified() || !result.changed()) return;
        Runnable onChanged;
        synchronized (this) {
            onChanged = flight.onChanged;
        }
        if (onChanged != null) onChanged.run();
    }

    Result await(long timeoutMs, Runnable onChanged) throws Exception {
        try {
            return request(onChanged).get(timeoutMs, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            // Leave the request running: its onChanged callback still repairs
            // badges and room state if the verified response arrives later.
            return Result.unavailable();
        }
    }
}
