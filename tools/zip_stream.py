# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Pure bounded validation of raw ZIP member streams, independent of source trees."""
import struct
import zipfile
import zlib


def raw_member(data, entry, remaining, *, error=ValueError):
    """Validate the full raw STORED/DEFLATED span, not ZipExtFile's truncated view."""
    def _require(condition, message):
        if not condition:
            raise error(message)

    _require(entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
             "Unsupported ZIP compression method; only STORED and DEFLATED are accepted")
    offset = entry.header_offset
    _require(0 <= offset <= len(data) - 30, "Invalid ZIP local header offset")
    header = struct.unpack_from("<4s5H3I2H", data, offset)
    _require(header[0] == b"PK\x03\x04" and header[2] == entry.flag_bits and header[3] == entry.compress_type,
             "ZIP local/central header mismatch")
    if not entry.flag_bits & 8:  # Streaming writers may leave sizes/CRC to a data descriptor.
        _require(header[6:9] == (entry.CRC, entry.compress_size, entry.file_size), "ZIP local/central size or CRC mismatch")
    position = offset + 30 + header[-2] + header[-1]
    end = position + entry.compress_size
    _require(position <= end <= len(data), "ZIP compressed span exceeds archive")
    allowed = min(entry.file_size, remaining)
    count = crc = 0
    decoder = zlib.decompressobj(-zlib.MAX_WBITS) if entry.compress_type == zipfile.ZIP_DEFLATED else None
    pending = b""
    while True:
        # A one-byte sentinel detects a dishonest length without expanding the rest.
        maximum = min(65536, allowed - count + 1)
        if decoder is None:
            output = data[position:min(end, position + maximum)]
            position += len(output)
        else:
            if not pending and position < end:
                pending = data[position:min(end, position + 65536)]
                position += len(pending)
            output = decoder.decompress(pending, maximum)
            pending = decoder.unconsumed_tail
        count += len(output)
        _require(count <= allowed, f"ZIP expanded content exceeds allowed size ({count} > {allowed})")
        crc = zlib.crc32(output, crc)
        if decoder is None:
            if position == end:
                break
        elif decoder.eof:
            _require(not decoder.unused_data and not pending and position == end, "Extra bytes after complete DEFLATE stream")
            break
        else:
            _require(pending or position < end or output, "Incomplete DEFLATE stream")
    _require(count == entry.file_size, "ZIP actual decoded size differs from declared size")
    _require(crc == entry.CRC, "ZIP actual decoded CRC mismatch")
    return count
