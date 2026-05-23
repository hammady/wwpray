<!--
title: 'AWS NodeJS Example'
description: 'This template demonstrates how to deploy a NodeJS function running on AWS Lambda using the traditional Serverless Framework.'
layout: Doc
framework: v3
platform: AWS
language: nodeJS
priority: 1
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->


# Serverless Framework AWS NodeJS Example

This template demonstrates how to deploy a NodeJS function running on AWS Lambda using the traditional Serverless Framework. The deployed function does not include any event definitions as well as any kind of persistence (database). For more advanced configurations check out the [examples repo](https://github.com/serverless/examples/) which includes integrations with SQS, DynamoDB or examples of functions that are triggered in `cron`-like manner. For details about configuration of specific `events`, please refer to our [documentation](https://www.serverless.com/framework/docs/providers/aws/events/).

## Usage

### Deployment

In order to deploy the example, you need to run the following command:

```
$ serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-node-project to stage dev (us-east-1)

✔ Service deployed to stack aws-node-project-dev (112s)

functions:
  hello: aws-node-project-dev-hello (1.5 kB)
```

### Invocation

After successful deployment, you can invoke the deployed function by using the following command:

```bash
serverless invoke --function hello
```

Which should result in response similar to the following:

```json
{
    "statusCode": 200,
    "body": "{\n  \"message\": \"Go Serverless v3.0! Your function executed successfully!\",\n  \"input\": {}\n}"
}
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function hello
```

Which should result in response similar to the following:

```
{
    "statusCode": 200,
    "body": "{\n  \"message\": \"Go Serverless v3.0! Your function executed successfully!\",\n  \"input\": \"\"\n}"
}
```

## Serving the app locally

The frontend lives in `svelte/`. To run it locally:

**1. Install dependencies** (first time only):

```bash
cd svelte
npm install
```

**2. Provide the data file:**

The app reads from `svelte/src/routes/notified.json`. Copy the example file to get started:

```bash
cp svelte/tests/notified-example.json svelte/src/routes/notified.json
```

Or point it at a real generated file if you have one.

**3. Set required environment variables:**

Create `svelte/.env.local` with the following:

```env
# Base URL of the subscriptions API (used by the "Get iqama change alerts" form)
PUBLIC_SUBSCRIPTIONS_BASE_URL=https://your-api-endpoint
```

> `PUBLIC_` prefix means this variable is exposed to the browser. See [SvelteKit env docs](https://kit.svelte.dev/docs/modules#$env-static-public).

**4. Start the dev server:**

```bash
cd svelte
npm run dev
```

The app will be available at **http://localhost:5173**.

**Other useful commands:**

| Command | Description |
|---|---|
| `npm run build` | Build the static site for production |
| `npm run preview` | Preview the production build locally |
| `npm run check` | Type-check the Svelte/TypeScript code |
| `npm run test:unit` | Run unit tests |
