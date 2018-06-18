
def split_list_in_batches(lines):
    batches = []
    current_batch = []
    for line in lines:
        if line:
            current_batch.append(line)
        else:
            batches.append(current_batch)
            current_batch = []
    if current_batch:
        batches.append(current_batch)
    return batches