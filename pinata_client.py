from __future__ import annotations

import os
from typing import Dict, Any
import httpx


class PinataError(RuntimeError):
    pass


def _jwt() -> str | None:
    return os.getenv("PINATA_JWT")


def _gateway_base() -> str:
    return os.getenv("PINATA_GATEWAY", "https://gateway.pinata.cloud/ipfs")


def upload_file(path: str, name: str | None = None) -> Dict[str, Any]:
    jwt = _jwt()
    if not jwt:
        raise PinataError("PINATA_JWT is not set")

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"Authorization": f"Bearer {jwt}"}

    file_name = name or os.path.basename(path)

    with open(path, "rb") as f:
        files = {
            "file": (file_name, f),
        }
        with httpx.Client(timeout=120) as client:
            resp = client.post(url, headers=headers, files=files)
            if resp.status_code >= 400:
                raise PinataError(resp.text)
            data = resp.json()

    ipfs_hash = data.get("IpfsHash")
    if not ipfs_hash:
        raise PinataError("Pinata response missing IpfsHash")

    return {
        "ipfsHash": ipfs_hash,
        "ipfsUrl": f"ipfs://{ipfs_hash}",
        "gatewayUrl": f"{_gateway_base()}/{ipfs_hash}",
        "pinata": data,
    }
