mkdir -p logs
for file in $(ls test/open_tests); do
    SECONDS=0
    python3 src/final.py test/open_tests/${file} 2>&1 | tee logs/${file}.log
    echo "$file elapsed time: $SECONDS seconds" >> logs/${file}.log
    echo "$file elapsed time: $SECONDS seconds"
done
