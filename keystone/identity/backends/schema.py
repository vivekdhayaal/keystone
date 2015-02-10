USER_TABLE = {
        'user': {
          'hash_key': 'domain_id',
          'range_key': 'name'
        },
        'user_id_index': {
          'hash_key': 'id'
        }
    }

USER_SCHEMA = {
        'id': 'S',
        'name': 'S',
        'password': 'S',
        'extra': 'S',
        'enabled': 'N',
        'domain_id': 'S',
        'default_project_id': 'S'
}

GROUP_TABLE = {
        'group': {
            'hash_key': 'id'
        },
        'user_group': {
            'hash_key': 'user_id',
            'range_key': 'group_id'
        },
        'group_user': {
            'hash_key': 'group_id',
            'range_key': 'user_id'
        }
}
