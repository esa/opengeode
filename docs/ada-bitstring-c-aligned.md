# Ada backend: C-aligned BIT STRING representation

## Summary

OpenGeode's Ada backend now represents ASN.1 `BIT STRING` values the same way
the C backend does: as an array of **whole bytes** (asn1scc's
`adaasn1rtl.OctetBuffer`), instead of the packed one-element-per-bit
`adaasn1rtl.BitArray`.

This is done by passing `-adaBitStringAlignment` to asn1scc when the Ada
dataview is generated, and by emitting byte-based Ada expressions in
`opengeode/AdaGenerator.py`. It is the **default** for Ada: no OpenGeode flag
is needed.

## Why

asn1scc used to store an Ada `BIT STRING` as a packed array with
`Component_Size = 1`, which packs **LSB-first**: ASN.1 bit `k` was memory bit
`k mod 8` of byte `k / 8`. C stores it **MSB-first** (`byte arr[]`, bit `k` at
mask `0x80 >> (k mod 8)` of byte `k / 8`). The two agree on the wire (uPER /
ACN / XER are unchanged) but not in memory, so a `BIT STRING` buffer produced
by C and read by Ada (or vice versa) without going through a codec was
per-byte bit-reversed.

With `-adaBitStringAlignment`, `BS ::= BIT STRING (SIZE (8))` becomes:

```ada
type BS is record
    Data : adaasn1rtl.OctetBuffer (1 .. 1);   --  ceil(8 / 8) bytes
end record;
```

identical to C's `struct { byte arr[1]; }`. For a variable size the length is
still kept in **bits** next to the byte array:

```ada
BSVar ::= BIT STRING (SIZE (1..20))
-->
type BSVar is record
    Length : BSVar_length_index;               --  1 .. 20  (bits)
    Data   : adaasn1rtl.OctetBuffer (1 .. 3);  --  ceil(20 / 8) bytes
end record;
```

## Addressing a bit

ASN.1 bit `k` (0-based, as in SDL) is:

| | expression |
|---|---|
| byte index (1-based) | `k / 8 + 1` |
| mask | `0x80 >> (k mod 8)` = `Shift_Right (16#80#, k mod 8)` |

The generated Ada uses exactly this. Reading bit `k` of a variable `X`:

```ada
if (X.Data (k / 8 + 1) and Shift_Right (16#80#, k mod 8)) /= 0 then ...
```

Writing bit `k` is a read-modify-write:

```ada
X.Data (k / 8 + 1) := (if <cond> then X.Data (k / 8 + 1) or mask
                                else X.Data (k / 8 + 1) and not mask);
```

## What changed for users (API break)

`X.Data` now indexes **bytes**, not bits. Any OpenGeode Ada application whose
SDL uses `bs(i)` (index a bit), a bit-string literal `'1010'B`, `not` /
bitwise operators, substring, or `//` on a `BIT STRING` is affected, but the
generated code handles all of those automatically — the break is for hand-
written Ada that touched the asn1scc dataview directly:

| before (per bit) | now (per byte) |
|---|---|
| `X.Data (1) := 1;` (bit 0) | `X.Data (1) := 16#80#;` |
| `X.Data (9) := 1;` (bit 8) | `X.Data (2) := 16#80#;` |
| `B := X.Data (1);` | `B := (X.Data (1) and 16#80#) /= 0;` |
| `X.Data'Length` (N bits) | `X.Data'Length` (ceil(N/8) bytes) |
| `X.Length` | unchanged, still bits |

SDL-level code does not need to change: indexing, literals and operators are
translated by OpenGeode.

## What did not change

* The wire format (uPER, ACN, XER) — bit-identical to before.
* The C and Rust backends.
* SDL source syntax and semantics: `bs(i)`, `'1010'B`, `{bit0, bit3}`,
  `length(bs)`, `not bs`, `bs1 and bs2`, `bs(i, j)`, `bs1 // bs2` all keep
  working; only the Ada they lower to changed.

## Implementation

* `opengeode/AdaGenerator.py`
  * `_bit_index_of` / `_bit_byte_mask` — map a bit index to `(byte, mask)`.
  * `_pack_bits_to_bytes` — pack a `'...'B` literal MSB-first into bytes.
  * `_prim_index` — bit read is a masked test, bit write is a
    read-modify-write.
  * `_string_literal` / `array_content` — literals become byte aggregates.
  * `string_payload` / `_append` / `append_size` — byte ranges, while `Length`
    stays in bits.
  * `_bitwise_operators` / `_not_expression` — per-byte.
  * `_expr_in` — per-byte membership.
* `opengeode/opengeode.py` — the generated `Makefile.project` passes
  `-adaBitStringAlignment` to asn1scc for Ada.
* `tests/testsuite/*/Makefile*`, `shared.mk`, `testqgen.py` — same flag in the
  test harness.
* asn1scc side (branch `feature_bitstring_align_ada_with_c`): the BIT STRING
  constant printer emits bytes, and the aligned `_array` subtype is a
  constrained `OctetBuffer` so constant aggregates have bounds.

## Limitations

* A non-byte-multiple size carries up to 7 unused bits in the top byte; they
  are zeroed by asn1scc's decoder. Mask the top byte if C sets that padding.
* `X.Data'Length` is a byte count. For a fixed-size type the bit count is the
  compile-time constant `N`; for a variable-size type it is `X.Length`.
