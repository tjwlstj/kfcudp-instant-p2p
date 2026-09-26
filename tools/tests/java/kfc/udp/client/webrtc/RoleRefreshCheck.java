package kfc.udp.client.webrtc;

import java.util.ArrayDeque;
import java.util.Queue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

/** Standalone, deterministic timing checks for the login role refresh coordinator. */
public final class RoleRefreshCheck {
    private RoleRefreshCheck() {}

    public static void main(String[] args) throws Exception {
        Queue<Runnable> work = new ArrayDeque<>();
        Executor delayed = work::add;
        AtomicInteger calls = new AtomicInteger();
        AtomicInteger oldRoomChanges = new AtomicInteger();
        AtomicInteger activeRoomChanges = new AtomicInteger();
        AtomicReference<RoleRefreshCoordinator.Result> next = new AtomicReference<>(
                new RoleRefreshCoordinator.Result(true, true));
        RoleRefreshCoordinator coordinator = new RoleRefreshCoordinator(delayed, () -> {
            calls.incrementAndGet();
            return next.get();
        });

        // One fetch and one notification, even when many logins attach callbacks.
        // The latest callback represents the currently active room.
        var first = coordinator.request(oldRoomChanges::incrementAndGet);
        var second = coordinator.request(activeRoomChanges::incrementAndGet);
        check(first == second && work.size() == 1, "concurrent logins must share in-flight fetch");
        check(calls.get() == 0, "non-full request must return before network work");
        work.remove().run();
        check(first.get().verified() && calls.get() == 1 && oldRoomChanges.get() == 0
                        && activeRoomChanges.get() == 0 && work.size() == 1,
                "fetch completion must enqueue rather than run a callback inline");
        work.remove().run();
        check(oldRoomChanges.get() == 0 && activeRoomChanges.get() == 1,
                "only the current room callback runs for a shared fetch");

        // startHost can start a fetch with no callback; login adds one later.
        var startedWithoutCallback = coordinator.request(null);
        var registeredLate = coordinator.request(activeRoomChanges::incrementAndGet);
        check(startedWithoutCallback == registeredLate && work.size() == 1,
                "late callback registration must reuse the running fetch");
        work.remove().run();
        check(activeRoomChanges.get() == 1, "late callback must remain asynchronous");
        work.remove().run();
        check(activeRoomChanges.get() == 2, "late registered callback must fire");

        // A completed result cannot authorize a later login. The pending
        // notification belongs only to its original flight, even if a new one
        // is requested before that notification is dispatched.
        var oldFlight = coordinator.request(oldRoomChanges::incrementAndGet);
        work.remove().run();
        check(oldFlight.isDone() && work.size() == 1, "old fetch completed before callback delivery");
        var newFlight = coordinator.request(activeRoomChanges::incrementAndGet);
        check(newFlight != oldFlight && work.size() == 2,
                "login after fetch completion must schedule a new fetch");
        work.remove().run();
        check(oldRoomChanges.get() == 1 && activeRoomChanges.get() == 2,
                "old flight notification must not capture the new flight callback");
        work.remove().run();
        check(activeRoomChanges.get() == 2, "new flight callback must also be deferred");
        work.remove().run();
        check(activeRoomChanges.get() == 3, "new flight must notify its own room");

        // A failed or invalid response never notifies the room or grants bypass.
        next.set(RoleRefreshCoordinator.Result.unavailable());
        var failed = coordinator.request(activeRoomChanges::incrementAndGet);
        check(failed != newFlight && work.size() == 1, "a completed result must not authorize a later login");
        work.remove().run();
        work.remove().run();
        check(!failed.get().verified() && activeRoomChanges.get() == 3,
                "unverified response cannot grant a perk or trigger a badge update");

        // Timeout leaves background work alive for late UI repair, but grants no bypass.
        next.set(new RoleRefreshCoordinator.Result(true, true));
        var timedOut = coordinator.await(10, activeRoomChanges::incrementAndGet);
        check(!timedOut.verified() && activeRoomChanges.get() == 3 && work.size() == 1,
                "full-room wait must be bounded and fail closed");
        work.remove().run();
        check(activeRoomChanges.get() == 3, "late result must not notify inline");
        work.remove().run();
        check(activeRoomChanges.get() == 4 && calls.get() == 6,
                "late verified change must still notify the UI callback");

        // An unchanged signed response is valid for the capacity decision.
        next.set(new RoleRefreshCoordinator.Result(true, false));
        var unchanged = coordinator.request(activeRoomChanges::incrementAndGet);
        work.remove().run();
        work.remove().run();
        check(unchanged.get().verified() && activeRoomChanges.get() == 4,
                "verified unchanged response is usable without redundant badge update");
        checkFastCompletionAndBackgroundDispatch();
        System.out.println("PASS role refresh: coalesced notifications, late registration,"
                + " flight race, failure, timeout, late callback, unchanged, dispatch");
    }

    private static void checkFastCompletionAndBackgroundDispatch() throws Exception {
        // With an immediate executor the fetch can finish before the completion
        // handler is attached. Its first non-null callback must still be seen.
        AtomicInteger immediateChanges = new AtomicInteger();
        RoleRefreshCoordinator immediate = new RoleRefreshCoordinator(Runnable::run,
                () -> new RoleRefreshCoordinator.Result(true, true));
        check(immediate.request(immediateChanges::incrementAndGet).get().verified()
                        && immediateChanges.get() == 1,
                "first callback must survive immediate fetch completion");

        // Production supplies a dedicated background executor. Assert that the
        // completion callback does not run on the requesting login thread.
        ExecutorService background = Executors.newSingleThreadExecutor();
        try {
            Thread loginThread = Thread.currentThread();
            AtomicReference<Thread> callbackThread = new AtomicReference<>();
            CountDownLatch delivered = new CountDownLatch(1);
            RoleRefreshCoordinator coordinator = new RoleRefreshCoordinator(background,
                    () -> new RoleRefreshCoordinator.Result(true, true));
            coordinator.request(() -> {
                callbackThread.set(Thread.currentThread());
                delivered.countDown();
            });
            check(delivered.await(5, TimeUnit.SECONDS) && callbackThread.get() != loginThread,
                    "production background executor must keep callback off login thread");
        } finally {
            background.shutdownNow();
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
