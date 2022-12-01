function sim()
{
    $MASTER/simfactory/bin/sim "$@"
}

function mdbentry()
{
    local machine=$1
    local key=$2
    local value
    value=$($MASTER/simfactory/bin/sim print-mdb-entry ${machine} |grep "^[ \t]*${key}[ \t]*=[ \t]\(.*\)[\t ]*\$" | awk '{print $3}'|sed "s/@USER@/$USER/")
    if [ -z "${value}" ]; then
        echo "Cannot find key $key in machine $machine">&2
        return 1
    else
        echo "$value"
        return 0
    fi
}

function current_machine()
{
    $MASTER/simfactory/bin/sim whoami|grep 'Current machine'|awk '{print $3}'
}
