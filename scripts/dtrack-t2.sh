declare script_path=`realpath $0`
declare script_dir=`dirname $script_path`

export DTRACK_CONFIG=./test-data/config/test-dtrack-2.toml
export PYTHONPATH=./src:./tgstore/src
python $script_dir/dtrack-t.py "$@"

# vi: se ts=2 sw=2 et:
