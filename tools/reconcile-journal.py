from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = """    if (todayLog.length === 0 && result.status && result.since) {
      todayLog.push({
        type: result.status,
        ts: result.since,
        time: result.time || formatTime(result.since),
        hours: null
      });
    }

    saveData();
"""
new = """    const serverSinceMs = result.since ? new Date(result.since).getTime() : NaN;

    if (!result.status) {
      todayLog = [];
    } else if (Number.isFinite(serverSinceMs)) {
      // Server is the authority for the latest real punch. Remove local entries
      // that are newer than the server's confirmed status (e.g. deleted tests).
      todayLog = todayLog.filter(entry => {
        const entryMs = new Date(entry.ts).getTime();
        return !Number.isFinite(entryMs) || entryMs <= serverSinceMs + 1000;
      });

      const hasServerEntry = todayLog.some(entry => {
        const entryMs = new Date(entry.ts).getTime();
        return Number.isFinite(entryMs) &&
          Math.abs(entryMs - serverSinceMs) <= 1000 &&
          entry.type === result.status;
      });

      if (!hasServerEntry) {
        todayLog.push({
          type: result.status,
          ts: result.since,
          time: result.time || formatTime(result.since),
          hours: null
        });
      }
    }

    saveData();
"""
count = s.count(old)
if count != 1:
    raise SystemExit(f'Expected exactly one journal sync block, found {count}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
