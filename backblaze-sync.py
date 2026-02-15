

import time
import sys

import b2sdk.v2


info = b2sdk.v2.InMemoryAccountInfo()  # store credentials, tokens and cache in memory
b2_api = b2sdk.v2.B2Api(info)
application_key_id = '0058b2a3056cdad0000000001'
application_key = 'K0054GLkrUDwGR1wSclEOOTzrKyaJL0'
bucket_name = 'chirp-next'
source_dir = './downloads/'
destination_bucket = f'b2://{bucket_name}'
no_progress = False

b2_api.authorize_account("production", application_key_id, application_key)
b2_api.get_bucket_by_name(bucket_name)

source = b2sdk.v2.parse_folder(source_dir, b2_api)
destination = b2sdk.v2.parse_folder(destination_bucket, b2_api)
policies_manager = b2sdk.v2.ScanPoliciesManager(exclude_all_symlinks=True)

synchronizer = b2sdk.v2.Synchronizer(
        max_workers=10,
        policies_manager=policies_manager,
        dry_run=False,
        allow_empty_source=True,
)


with b2sdk.v2.SyncReport(sys.stdout, no_progress) as reporter:
        synchronizer.sync_folders(
            source_folder=source,
            dest_folder=destination,
            now_millis=int(round(time.time() * 1000)),
            reporter=reporter,
        )