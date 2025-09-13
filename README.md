# Simple Websocket Subscriber

> Requires [uv](https://docs.astral.sh/uv/)

Configure in `config.toml`:

- \[server] configures the websocket interface
- \[connection] configures the serial interface
- \[subscribers] configures the portst to listen to. The key is a webalias, the value is the port number.

Produced messages are formatted as JSON objects like this:
```JSON
{
  "port": "<port number>",
  "value": "<stringified value>"
}
```

Run using `uv run main.py`

- - -

## Licensing terms
This is free software, licensed under the [Unlicense](https://unlicense.org/). See the [LICENSE](LICENSE) file for details. In short: do whatever you want with it.
