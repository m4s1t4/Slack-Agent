schema = [
    {
        "type": "function",
        "function": {
            "name": "get_trello_board_info",
            "description": "Gets all information from a Trello board including lists, cards and members. Shows IDs for lists and cards.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_card_to_list",
            "description": "Creates a new card in a specific Trello list. You can use either the list ID or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "ID or name of the list where the card will be created. Example: '12345' or 'Task List'",
                    },
                    "name": {"type": "string", "description": "Name of the card."},
                    "description": {"type": "string", "description": "Description of the card."},
                },
                "required": ["list_id", "name", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_card",
            "description": "Deletes a Trello card using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "card_id": {
                        "type": "string",
                        "description": "ID of the card to delete. Use get_trello_board_info() to get the IDs.",
                    },
                },
                "required": ["card_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_list_cards",
            "description": "Gets all cards from a specific list. You can use either the list ID or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "string",
                        "description": "ID or name of the list. Example: '12345' or 'Task List'",
                    },
                },
                "required": ["list_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_card_descriptions",
            "description": "Searches for a specific term in the descriptions of all cards on the Trello board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Term to search for in card descriptions"
                    }
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_repos",
            "description": "Lists all repositories of the authenticated GitHub user, showing details like name, privacy, description, stars and last update.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "print_repo_contents",
            "description": "Shows the contents of a GitHub repository recursively, including files and directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository to explore"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path within the repository (optional)",
                        "default": "",
                    },
                    "level": {
                        "type": "integer",
                        "description": "Indentation level (optional)",
                        "default": 0,
                    },
                },
                "required": ["repo_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_branches",
            "description": "Lists all branches of a specific GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository to list branches from"
                    },
                },
                "required": ["repo_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_commit_history",
            "description": "Shows the commit history of a GitHub repository, including details like author, date and message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository to show history from"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of commits to show (optional)",
                        "default": 30,
                    },
                },
                "required": ["repo_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_rag",
            "description": "Makes a query to the RAG (Retrieval-Augmented Generation) system that searches for relevant information in the knowledge base and generates a contextual response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "Text of the question or query to ask the RAG system"
                    }
                },
                "required": ["query_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_card",
            "description": "Gets information about the latest card added to the Trello board, including its name, description, creation date and list where it's located.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]
