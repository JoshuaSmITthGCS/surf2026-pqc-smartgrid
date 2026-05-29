"""RSA baseline implementations for SURF 2026 benchmarks."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from rich.console import Console

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner

DEFAULT_RSA_KEY_SIZES = (2048, 4096)
DEFAULT_RSA_PAYLOAD_SIZES = (64, 128, 256)
DEFAULT_RSA_HASH = SHA256
PayloadFactory = Callable[[int], bytes]


def generate_rsa_keypair(key_bits: int) -> RSA.RsaKey:
    """Generate an RSA keypair for the requested modulus size."""

    if key_bits not in DEFAULT_RSA_KEY_SIZES:
        raise ValueError(f"Unsupported RSA key size: {key_bits}")
    return RSA.generate(key_bits)


def max_oaep_plaintext_bytes(key_bits: int, *, hash_module=DEFAULT_RSA_HASH) -> int:
    """Return the OAEP maximum plaintext size for a modulus and hash function."""

    modulus_bytes = key_bits // 8
    return modulus_bytes - (2 * hash_module.digest_size) - 2


def encrypt_rsa(public_key: RSA.RsaKey, plaintext: bytes, *, hash_module=DEFAULT_RSA_HASH) -> bytes:
    """Encrypt plaintext with RSA-OAEP."""

    cipher = PKCS1_OAEP.new(public_key, hashAlgo=hash_module)
    return cipher.encrypt(plaintext)


def decrypt_rsa(private_key: RSA.RsaKey, ciphertext: bytes, *, hash_module=DEFAULT_RSA_HASH) -> bytes:
    """Decrypt RSA-OAEP ciphertext."""

    cipher = PKCS1_OAEP.new(private_key, hashAlgo=hash_module)
    return cipher.decrypt(ciphertext)


def _payload_for_size(payload_bytes: int, payload_factory: PayloadFactory | None) -> bytes:
    plaintext = (
        bytes(payload_factory(payload_bytes))
        if payload_factory is not None
        else get_random_bytes(payload_bytes)
    )
    if len(plaintext) != payload_bytes:
        raise ValueError(
            "payload_factory must return exactly "
            f"{payload_bytes} bytes, got {len(plaintext)}"
        )
    return plaintext


def benchmark_rsa_baselines(
    runner: BenchmarkRunner | None = None,
    *,
    trials: int = 25,
    warmup: int = 2,
    payload_sizes: tuple[int, ...] = DEFAULT_RSA_PAYLOAD_SIZES,
    key_sizes: tuple[int, ...] = DEFAULT_RSA_KEY_SIZES,
    payload_factory: PayloadFactory | None = None,
    export_path: str | Path = "rsa_baseline.csv",
    console: Console | None = None,
) -> list[BenchmarkRecord]:
    """Benchmark RSA encryption and decryption for valid OAEP payload sizes.

    OAEP has a strict plaintext limit of ``k - 2*hLen - 2`` bytes, where ``k`` is
    the modulus size in bytes and ``hLen`` is the hash digest size. With SHA-256:
    RSA-2048 supports up to 190 bytes and RSA-4096 supports up to 446 bytes.
    That means the requested 256-byte test case is valid for RSA-4096 but not
    for RSA-2048, so the latter is skipped and reported to the console.

    ``payload_factory`` can be provided to benchmark deterministic real-data
    payloads instead of random bytes. It must return exactly the requested
    number of bytes.
    """

    runner = runner or BenchmarkRunner()
    console = console or runner.console
    records: list[BenchmarkRecord] = []

    for key_bits in key_sizes:
        keypair = generate_rsa_keypair(key_bits)
        public_key = keypair.publickey()
        max_payload = max_oaep_plaintext_bytes(key_bits)

        for payload_bytes in payload_sizes:
            if payload_bytes > max_payload:
                console.print(
                    "[yellow]Skipping RSA-"
                    f"{key_bits} payload {payload_bytes} bytes: "
                    f"OAEP-SHA256 max is {max_payload} bytes.[/yellow]"
                )
                continue

            plaintext = _payload_for_size(payload_bytes, payload_factory)

            encrypt_record = runner.benchmark(
                lambda key=public_key, data=plaintext: encrypt_rsa(key, data),
                scheme="RSA",
                mode="OAEP-SHA256",
                key_size=key_bits,
                payload_bytes=payload_bytes,
                operation="encrypt",
                trials=trials,
                warmup=warmup,
            )
            records.append(encrypt_record)

            ciphertext = encrypt_rsa(public_key, plaintext)
            decrypt_record = runner.benchmark(
                lambda key=keypair, blob=ciphertext: decrypt_rsa(key, blob),
                scheme="RSA",
                mode="OAEP-SHA256",
                key_size=key_bits,
                payload_bytes=payload_bytes,
                operation="decrypt",
                trials=trials,
                warmup=warmup,
            )
            records.append(decrypt_record)

    runner.export_records(records, export_path)
    return records


__all__ = [
    "DEFAULT_RSA_KEY_SIZES",
    "DEFAULT_RSA_PAYLOAD_SIZES",
    "benchmark_rsa_baselines",
    "decrypt_rsa",
    "encrypt_rsa",
    "generate_rsa_keypair",
    "max_oaep_plaintext_bytes",
]
