def create_indexes(db):
    db["Pointers"].create_index(
        "normalized_url",
        unique=True,
        name="unique_pointer_url",
    )

    db["Pointers"].create_index(
        "next_fetch",
        name="pointer_next_fetch",
    )

    db["Topics"].create_index(
        [
            ("userId", 1),
            ("topic", 1),
        ],
        unique=True,
        name="unique_user_topic",
    )

    db["Stories"].create_index(
        [
            ("pointer_id", 1),
            ("link", 1),
        ],
        unique=True,
        name="unique_pointer_story",
    )
