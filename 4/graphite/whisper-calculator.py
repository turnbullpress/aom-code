## Original source - https://gist.github.com/jjmaestro/5774063

#!/usr/bin/env python
# -*- coding: utf-8 -*-


def archive_to_bytes(archive):
    def to_seconds(s):
        SECONDS_IN_A = {
            's': 1,
            'm': 1 * 60,
            'h': 1 * 60 * 60,
            'd': 1 * 60 * 60 * 24,
            'y': 1 * 60 * 60 * 24 * 365,
        }

        return int(s[:-1]) * SECONDS_IN_A[s[-1]]

    archive = [map(to_seconds, point.split(':'))
               for point in args.archive.split(',')]

    SIZE_METADATA = 2 * 4 + 4 + 4  # 16 [!2LfL]
    SIZE_ARCHIVE_INFO = 3 * 4  # 12 [!3L]+
    SIZE_POINT = 4 + 8  # 12 [!Ld]+

    size = 0
    for resolution, retention in archive:
        size += SIZE_ARCHIVE_INFO + SIZE_POINT * retention/resolution

    if size:
        size += SIZE_METADATA

    return size


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculates the size of the whisper storage for the given \
                archive (in resolution:retention format, e.g. 1m:24h,5m:3m)"
    )
    parser.add_argument(
        'archive',
        help="Archive in storage-schemas.conf format (resolution:retention)"
    )

    args = parser.parse_args()

    print "{} >> {} bytes".format(args.archive, archive_to_bytes(args.archive))

