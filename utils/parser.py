def parse_bid(message: str):

    message = message.strip()

    if not message.isdigit():
        return None

    return int(message)
