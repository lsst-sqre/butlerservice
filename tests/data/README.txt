hsc_raw was generated as follows:

* Start with a copy of the DM stack that includes obs_subaru
* git clone https://github.com/lsst/testdata_ci_hsc
* execute these commands::

    rm -rf hsc_raw
    setup obs_subaru
    butler create hsc_raw
    butler register-instrument hsc_raw lsst.obs.subaru.HyperSuprimeCam
    butler ingest-raws hsc_raw <path-to-testdata_ci_hsc>/raw

Then delete all contents from hsc_raw except butler.yaml and gen3.sqlite3.

test_repo was generated as follows:

* Start with a copy of the DM stack that includes daf_butler
* If your copy of daf_butler is installed then git clone daf_butler tests/data/
* butler create test_repo
* butler import test_repo . --export-file <path-to-tests/data>/registry/hsc-rc2-subset.yaml
