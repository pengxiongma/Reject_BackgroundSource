import re
from itertools import combinations
from collections import defaultdict, deque
import sys
def parse_line(line):
    "loading events"
    match = re.match(r"(\d+\.\d+):\s*\[(.*)\]", line)
    if not match:
        return None, []
    
    timestamp = float(match.group(1))
    detectors = []
    for item in match.group(2).split("),"):
        item = item.strip(" ()")
        if not item:
            continue
        detector_id, time = map(int, item.split(","))
        detectors.append((detector_id, time))
    
    return timestamp, detectors

def calculate_pair_differences(detectors):
    """difference of time for each pair"""
    pairs = defaultdict(int)
    for (id1, t1), (id2, t2) in combinations(detectors, 2):
        pair_key = tuple(sorted((id1, id2)))
        pairs[pair_key] = t1 - t2
    return pairs
def process_signals(input_lines, threshold=100, history_size=1000, min_pair=1):
    output = []
    prev_pairs = None
    history = deque(maxlen=history_size)  # repeat pairs saved to history

    for idx, line in enumerate(input_lines, 1):
        timestamp, detectors = parse_line(line)
        if not detectors:
            continue

        current_pairs = calculate_pair_differences(detectors)
        is_duplicate = False

        # compare with history 
        for h_idx, historical_pairs in enumerate(history, 1):
            common_pairs = set(current_pairs.keys()) & set(historical_pairs.keys())
            similar_count = sum(
                1 for pair in common_pairs
                if abs(current_pairs[pair] - historical_pairs[pair]) < threshold
            )
            if similar_count >= min_pair:
                is_duplicate = True
                break

        # compare with previous event
        if not is_duplicate and prev_pairs:
            common_pairs = set(current_pairs.keys()) & set(prev_pairs.keys())
            similar_count = sum(
                1 for pair in common_pairs
                if abs(current_pairs[pair] - prev_pairs[pair]) < threshold
            )
            if similar_count >= min_pair:
                is_duplicate = True

        if is_duplicate:
            # only save repeating  pairs into history
            history.append(current_pairs)
            continue

        # save event
        output.append(line)
        prev_pairs = current_pairs

    return output


def main():
    input_file = sys.argv[1]  # input file
    output_file = sys.argv[2] #
    
    try:
        with open(input_file, 'r') as f:
            input_lines = [line.strip() for line in f.readlines()]
        
        result = process_signals(input_lines)
        
        with open(output_file, 'w') as f:
            for line in result:
                f.write(line + "\n")
        print(f"Done, results saved into {output_file}")
        print(f"lines of raw file: {len(input_lines)}，left lines: {len(result)}")
    
    except FileNotFoundError:
        print(f"Error：not find {input_file}")
    except Exception as e:
        print(f"error in processing: {str(e)}")

if __name__ == "__main__":
    main()

