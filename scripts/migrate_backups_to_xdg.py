"""Migração de arquivos de backup legados para o diretório XDG correto.

Contexto: antes do fix da issue #47, o BackupService resolvia backup_dir a
partir de db_path.parent, gerando `src/data/backups/` quando
TIMEBLOCK_DB_PATH era relativo. Após o fix, backups são gravados em
$XDG_DATA_HOME/atomvs/backups (~/.local/share/atomvs/backups por padrão).

Este script move arquivos legados da origem para o destino correto,
tratando duplicatas via hash SHA-256 e preservando arquivos em caso
de erro para permitir inspeção manual.

Uso:
    python scripts/migrate_backups_to_xdg.py --dry-run
    python scripts/migrate_backups_to_xdg.py

O modo --dry-run lista as ações planejadas sem executá-las.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path


def resolve_xdg_backup_dir() -> Path:
    """Resolve o diretório XDG para backups do ATOMVS."""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "atomvs" / "backups"
    return Path.home() / ".local" / "share" / "atomvs" / "backups"


def file_hash(path: Path) -> str:
    """Calcula SHA-256 de um arquivo para detecção de duplicatas."""
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def migrate(source_dir: Path, target_dir: Path, dry_run: bool) -> None:
    """Move arquivos .db da origem para o destino, tratando duplicatas."""
    if not source_dir.exists():
        print(f"[INFO] Origem inexistente: {source_dir}")
        print("[INFO] Nada a migrar.")
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    db_files = sorted(source_dir.glob("*.db"))
    if not db_files:
        print(f"[INFO] Nenhum arquivo .db em {source_dir}")
        return

    total = len(db_files)
    print(f"[INFO] {total} arquivo(s) .db encontrado(s) em {source_dir}")
    print(f"[INFO] Destino: {target_dir}")
    if dry_run:
        print("[INFO] Modo dry-run: nenhuma operação será executada\n")
    else:
        print()

    moved = 0
    duplicates_removed = 0
    skipped = 0

    for src_file in db_files:
        dst_file = target_dir / src_file.name

        if not dst_file.exists():
            if dry_run:
                print(f"[MOVE]   {src_file.name}")
            else:
                try:
                    shutil.move(str(src_file), str(dst_file))
                    print(f"[MOVED]  {src_file.name}")
                except Exception as exc:
                    print(f"[ERROR]  {src_file.name}: {exc}")
                    skipped += 1
                    continue
            moved += 1
            continue

        src_hash = file_hash(src_file)
        dst_hash = file_hash(dst_file)

        if src_hash == dst_hash:
            if dry_run:
                print(f"[DUP]    {src_file.name} (hash idêntico, remove origem)")
            else:
                try:
                    src_file.unlink()
                    print(f"[DUP]    {src_file.name} (origem removida)")
                except Exception as exc:
                    print(f"[ERROR]  {src_file.name}: {exc}")
                    skipped += 1
                    continue
            duplicates_removed += 1
        else:
            print(f"[SKIP]   {src_file.name} (existe com conteúdo diferente)")
            skipped += 1

    print()
    print(f"[SUMMARY] Movidos: {moved}")
    print(f"[SUMMARY] Duplicatas removidas: {duplicates_removed}")
    print(f"[SUMMARY] Ignorados: {skipped}")
    print(f"[SUMMARY] Total processado: {moved + duplicates_removed + skipped}/{total}")


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Lista ações planejadas sem executá-las",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("src/data/backups"),
        help="Diretório de origem (padrão: src/data/backups)",
    )
    args = parser.parse_args()

    source_dir = args.source.resolve()
    target_dir = resolve_xdg_backup_dir()

    migrate(source_dir, target_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
