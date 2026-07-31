# Video Summary: AWS re:Invent 2024 – Building State Machines with AWS Step Functions Workflow Studio (API217)

**Video:** https://www.youtube.com/watch?v=o9tn7ZxPYhc
**Speaker:** Ben Moses, Principal Solutions Architect, AWS
**Format:** Lightning talk with live demo

## Overview

This session introduces Workflow Studio, the visual drag-and-drop editor for AWS Step Functions. The talk targets developers and application architects who need to incorporate workflows into their applications, showing how to build complete state machines visually without writing code.

## Step Functions Use Cases

The speaker outlines four major use cases for Step Functions:

1. **Data processing** – Using Distributed Map to run tens of thousands of parallel executions over large datasets.
2. **IT and security automation** – Incident response automation and infrastructure scaling control.
3. **Machine learning** – Orchestrating dataset splitting, training, and automated testing in one place.
4. **Microservices orchestration** – Coordinating processing of event-driven payloads across services.

## Why Workflow Studio

- Workflows can be written as code in Amazon States Language (ASL, JSON-based), but code is hard for business stakeholders (product managers, business teams) to understand.
- Workflow Studio shows the same workflow visually with business-friendly step names, so everyone can follow what's happening.
- **Bidirectional conversion**: build visually, export ASL for version control, modify in code, and re-import for visual editing.

## Live Demo: Image Processing Workflow

The demo builds a workflow that takes an image (generated with Amazon Bedrock) as input, validates it, creates a thumbnail, detects image features, and stores metadata in DynamoDB.

### Editor features shown

- **States palette** – Integrations with 220+ AWS services and access to over 10,000 API actions; flow components for Choice (branching), Parallel, and Map states; a Patterns section with common pre-configured building blocks.
- **Canvas** – Infinitely scrollable, auto-adjusting layout as components are added.
- **Properties panel** – Configure each state; ~15 services offer "optimized" integrations for easier setup, while all services accept standard AWS SDK parameters as JSON.
- **IAM assistance** – Step Functions can propose and create execution roles with the right permissions for most integrated services.

### Data flow (JSONPath)

- The demo uses JSONPath (a newer alternative, **JSONata**, was released shortly before the talk and is recommended once comfortable with the tool).
- **Output path** – Default filter that extracts just the Lambda payload from the full response.
- **Result path** – Preserves the original input object and attaches the state's result as a sub-object (useful for carrying values like table names forward).
- **Result selector** – Cleans up the result to keep only the desired fields (e.g., `image_valid` from the Lambda payload).
- A newer **variables** feature lets you save values as global variables within an execution and reference them later.

### Completed workflow

1. Lambda function extracts/validates image metadata.
2. A **Choice** state routes valid images onward; unsupported types go to a failure branch.
3. DynamoDB **PutItem** stores the initial record (S3 object key as ID).
4. A **Parallel** state runs two branches: a Lambda that creates a thumbnail, and **Amazon Rekognition** called directly (no SDK code) to detect the top image label.
5. DynamoDB item is updated with the Rekognition label (e.g., "nature and outdoors") and the thumbnail's S3 key.

### Debugging and execution history

- Each execution shows a graph view plus a full event table from start to finish.
- Every event is expandable to inspect the exact input, processing, and output of each state — a powerful tool for debugging.

## Key Takeaways

- Complete, multi-service workflows can be built with zero custom code by dragging and dropping service actions.
- Visual design makes workflows easy to share and explain to non-technical stakeholders.
- AWS provides a self-paced hands-on workshop covering basics through advanced topics like input/output filtering.
