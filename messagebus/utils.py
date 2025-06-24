def split_message(message, max_length=3900):
    """
    Split a message into parts < max_length, adding '[X/Y]' prefixes if needed.
    Returns an empty list for empty messages.
    """
    if not message:
        return []

    chunks = []
    prefix_buffer = 10
    while len(message) > max_length - prefix_buffer:
        split_point = message[:max_length - prefix_buffer].rfind('\n')
        if split_point == -1:
            split_point = message[:max_length - prefix_buffer].rfind('. ')
            if split_point == -1:
                split_point = max_length - prefix_buffer
        chunks.append(message[:split_point].rstrip())
        message = message[split_point:].lstrip()
    if message:
        chunks.append(message)

    if len(chunks) == 1:
        return chunks

    total = len(chunks)
    result = []
    for i, chunk in enumerate(chunks):
        prefixed = f"[{i+1}/{total}]\n{chunk}"
        if len(prefixed) > max_length:
            raise ValueError(f"Chunk {i+1} exceeds max length after prefixing")
        result.append(prefixed)
    return result