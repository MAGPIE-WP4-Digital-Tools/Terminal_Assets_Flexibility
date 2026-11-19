from datetime import datetime
from collections import defaultdict

# ======================================================================================================================
#   Convert objects of dictionary to datetime format
# ======================================================================================================================
def convert_datetime_to_str(data):
    if isinstance(data, dict):
        return {key: convert_datetime_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_to_str(item) for item in data]
    elif isinstance(data, datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")  # Adjust the format as needed
    else:
        return data


# ======================================================================================================================
#   Check if there is intersection between two intervals
# ======================================================================================================================
def check_overlapping(range_1, range_2):
    return bool(set(range_1) & set(range_2))
    # range_1_start = range_1[0]
    # range_1_end = range_1[-1]
    # range_2_start = range_2[0]
    # range_2_end = range_2[-1]
    # if (range_2_start <= range_1_start <= range_2_end) or (range_2_start <= range_1_end <= range_2_end):
    #     return True
    # elif (range_1_start < range_2_start) and (range_2_end < range_1_end):
    #     return True
    # else:
    #     return False


# ======================================================================================================================
#   Merge shiftable intervals for similar job
# ======================================================================================================================
def find_and_merge_by_key(dicts, group_by_key, merge_key):
    # Create a dictionary to hold groups of dictionaries
    grouped_dicts = defaultdict(list)

    # Iterate over the list of dictionaries
    for d in dicts:
        # Group dictionaries by the value of the group_by_key
        grouped_dicts[d[group_by_key]].append(d)

    merged_dicts = []

    # Merge dictionaries within each group
    for group in grouped_dicts.values():
        if len(group) > 1:
            merged_dict = {}
            for k in group[0].keys():
                if k == merge_key:
                    # Merge values of the merge_key into a single list
                    merged_dict[k] = []
                    for d in group:
                        merged_dict[k].extend(d[k])
                else:
                    # Assume other values are similar, so just take the value from the first dictionary
                    merged_dict[k] = group[0][k]
            merged_dicts.append(merged_dict)
        else:
            # Add the single unmerged dictionary to the result
            merged_dicts.append(group[0])

    return merged_dicts