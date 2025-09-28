# umbral

Asynchronous Roblox API wrapper for retrieving Roblox user(s) profile information (avatar, username, friends, etc). 

## Basic features

- **asynchronous** - Built with `asyncio` and `aiohttp` for high performance.
- **rate limiting** - Automatic rate limiting to respect Roblox's absurd API rules.
- **smart caching** - LRU cache with TTL for optimized API usage.
- **performance monitoring** - Built-in metrics and performance tracking.
- **user profiles** - Get detailed user information, followers, following, friends.
- **avatar system** - Retrieve user avatars in multiple sizes and formats.
- **batch operations** - Efficient batch processing for multiple users.

## Plans to add

- [ ] **premium status** - Track if the user(s) exhibits premium (probably will add how long they've been premium as well).
- [ ] **user badges** - Complete badge collection and rarity information.
- [ ] **badge categories** - Organize badges by type and difficulty.
- [ ] **achievement tracking** - Track badge progress and unlock dates.
- [ ] **badge statistics** - Rarity percentages and award counts.
- [ ] **user status** - Online presence and activity status.
- [ ] **user assets** - Inventory items and collections.

## Installation

```bash
pip install git+ssh://git@github.com/orvyne/umbral.git
```

## Documentation

For comprehensive usage examples, advanced features, and detailed API reference, see the [full documentation](DOCUMENTATION.md).

### The documentation covers:
- Complete setup and configuration options.
- Detailed usage examples for all features.
- Error handling and best practices.

## Contributing

Contributions are welcome through official channels only. Please note:

- **Official channels only** - All contributions must be submitted via GitHub pull requests
- **No unauthorized modifications** - Forking for derivative projects or unauthorized changes is prohibited
- **Code style** - Keep your code consistent with the current codebase
- **Stay relevant** - Only contribute features related to Roblox API functionality
- **No irrelevant additions** - Please don't add unrelated features or dependencies
- **Test your changes** - Ensure your code works properly before submitting
- **Keep it minimal** - Follow the project's philosophy of being lightweight and focused

By contributing, you agree to the terms outlined in the [LICENSE](LICENSE) file.

If you're unsure whether a feature fits the project's scope, please open an issue to discuss it first.

## License

This project is licensed under a custom license that allows usage and contributions through official channels while prohibiting unauthorized modifications. See the [LICENSE](LICENSE) file for full terms.

---
For the record, I am not affiliated with Roblox in any way or form.