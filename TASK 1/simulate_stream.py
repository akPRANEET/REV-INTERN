
import os
import time
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import logging
import signal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def analyze_history(df):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    cols = [c for c in df.columns if c != 'timestamp']
    stats = {}
    diffs = {}
    hourly_profile = {}

    for c in cols:
        series = df[c]
        diff = series.diff().dropna()
        stats[c] = {
            'last_value': float(series.iloc[-1]),
            'mean': float(series.mean()),
            'std': float(series.std()) if series.std() is not None else 0.0,
            'diff_mean': float(diff.mean()) if not diff.empty else 0.0,
            'diff_std': float(diff.std()) if not diff.empty else 0.0
        }
        diffs[c] = diff
        df['hour'] = df['timestamp'].dt.hour
        hourly_profile[c] = df.groupby('hour')[c].mean().to_dict()

    median_interval_seconds = float(df['timestamp'].diff().median().total_seconds())
    meta = {
        'last_timestamp': df['timestamp'].iloc[-1],
        'median_interval_seconds': median_interval_seconds,
        'cols': cols
    }
    return stats, hourly_profile, meta

def append_row_csv(path, row):
    header = not os.path.exists(path)
    pd.DataFrame([row]).to_csv(path, mode='a', header=header, index=False)

class GracefulExit(SystemExit):
    pass

def register_signal_handlers():
    def handler(signum, frame):
        raise GracefulExit()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

def generate_next_values(last_vals, stats, hourly_profile, last_ts, next_ts, method):
    elapsed = (next_ts - last_ts).total_seconds()
    out = {}
    for c, last_val in last_vals.items():
        s = stats[c]
        trend_per_sec = 0.0
        if s['diff_mean'] != 0 and elapsed > 0:
            trend_per_sec = s['diff_mean'] / max(1.0, elapsed)
        trend = trend_per_sec * elapsed

        hour = next_ts.hour
        seasonal_mean = hourly_profile.get(c, {}).get(hour, s['mean'])

        if method == 'trend_seasonal':
            noise = np.random.normal(0, s['std'] * 0.05 if s['std'] > 0 else 0.01)
            seasonal_adjust = (seasonal_mean - s['mean']) * 0.08
            next_val = last_val + trend + seasonal_adjust + noise

        if 'temperature' in c:
            next_val = max(-50.0, min(60.0, next_val))
        if 'humidity' in c:
            next_val = max(0.0, min(100.0, next_val))
        if 'air_quality' in c:
            next_val = max(0.0, next_val)

        out[c] = float(next_val)
    return out

def generator_loop(out_csv, stats, hourly_profile, meta, interval, seed, method, use_real_time):
    np.random.seed(seed)
    last_ts = pd.to_datetime(meta['last_timestamp'])
    last_vals = {c: stats[c]['last_value'] for c in meta['cols']}
    logging.info(f"Starting simulation -> {out_csv}. Interval: {interval}s. Method: {method}")

    try:
        while True:
            if use_real_time:
                next_ts = datetime.now()
            else:
                next_ts = last_ts + timedelta(seconds=meta['median_interval_seconds'])

            next_vals = generate_next_values(last_vals, stats, hourly_profile, last_ts, next_ts, method)

            row = {'timestamp': next_ts.isoformat()}
            row.update(next_vals)
            append_row_csv(out_csv, row)
            logging.info(f"Emitted: {row}")

            last_ts = next_ts
            last_vals = next_vals

            time.sleep(interval)
    except GracefulExit:
        logging.info("Simulation stopped by user.")
    except Exception:
        logging.exception("Unexpected error.")
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', type=str, default='historical.csv', help='path to historical csv')
    parser.add_argument('--out', type=str, default='simulated_stream.csv', help='output csv path')
    parser.add_argument('--interval', type=float, default=1.0, help='seconds between emissions')
    parser.add_argument('--seed', type=int, default=42, help='random seed')
    parser.add_argument('--method', type=str, default='trend_seasonal', choices=['random_walk','trend_seasonal','bootstrap_diff'], help='simulation method')
    parser.add_argument('--real_time', action='store_true', help='use actual current time for timestamps')
    args = parser.parse_args()

    if not os.path.exists(args.history):
        raise SystemExit(f"History file not found: {args.history}")

    df = pd.read_csv(args.history)
    stats, hourly_profile, meta = analyze_history(df)
    logging.info("History meta: %s", meta)
    register_signal_handlers()
    generator_loop(args.out, stats, hourly_profile, meta, args.interval, args.seed, args.method, args.real_time)

if __name__ == '__main__':
    main()
