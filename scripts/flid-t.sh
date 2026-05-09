declare script_path=`realpath $0`
declare script_dir=`dirname $script_path`
declare id_file=`dirname $script_dir`/test-data/idgen-1/idx.txt

function run_idtest
{
  local prj_dir=`dirname $script_dir`
  local pypath=$prj_dir/src
  local test_dir=$prj_dir/test-data/idgen-1

  sleep $1  

  PYTHONPATH=$pypath python $script_dir/flid-t.py \
    --idfile=$id_file --test-count=1 
}


function main_proc
{
  local prj_dir=`dirname $script_dir`

  for idx in `seq 1000`; do
    run_idtest 0.$RANDOM >/dev/null &
  done
  wait
  cat $id_file
}

main_proc


# vi: se ts=2 sw=2 et:
