import argparse
import sys
import time
from pathlib import Path

import pandas as pd
from phe import paillier

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load(n):
    df = pd.read_csv(ROOT / "data" / "smart_grid_dataset.csv", nrows=n)
    return [round(float(v), 2) for v in df["Power Consumption (kW)"]]


def t0():
    return time.perf_counter()


def ms(s):
    return f"{(time.perf_counter() - s) * 1000:.1f}ms"


def paillier_run(r):
    x = [int(round(v * 100)) for v in r]
    print("\npaillier-2048")
    s = t0()
    pk, sk = paillier.generate_paillier_keypair(n_length=2048)
    print(f"keygen {ms(s)}  n={pk.n.bit_length()}b")
    s = t0()
    ct = [pk.encrypt(v) for v in x]
    print(f"encrypt x{len(x)} {ms(s)}")
    for v, c in zip(x[:3], ct):
        print(f"  {v} -> {str(c.ciphertext(be_secure=False))[:32]}...")
    s = t0()
    tot = ct[0]
    for c in ct[1:]:
        tot = tot + c
    print(f"add {ms(s)}")
    s = t0()
    d = sk.decrypt(tot)
    print(f"decrypt {ms(s)}")
    print(f"got={d} want={sum(x)} {'ok' if d == sum(x) else 'FAIL'}")


def bfv_run(r):
    from src.fhe import bfv_scheme as b

    x = [int(round(v * 100)) for v in r]
    print("\nbfv-8192")
    s = t0()
    ctx = b.create_bfv_context(8192)
    print(f"keygen {ms(s)}")
    s = t0()
    v = b.encrypt_integers(ctx, x)
    print(f"encrypt x{len(x)} {ms(s)}  ct={len(v.serialize())}B")
    s = t0()
    tot = v.sum()
    print(f"sum {ms(s)}")
    s = t0()
    d = int(tot.decrypt()[0])
    print(f"decrypt {ms(s)}")
    print(f"got={d} want={sum(x)} {'ok' if d == sum(x) else 'FAIL'}")


def ckks_run(r):
    from src.fhe import ckks_scheme as c

    print("\nckks-8192")
    s = t0()
    ctx = c.create_ckks_context(c.DEFAULT_CKKS_CONFIGS[0])
    print(f"keygen {ms(s)}")
    s = t0()
    v = c.encrypt_floats(ctx, r)
    print(f"encrypt x{len(r)} {ms(s)}  ct={len(v.serialize())}B")
    s = t0()
    tot = v.sum()
    print(f"sum {ms(s)}")
    s = t0()
    d = float(tot.decrypt()[0])
    print(f"decrypt {ms(s)}")
    print(f"got={d:.6f} want={sum(r):.6f} err={abs(d - sum(r)):.1e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-n", type=int, default=8)
    p.add_argument("--attack", action="store_true")
    a = p.parse_args()

    r = load(a.n)
    print(f"readings(kW): {r}")
    print(f"sum: {sum(r):.2f}")

    paillier_run(r)
    bfv_run(r)
    ckks_run(r)

    if a.attack:
        print("\nshor vs paillier (toy key)")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import real_shor_vs_paillier

        real_shor_vs_paillier.main()


if __name__ == "__main__":
    main()
