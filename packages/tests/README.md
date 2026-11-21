# Tests & Verification

Integration tests, benchmark evaluations, and API key smoke tests.

## Anthropic API Key Smoke Test

Use Node.js 22.9 or later. Set `ANTHROPIC_API_KEY` in your shell environment or in the repository root's ignored `.env` file. A key set in the shell takes precedence. From the repository root, run:

```sh
npm --prefix packages/tests test
```

The test calls Anthropic's model-list endpoint without generating a response from a model. It passes when Anthropic accepts the key and exits with an error if the key is missing, is rejected, or the request fails. The test output omits the key and the response body.

## Python Integration & Benchmark Tests

Run pytest from the repository root:

```sh
pytest packages/tests
```
