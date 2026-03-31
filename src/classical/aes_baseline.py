"""AES baseline implementations for smart-grid benchmark workloads."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from benchmarks.runner import BenchmarkRecord, BenchmarkRunner

AESMode = Literal["CBC", "GCM"]
DEFAULT_AES_KEY_SIZES = (128, 256)
DEFAULT_AES_PAYLOAD_SIZES = (64, 512, 1024, 65536)


@dataclass(slots=True, frozen=True)
class AESCiphertext:
    """Normalized encrypted payload for both CBC and GCM."""

    mode: AESMode
    ciphertext: bytes
    nonce_or_iv: bytes
    tag: bytes | None = None


def generate_aes_key(key_bits: int) -> bytes:
    """Generate an AES key for the requested key size."""

    if key_bits not in DEFAULT_AES_KEY_SIZES:
        raise ValueError(f"Unsupported AES key size: {key_bits}")
    return get_random_bytes(key_bits // 8)


def encrypt_aes_cbc(key: bytes, plaintext: bytes) -> AESCiphertext:
    """Encrypt plaintext with AES-CBC and PKCS7 padding."""

    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return AESCiphertext(mode="CBC", ciphertext=ciphertext, nonce_or_iv=iv)


def decrypt_aes_cbc(key: bytes, bundle: AESCiphertext) -> bytes:
    """Decrypt an AES-CBC ciphertext bundle."""

    cipher = AES.new(key, AES.MODE_CBC, iv=bundle.nonce_or_iv)
    return unpad(cipher.decrypt(bundle.ciphertext), AES.block_size)


def encrypt_aes_gcm(key: bytes, plaintext: bytes) -> AESCiphertext:
    """Encrypt plaintext with AES-GCM and return nonce plus authentication tag."""

    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return AESCiphertext(
        mode="GCM",
        ciphertext=ciphertext,
        nonce_or_iv=cipher.nonce,
        tag=tag,
    )


def decrypt_aes_gcm(key: bytes, bundle: AESCiphertext) -> bytes:
    """Decrypt and authenticate an AES-GCM ciphertext bundle."""

    cipher = AES.new(key, AES.MODE_GCM, nonce=bundle.nonce_or_iv)
    return cipher.decrypt_and_verify(bundle.ciphertext, bundle.tag)


def encrypt_aes(key: bytes, plaintext: bytes, mode: AESMode) -> AESCiphertext:
    """Route to the requested AES mode."""

    if mode == "CBC":
        return encrypt_aes_cbc(key, plaintext)
    if mode == "GCM":
        return encrypt_aes_gcm(key, plaintext)
    raise ValueError(f"Unsupported AES mode: {mode}")


def decrypt_aes(key: bytes, bundle: AESCiphertext) -> bytes:
    """Decrypt a previously encrypted AES payload."""

    if bundle.mode == "CBC":
        return decrypt_aes_cbc(key, bundle)
    if bundle.mode == "GCM":
        return decrypt_aes_gcm(key, bundle)
    raise ValueError(f"Unsupported AES mode: {bundle.mode}")


def benchmark_aes_baselines(
    runner: BenchmarkRunner | None = None,
    *,
    trials: int = 100,
    warmup: int = 3,
    payload_sizes: tuple[int, ...] = DEFAULT_AES_PAYLOAD_SIZES,
    key_sizes: tuple[int, ...] = DEFAULT_AES_KEY_SIZES,
    export_path: str | Path = "aes_baseline.csv",
) -> list[BenchmarkRecord]:
    """Benchmark AES encryption and decryption across key sizes and modes."""

    runner = runner or BenchmarkRunner()
    records: list[BenchmarkRecord] = []

    for key_bits in key_sizes:
        key = generate_aes_key(key_bits)
        for mode in ("CBC", "GCM"):
            for payload_bytes in payload_sizes:
                plaintext = get_random_bytes(payload_bytes)

                encrypt_record = runner.benchmark(
                    lambda key=key, data=plaintext, mode=mode: encrypt_aes(key, data, mode),
                    scheme="AES",
                    mode=mode,
                    key_size=key_bits,
                    payload_bytes=payload_bytes,
                    operation="encrypt",
                    trials=trials,
                    warmup=warmup,
                )
                records.append(encrypt_record)

                encrypted = encrypt_aes(key, plaintext, mode)
                decrypt_record = runner.benchmark(
                    lambda key=key, blob=encrypted: decrypt_aes(key, blob),
                    scheme="AES",
                    mode=mode,
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
    "AESCiphertext",
    "DEFAULT_AES_KEY_SIZES",
    "DEFAULT_AES_PAYLOAD_SIZES",
    "benchmark_aes_baselines",
    "decrypt_aes",
    "encrypt_aes",
    "generate_aes_key",
]
