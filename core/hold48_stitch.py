"""D-111 — stitch tile PDBs and PAE. Overlap by per-residue pLDDT; off-block PAE is null.

⚠ A zero in an off-block cell would assert measured pair-confidence for residues
that never shared a forward pass. Off-block is ``None``, never ``0``.
⚠ A residue covered by no tile is an error, not a gap filled with invented
coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from core.features import parse_pdb
from core.hold48 import TILE_WINDOW_AA, UncoveredResidue


@dataclass(frozen=True)
class TileFold:
    """One folded tile. ``pdb`` residues are numbered 1..length (ESMFold local).
    ``start``/``end`` are 1-based inclusive on the parent ECD sequence."""

    start: int
    end: int
    pdb: str
    plddt: Sequence[float]
    pae: Sequence[Sequence[float]]

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def _local_index(parent_res: int, tile: TileFold) -> int:
    return parent_res - tile.start


def _covers(tile: TileFold, parent_res: int) -> bool:
    return tile.start <= parent_res <= tile.end


def _plddt_at(tile: TileFold, parent_res: int) -> float:
    i = _local_index(parent_res, tile)
    return float(tile.plddt[i])


def winning_tile(tiles: Sequence[TileFold], parent_res: int) -> TileFold:
    """Overlap: the covering tile with higher pLDDT at this residue; tie → earlier tile."""
    covering = [t for t in tiles if _covers(t, parent_res)]
    if not covering:
        raise UncoveredResidue(
            f"residue {parent_res} is covered by no tile — a gap is an error, "
            f"not invented coordinates (D-111)"
        )
    return max(covering, key=lambda t: (_plddt_at(t, parent_res), -tiles.index(t)))


def stitch_plddt(tiles: Sequence[TileFold], length: int) -> list[float]:
    return [_plddt_at(winning_tile(tiles, r), r) for r in range(1, length + 1)]


def _atoms_by_local_res(pdb: str) -> dict[int, list]:
    grouped: dict[int, list] = {}
    for atom in parse_pdb(pdb):
        grouped.setdefault(atom.res_seq, []).append(atom)
    return grouped


def _format_atom(serial: int, atom, res_seq: int, b_factor: float) -> str:
    """Fixed-column PDB ATOM. ``parse_pdb`` round-trips name/res/xyz/element."""
    name = atom.name if len(atom.name) >= 4 else f"{atom.name:>3s} "
    if len(name) > 4:
        name = name[:4]
    res_name = (atom.res_name or "UNK")[:3].ljust(3)
    chain = (atom.chain or "A")[:1] or "A"
    element = (atom.element or "")[:2]
    return (
        f"ATOM  {serial:5d} {name} {res_name} {chain}{res_seq:4d}    "
        f"{atom.x:8.3f}{atom.y:8.3f}{atom.z:8.3f}  1.00{b_factor:6.2f}          "
        f"{element:>2s}  "
    )


def stitch_pdb(tiles: Sequence[TileFold], length: int) -> str:
    """Concatenate winning-tile atoms, remapped to parent residue numbers.

    ⚠ No atom is invented. A residue the winning tile did not emit raises.
    """
    grouped = [(t, _atoms_by_local_res(t.pdb)) for t in tiles]
    lines: list[str] = []
    serial = 1
    plddt = stitch_plddt(tiles, length)
    for parent_res in range(1, length + 1):
        winner = winning_tile(tiles, parent_res)
        local = _local_index(parent_res, winner)
        atoms_map = next(m for t, m in grouped if t is winner)
        atoms = atoms_map.get(local + 1)  # ESMFold local res_seq is 1-based
        if not atoms:
            raise UncoveredResidue(
                f"residue {parent_res} won by tile {winner.start}-{winner.end} "
                f"but that PDB has no atoms at local {local + 1} — refusing to invent coordinates"
            )
        bf = plddt[parent_res - 1]
        for atom in atoms:
            lines.append(_format_atom(serial, atom, parent_res, bf))
            serial += 1
    lines.append("END")
    return "\n".join(lines) + "\n"


def stitch_pae(tiles: Sequence[TileFold], length: int) -> list[list[Optional[float]]]:
    """Block-diagonal PAE. Off-block is ``None``, never ``0``.

    A pair ``(i, j)`` keeps a tile's PAE only when **both** residues sat in that
    tile's window. If several tiles cover the pair, the tile that won residue
    ``i`` supplies the value when it also covers ``j``; otherwise ``None``.
    """
    matrix: list[list[Optional[float]]] = [[None] * length for _ in range(length)]
    winners = [winning_tile(tiles, r) for r in range(1, length + 1)]
    for i in range(length):
        for j in range(length):
            ti = winners[i]
            parent_i, parent_j = i + 1, j + 1
            if not (_covers(ti, parent_i) and _covers(ti, parent_j)):
                continue
            li = _local_index(parent_i, ti)
            lj = _local_index(parent_j, ti)
            matrix[i][j] = float(ti.pae[li][lj])
    return matrix


def write_stitched(
    tiles: Sequence[TileFold],
    length: int,
    out_dir,
) -> dict[str, str]:
    """Write stitched PDB + PAE JSON (null off-block) and keep per-tile PAE."""
    import json
    from pathlib import Path

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pdb = stitch_pdb(tiles, length)
    pae = stitch_pae(tiles, length)
    plddt = stitch_plddt(tiles, length)
    (out / "stitched.pdb").write_text(pdb, encoding="utf-8")
    (out / "stitched_plddt.json").write_text(json.dumps(plddt), encoding="utf-8")
    (out / "stitched_pae.json").write_text(json.dumps(pae), encoding="utf-8")
    for n, tile in enumerate(tiles, start=1):
        (out / f"tile{n}.pdb").write_text(tile.pdb, encoding="utf-8")
        (out / f"tile{n}_pae.json").write_text(json.dumps([list(row) for row in tile.pae]),
                                               encoding="utf-8")
        (out / f"tile{n}_plddt.json").write_text(json.dumps(list(tile.plddt)), encoding="utf-8")
    return {
        "pdb": str(out / "stitched.pdb"),
        "pae": str(out / "stitched_pae.json"),
        "plddt": str(out / "stitched_plddt.json"),
    }


def assert_tile_cap(tiles: Sequence[TileFold]) -> None:
    for t in tiles:
        if t.length > TILE_WINDOW_AA:
            raise UncoveredResidue(
                f"tile {t.start}-{t.end} length {t.length} exceeds {TILE_WINDOW_AA}"
            )
