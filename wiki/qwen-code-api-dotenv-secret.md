# `qwen-code-api/.env.secret`

<h2>Table of contents</h2>

- [About `qwen-code-api/.env.secret`](#about-qwen-code-apienvsecret)
- [`QWEN_CODE_API_HOST_PORT`](#qwen_code_api_host_port)
- [`QWEN_CODE_API_KEY`](#qwen_code_api_key)

## About `qwen-code-api/.env.secret`

`qwen-code-api/.env` is a [`.env` file](./environments.md#env-file) that is on [your VM](./vm) and stores [environment variables](./environments.md#environment-variable) for the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api) deployed there.

Default values: `qwen-code-api/.env.example`.

> [!NOTE]
> The file `qwen-code-api/.env.secret` was added to `qwen-code-api/.gitignore` because you may specify there
> [secrets](./environments.md#secrets) such as the [`QWEN_CODE_API_KEY`](#qwen_code_api_key).

## `QWEN_CODE_API_HOST_PORT`

The [port](./computer-networks.md#port) at which the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api) is available on the [host](./computer-networks.md#host) where it is deployed.

## `QWEN_CODE_API_KEY`

The [API key](./web-api.md#api-key) used to authorize requests to the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api) deployed on your VM.
