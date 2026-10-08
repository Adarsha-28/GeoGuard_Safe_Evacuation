#!/usr/bin/env python3
"""Automated local PostgreSQL + PostGIS setup for GeoGuard on Windows.

Sets up a local user-space PostgreSQL 18 + PostGIS 3.6 instance running on port 5433
without requiring administrator privileges.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

PG_SOURCE = Path("D:/Apps/Postgresql")
BASE_USER_DIR = Path(os.environ.get("USERPROFILE", "C:/Users/ADARSHA"))
PG_TARGET = BASE_USER_DIR / "geoguard_pgsql"
PG_DATA = BASE_USER_DIR / "geoguard_pgdata"
POSTGIS_ZIP_URL = "https://download.osgeo.org/postgis/windows/pg18/postgis-bundle-pg18-3.6.2x64.zip"
CACHE_ZIP = BASE_USER_DIR / "postgis-bundle-pg18-3.6.2x64.zip"
PG_PORT = 5433


def run_cmd(cmd: list[str], check: bool = True, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run subprocess command and capture output."""
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    # Ensure PG_TARGET bin is on PATH
    full_env["PATH"] = f"{PG_TARGET / 'bin'};{full_env.get('PATH', '')}"
    print(f"[CMD] {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=full_env)
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed with code {result.returncode}:")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {cmd[0]}")
    return result


def main() -> int:
    print("=" * 65)
    print("   GeoGuard V2 — Automated Local PostGIS Setup")
    print("=" * 65)

    # 1. Copy base PostgreSQL binaries (bin, lib, share)
    PG_TARGET.mkdir(parents=True, exist_ok=True)
    for folder in ["bin", "lib", "share"]:
        src = PG_SOURCE / folder
        dst = PG_TARGET / folder
        if not dst.exists():
            print(f"[..] Copying {folder} from {src} to {dst}...")
            shutil.copytree(src, dst)
            print(f"[OK] {folder} copied.")
        else:
            print(f"[OK] {dst} already exists.")

    # 2. Extract and overlay PostGIS bundle if not already done
    postgis_control = PG_TARGET / "share" / "extension" / "postgis.control"
    if not postgis_control.exists():
        extracted_dir = PG_TARGET / "postgis-bundle-pg18-3.6.2x64"
        if not extracted_dir.exists():
            print(f"[..] Extracting PostGIS zip into {PG_TARGET}...")
            with zipfile.ZipFile(CACHE_ZIP, "r") as z:
                z.extractall(PG_TARGET)

        print(f"[..] Overlaying PostGIS files into {PG_TARGET}...")
        for item in extracted_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, PG_TARGET / item.name, dirs_exist_ok=True)
        print("[OK] PostGIS bundle overlay complete.")
    else:
        print("[OK] PostGIS extension files verified.")

    # 3. Initialize database cluster if not exists
    initdb_exe = PG_TARGET / "bin" / "initdb.exe"
    if not (PG_DATA / "PG_VERSION").exists():
        print(f"[..] Initializing new database cluster at {PG_DATA}...")
        run_cmd([
            str(initdb_exe),
            "-U", "postgres",
            "-A", "trust",
            "-E", "UTF8",
            "-D", str(PG_DATA),
        ])
        print("[OK] Database cluster initialized.")
    else:
        print(f"[OK] Database cluster already exists at {PG_DATA}.")

    # 4. Start PostgreSQL on port 5433
    pg_ctl_exe = PG_TARGET / "bin" / "pg_ctl.exe"
    log_file = PG_DATA / "server.log"
    print(f"[..] Checking/Starting PostgreSQL server on port {PG_PORT}...")
    status = run_cmd([str(pg_ctl_exe), "status", "-D", str(PG_DATA)], check=False)
    if "is running" not in status.stdout:
        run_cmd([
            str(pg_ctl_exe),
            "start",
            "-D", str(PG_DATA),
            "-l", str(log_file),
            "-o", f"-p {PG_PORT}",
        ])
        time.sleep(3)
        print(f"[OK] PostgreSQL server running on port {PG_PORT}.")
    else:
        print(f"[OK] PostgreSQL server is already running on port {PG_PORT}.")

    # 5. Create geoguard database and enable PostGIS
    createdb_exe = PG_TARGET / "bin" / "createdb.exe"
    psql_exe = PG_TARGET / "bin" / "psql.exe"

    print("[..] Verifying 'geoguard' database...")
    run_cmd([
        str(createdb_exe),
        "-h", "localhost",
        "-p", str(PG_PORT),
        "-U", "postgres",
        "geoguard",
    ], check=False)

    print("[..] Enabling PostGIS extension in 'geoguard' database...")
    res = run_cmd([
        str(psql_exe),
        "-h", "localhost",
        "-p", str(PG_PORT),
        "-U", "postgres",
        "-d", "geoguard",
        "-c", "CREATE EXTENSION IF NOT EXISTS postgis; SELECT PostGIS_Full_Version();",
    ])
    print(f"[OK] PostGIS Active:\n{res.stdout.strip()}")

    # 6. Set password for postgres user to 'postgres'
    print("[..] Setting superuser password...")
    run_cmd([
        str(psql_exe),
        "-h", "localhost",
        "-p", str(PG_PORT),
        "-U", "postgres",
        "-d", "geoguard",
        "-c", "ALTER USER postgres WITH PASSWORD 'postgres';",
    ])
    print("[OK] Superuser configured.")

    # 7. Update .env with working DATABASE_URL
    env_file = Path(__file__).resolve().parent.parent / ".env"
    conn_str = f"postgresql://postgres:postgres@localhost:{PG_PORT}/geoguard"
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        import re
        content = re.sub(r"DATABASE_URL=.*", f"DATABASE_URL={conn_str}", content)
        env_file.write_text(content, encoding="utf-8")
        print(f"[OK] Updated {env_file.name} with DATABASE_URL={conn_str}")

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Local PostgreSQL + PostGIS operational at localhost:{PG_PORT}")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
