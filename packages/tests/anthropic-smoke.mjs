async function checkAnthropicKey() {
  const apiKey = process.env.ANTHROPIC_API_KEY?.trim();

  if (!apiKey || apiKey === "your_anthropic_api_key_here") {
    console.error("Set ANTHROPIC_API_KEY in your environment or in the root .env file.");
    return 1;
  }

  let response;
  try {
    response = await fetch("https://api.anthropic.com/v1/models?limit=1", {
      headers: {
        "anthropic-version": "2023-06-01",
        "x-api-key": apiKey,
      },
      redirect: "error",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    console.error("Could not reach the Anthropic API. Check your connection and retry.");
    return 1;
  }

  if (response.status === 401 || response.status === 403) {
    console.error(`Anthropic rejected ANTHROPIC_API_KEY (HTTP ${response.status}). Check that the key is valid and has access.`);
    return 1;
  }

  if (!response.ok) {
    console.error(`Anthropic API check failed (HTTP ${response.status}).`);
    return 1;
  }

  console.log("Anthropic API key accepted.");
  return 0;
}

process.exitCode = await checkAnthropicKey();
