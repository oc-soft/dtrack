declare namedp_dir=test-data/test-2/namedp

function setup_test
{
  . scripts/dtrack-t2.sh init

  mkdir -p $namedp_dir
}


function update_content
{
  local content_id=$1
  local num=$2
  local sleep_tm=$3 
  sleep $sleep_tm

  . scripts/dtrack-t2.sh edit --id $content_id

  . scripts/dtrack-t2.sh update --id $content_id test-data/test-src-2/blog2-$num.txt
  local email=''
  local author=''
  read email <test-data/author-email.txt
  read author <test-data/author-name.txt  
  . scripts/dtrack-t2.sh commit --id $content_id --author "$author" --email $email --delete
}

function create_content
{
  local sleep_tm=$1 
  local num=$2
  sleep $sleep_tm

  local content_id=`. scripts/dtrack-t2.sh create`
  . scripts/dtrack-t2.sh update --id $content_id test-data/test-src-1/blog1-$num.txt
  . scripts/dtrack-t2.sh update-header --id $content_id test-data/test-src-1/header-1.json
  local email=''
  local author=''
  read email <test-data/author-email.txt
  read author <test-data/author-name.txt  
  . scripts/dtrack-t2.sh commit --id $content_id --author "$author" --email $email --delete

  echo $content_id $num
}


function do_update
{
  local fifo_name=$namedp_dir/content-ids
  mkfifo $fifo_name
  local idx=''
  local fd_ids_in=''

  for idx in `seq 100`; do
    create_content "0.$RANDOM" $idx >>$fifo_name &
  done

  exec {fd_ids_in}<$fifo_name

  while read content_id data_num ; do
    update_content $content_id $data_num "0.$RANDOM" &  
  done <&$fd_ids_in
  
  while true; do
    wait -n
    local res=$?
    if [ $res == 127 ]; then
      break
    elif [ $res != 0 ]; then
      echo "finished $res"
    fi
  done

  exec {fd_ids_in}<&-

  unlink $fifo_name
}

function main_proc
{
  setup_test
  do_update
}


main_proc

# vi: se ts=2 sw=2 et:
