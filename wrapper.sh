./SyGuS-solver-mac $1 > tmp1 &
python3 src/final.py $1 > tmp2 &
while true; do
    sleep 1
    if [ -s tmp1 ]; then
        cat tmp1
        break
    fi
    if [ -s tmp2 ]; then
        cat tmp2
        break
    fi
done
kill -- -$$
# trap - SIGTERM && kill -- -$$
# trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
