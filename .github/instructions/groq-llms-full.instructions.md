# https://console.groq.com llms-full.txt

## 🗂️ LlamaIndex 🦙

URL: https://console.groq.com/docs/llama-index

## 🗂️ LlamaIndex 🦙

<br />

[LlamaIndex](https://www.llamaindex.ai/) is a data framework for LLM-based applications that benefit from context augmentation, such as Retrieval-Augmented Generation (RAG) systems. LlamaIndex provides the essential abstractions to more easily ingest, structure, and access private or domain-specific data, resulting in safe and reliable injection into LLMs for more accurate text generation.

<br />

For more information, read the LlamaIndex Groq integration documentation for [Python](https://docs.llamaindex.ai/en/stable/examples/llm/groq.html) and [JavaScript](https://ts.llamaindex.ai/modules/llms/available_llms/groq).

---

## Rate Limits

URL: https://console.groq.com/docs/rate-limits

## Rate Limits

Rate limits act as control measures to regulate how frequently users and applications can access our API within specified timeframes. These limits help ensure service stability, fair access, and protection
against misuse so that we can serve reliable and fast inference for all.

### Understanding Rate Limits
Rate limits are measured in:
- **RPM:** Requests per minute
- **RPD:** Requests per day
- **TPM:** Tokens per minute
- **TPD:** Tokens per day
- **ASH:** Audio seconds per hour
- **ASD:** Audio seconds per day

Rate limits apply at the organization level, not individual users. You can hit any limit type depending on which threshold you reach first.

**Example:** Let's say your RPM =50 and your TPM =200K. If you were to send50 requests with only100 tokens within a minute, you would reach your limit even though you did not send200K tokens within those
50 requests.

## Rate Limits
The following is a high level summary and there may be exceptions to these limits. You can view the current, exact rate limits for your organization on the [limits page](/settings/limits) in your account settings.

## Rate Limit Headers
In addition to viewing your limits on your account's [limits](https://console.groq.com/settings/limits) page, you can also view rate limit information such as remaining requests and tokens in HTTP response 
headers as follows:

The following headers are set (values are illustrative):

## Handling Rate Limits
When you exceed rate limits, our API returns a `429 Too Many Requests` HTTP status code.

**Note**: `retry-after` is only set if you hit the rate limit and status code429 is returned. The other headers are always included.

---

## Initialize the Groq client

URL: https://console.groq.com/docs/speech-to-text/scripts/transcription.py

```python
import os
import json
from groq import Groq

# Initialize the Groq client
client = Groq()

# Specify the path to the audio file
filename = os.path.dirname(__file__) + "/YOUR_AUDIO.wav" # Replace with your audio file!

# Open the audio file
with open(filename, "rb") as file:
    # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
        file=file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        prompt="Specify context or spelling", # Optional
        response_format="verbose_json", # Optional
        timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
        language="en", # Optional
        temperature=0.0 # Optional
    )
    # To print only the transcription text, you'd use print(transcription.text) (here we're printing the entire transcription object to access timestamps)
    print(json.dumps(transcription, indent=2, default=str))
```

---

## Speech To Text: Transcription (js)

URL: https://console.groq.com/docs/speech-to-text/scripts/transcription

import fs from "fs";
import Groq from "groq-sdk";

// Initialize the Groq client
const groq = new Groq();

async function main() {
 // Create a transcription job
 const transcription = await groq.audio.transcriptions.create({
 file: fs.createReadStream("YOUR_AUDIO.wav"), // Required path to audio file - replace with your audio file!
 model: "whisper-large-v3-turbo", // Required model to use for transcription
 prompt: "Specify context or spelling", // Optional
 response_format: "verbose_json", // Optional
 timestamp_granularities: ["word", "segment"], // Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
 language: "en", // Optional
 temperature:0.0, // Optional
 });
 // To print only the transcription text, you'd use console.log(transcription.text); (here we're printing the entire transcription object to access timestamps)
 console.log(JSON.stringify(transcription, null,2));
}
main();

---

## Initialize the Groq client

URL: https://console.groq.com/docs/speech-to-text/scripts/translation.py

```python
import os
from groq import Groq

# Initialize the Groq client
client = Groq()

# Specify the path to the audio file
filename = os.path.dirname(__file__) + "/sample_audio.m4a" # Replace with your audio file!

# Open the audio file
with open(filename, "rb") as file:
    # Create a translation of the audio file
    translation = client.audio.translations.create(
        file=(filename, file.read()), # Required audio file
        model="whisper-large-v3", # Required model to use for translation
        prompt="Specify context or spelling", # Optional
        language="en", # Optional ('en' only)
        response_format="json", # Optional
        temperature=0.0 # Optional
    )
    # Print the translation text
    print(translation.text)
```

---

## Speech To Text: Translation (js)

URL: https://console.groq.com/docs/speech-to-text/scripts/translation

import fs from "fs";
import Groq from "groq-sdk";

// Initialize the Groq client
const groq = new Groq();
async function main() {
 // Create a translation job
 const translation = await groq.audio.translations.create({
 file: fs.createReadStream("sample_audio.m4a"), // Required path to audio file - replace with your audio file!
 model: "whisper-large-v3", // Required model to use for translation
 prompt: "Specify context or spelling", // Optional
 language: "en", // Optional ('en' only)
 response_format: "json", // Optional
 temperature:0.0, // Optional
 });
 // Log the transcribed text
 console.log(translation.text);
}
main();

---

## Speech to Text

URL: https://console.groq.com/docs/speech-to-text

## Speech to Text
Groq API is the fastest speech-to-text solution available, offering OpenAI-compatible endpoints that
enable near-instant transcriptions and translations. With Groq API, you can integrate high-quality audio 
processing into your applications at speeds that rival human interaction.

## API Endpoints

We support two endpoints:

| Endpoint | Usage | API Endpoint |
|----------------|--------------------------------|-------------------------------------------------------------|
| Transcriptions | Convert audio to text | `https://api.groq.com/openai/v1/audio/transcriptions` |
| Translations | Translate audio to English text| `https://api.groq.com/openai/v1/audio/translations` |

## Supported Models

| Model ID | Model | Supported Language(s) | Description |
|-----------------------------|----------------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `whisper-large-v3-turbo` | Whisper Large V3 Turbo | Multilingual | A fine-tuned version of a pruned Whisper Large V3 designed for fast, multilingual transcription tasks. |
| `distil-whisper-large-v3-en` | Distil-Whisper English | English-only | A distilled, or compressed, version of OpenAI's Whisper model, designed to provide faster, lower cost English speech recognition while maintaining comparable accuracy. |
| `whisper-large-v3` | Whisper large-v3 | Multilingual | Provides state-of-the-art performance with high accuracy for multilingual transcription and translation tasks. |

  
## Which Whisper Model Should You Use?
Having more choices is great, but let's try to avoid decision paralysis by breaking down the tradeoffs between models to find the one most suitable for
your applications: 
- If your application is error-sensitive and requires multilingual support, use `whisper-large-v3`. 
- If your application is less sensitive to errors and requires English only, use `distil-whisper-large-v3-en`. 
- If your application requires multilingual support and you need the best price for performance, use `whisper-large-v3-turbo`. 

The following table breaks down the metrics for each model.
| Model | Cost Per Hour | Language Support | Transcription Support | Translation Support | Real-time Speed Factor | Word Error Rate |
|--------|--------|--------|--------|--------|--------|--------|
| `whisper-large-v3` | $0.111 | Multilingual | Yes | Yes |189 |10.3% |
| `whisper-large-v3-turbo` | $0.04 | Multilingual | Yes | No |216 |12% |
| `distil-whisper-large-v3-en` | $0.02 | English only | Yes | No |250 |13% |


## Working with Audio Files

### Audio File Limitations

* Max File Size: 40 MB (free tier), 100MB (dev tier)
* Max Attachment File Size: 25 MB. If you need to process larger files, use the `url` parameter to specify a url to the file instead.
* Minimum File Length: 0.01 seconds
* Minimum Billed Length: 10 seconds. If you submit a request less than this, you will still be billed for 10 seconds.
* Supported File Types: Either a URL or a direct file upload for `flac`, `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `ogg`, `wav`, `webm`
* Single Audio Track: Only the first track will be transcribed for files with multiple audio tracks. (e.g. dubbed video)
* Supported Response Formats: `json`, `verbose_json`, `text`
* Supported Timestamp Granularities: `segment`, `word`

### Audio Request Examples

I am on **free tier** and want to transcribe an audio file:
 - Use the `file` parameter to add a local file up to 25 MB.
 - Use the `url` parameter to add a url to a file up to 40 MB.

I am on **dev tier** and want to transcribe an audio file:
 - Use the `file` parameter to add a local file up to 25 MB.
 - Use the `url` parameter to add a url to a file up to 100 MB.

If audio files exceed these limits, you may receive a [413 error](/docs/errors).

### Audio Preprocessing
Our speech-to-text models will downsample audio to 16KHz mono before transcribing, which is optimal for speech recognition. This preprocessing can be performed client-side if your original file is extremely 
large and you want to make it smaller without a loss in quality (without chunking, Groq API speech-to-text endpoints accept up to 40MB for free tier and 100MB for [dev tier](/settings/billing)). We recommend FLAC for lossless compression.

The following `ffmpeg` command can be used to reduce file size:

```shell
ffmpeg \
 -i <your file> \
 -ar 16000 \
 -ac 1 \
 -map0:a \
 -c:a flac \
 <output file name>.flac
```

### Working with Larger Audio Files
For audio files that exceed our size limits or require more precise control over transcription, we recommend implementing audio chunking. This process involves:
1. Breaking the audio into smaller, overlapping segments
2. Processing each segment independently
3. Combining the results while handling overlapping

[To learn more about this process and get code for your own implementation, see the complete audio chunking tutorial in our Groq API Cookbook.](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/audio-chunking)

## Using the API 
The following are request parameters you can use in your transcription and translation requests:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | `string` | Required unless using `url` instead | The audio file object for direct upload to translate/transcribe. |
| `url` | `string` | Required unless using `file` instead | The audio URL to translate/transcribe (supports Base64URL). |
| `language` | `string` | Optional | The language of the input audio. Supplying the input language in ISO-639-1 (i.e. `en, `tr`) format will improve accuracy and latency.<br/><br/>The translations endpoint only supports 'en' as a parameter option. |
| `model` | `string` | Required | ID of the model to use.|
| `prompt` | `string` | Optional | Prompt to guide the model's style or specify how to spell unfamiliar words. (limited to 224 tokens) |
| `response_format` | `string` | json | Define the output response format.<br/><br/>Set to `verbose_json` to receive timestamps for audio segments.<br/><br/>Set to `text` to return a text response. |
| `temperature` | `float` |0 | The temperature between 0 and 1. For translations and transcriptions, we recommend the default value of 0. |
| `timestamp_granularities[]` | `array` | segment | The timestamp granularities to populate for this transcription. `response_format` must be set `verbose_json` to use timestamp granularities.<br/><br/>Either or both of `word` and `segment` are supported. <br/><br/>`segment` returns full metadata and `word` returns only word, start, and end timestamps. To get both word-level timestamps and full segment metadata, include both values in the array. |

### Example Usage of Transcription Endpoint 
The transcription endpoint allows you to transcribe spoken words in audio or video files.

#### Python
The Groq SDK package can be installed using the following command:
```shell
pip install groq
```

The following code snippet demonstrates how to use Groq API to transcribe an audio file in Python:
```python
import groq

# Your code here
```

#### JavaScript
The Groq SDK package can be installed using the following command:
```shell
npm install @groq/groq-sdk
```

The following code snippet demonstrates how to use Groq API to transcribe an audio file in JavaScript:
```javascript
// Your code here
```

#### cURL
The following is an example cURL request:
```shell
curl -X POST \
  https://api.groq.com/openai/v1/audio/transcriptions \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/audio/file.wav' \
  -F 'model=whisper-large-v3' \
  -F 'language=en'
```

The following is an example response:
```json
{
 "text": "Your transcribed text appears here...",
 "x_groq": {
 "id": "req_unique_id"
 }
}
```

### Example Usage of Translation Endpoint
The translation endpoint allows you to translate spoken words in audio or video files to English.

#### Python
The Groq SDK package can be installed using the following command:
```shell
pip install groq
```

The following code snippet demonstrates how to use Groq API to translate an audio file in Python:
```python
import groq

# Your code here
```

#### JavaScript
The Groq SDK package can be installed using the following command:
```shell
npm install @groq/groq-sdk
```

The following code snippet demonstrates how to use Groq API to translate an audio file in JavaScript:
```javascript
// Your code here
```

#### cURL
The following is an example cURL request:
```shell
curl -X POST \
  https://api.groq.com/openai/v1/audio/translations \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/audio/file.wav' \
  -F 'model=whisper-large-v3' \
  -F 'language=en'
```

The following is an example response:
```json
{
 "text": "Your translated text appears here...",
 "x_groq": {
 "id": "req_unique_id"
 }
}
```

## Understanding Metadata Fields
When working with Groq API, setting `response_format` to `verbose_json` outputs each segment of transcribed text with valuable metadata that helps us understand the quality and characteristics of our 
transcription, including `avg_logprob`, `compression_ratio`, and `no_speech_prob`.

This information can help us with debugging any transcription issues. Let's examine what this metadata tells us using a real 
example:
```json
{
 "id": 8,
 "seek": 3000,
 "start": 43.92,
 "end": 50.16,
 "text": " document that the functional specification that you started to read through that isn't just the",
 "tokens": [51061, 4166, 300, 264, 11745, 31256],
 "temperature": 0,
 "avg_logprob": -0.097569615,
 "compression_ratio": 1.6637554,
 "no_speech_prob": 0.012814695
}
```
As shown in the above example, we receive timing information as well as quality indicators. Let's gain a better understanding of what each field means:
- `id: 8`: The 9th segment in the transcription (counting begins at 0)
- `seek`: Indicates where in the audio file this segment begins (3000 in this case)
- `start` and `end` timestamps: Tell us exactly when this segment occurs in the audio (43.92 to 50.16 seconds in our example)
- `avg_logprob` (Average Log Probability): -0.097569615 in our example indicates very high confidence. Values closer to 0 suggest better confidence, while more negative values (like -0.5 or lower) might 
indicate transcription issues.
- `no_speech_prob` (No Speech Probability): 0.012814695 is very low, suggesting this is definitely speech. Higher values (closer to 1) would indicate potential silence or non-speech audio.
- `compression_ratio`: 1.6637554 is a healthy value, indicating normal speech patterns. Unusual values (very high or low) might suggest issues with speech clarity or word boundaries.

### Using Metadata for Debugging
When troubleshooting transcription issues, look for these patterns:
- Low Confidence Sections: If `avg_logprob` drops significantly (becomes more negative), check for background noise, multiple speakers talking simultaneously, unclear pronunciation, and strong accents. 
Consider cleaning up the audio in these sections or adjusting chunk sizes around problematic chunk boundaries.
- Non-Speech Detection: High `no_speech_prob` values might indicate silence periods that could be trimmed, background music or noise, or non-verbal sounds being misinterpreted as speech. Consider noise 
reduction when preprocessing.
- Unusual Speech Patterns: Unexpected `compression_ratio` values can reveal stuttering or word repetition, speaker talking unusually fast or slow, or audio quality issues affecting word separation.

### Quality Thresholds and Regular Monitoring
We recommend setting acceptable ranges for each metadata value we reviewed above and flagging segments that fall outside these ranges to be able to identify and adjust preprocessing or chunking strategies for 
flagged sections.

By understanding and monitoring these metadata values, you can significantly improve your transcription quality and quickly identify potential issues in your audio processing pipeline.

## Prompting Guidelines
 The prompt parameter (max 224 tokens) helps provide context and maintain a consistent output style.
 Unlike chat completion prompts, these prompts only guide style and context, not specific actions.

### Best Practices
- Provide relevant context about the audio content, such as the type of conversation, topic, or 
speakers involved.
- Use the same language as the language of the audio file.
- Steer the model's output by denoting proper spellings or emulate a specific writing style or tone.
- Keep the prompt concise and focused on stylistic guidance.

We can't wait to see what you build!

---

## CrewAI + Groq: High-Speed Agent Orchestration

URL: https://console.groq.com/docs/crewai

## CrewAI + Groq: High-Speed Agent Orchestration

CrewAI is a framework that enables the orchestration of multiple AI agents with specific roles, tools, and goals as a cohesive team to accomplish complex tasks and create sophisticated workflows.

Agentic workflows require fast inference due to their complexity. Groq's fast inference optimizes response times for CrewAI agent teams, enabling rapid autonomous decision-making and collaboration for:

- **Fast Agent Interactions:** Leverage Groq's fast inference speeds via Groq API for efficient agent communication
- **Reliable Performance:** Consistent response times across agent operations
- **Scalable Multi-Agent Systems:** Run multiple agents in parallel without performance degradation
- **Simple Integration:** Get started with just a few lines of code

### Python Quick Start (2 minutes to hello world)
####1. Install the required packages:
```bash
pip install crewai groq
```
####2. Configure your Groq API key:
```bash
export GROQ_API_KEY="your-api-key"
```
####3. Create your first Groq-powered CrewAI agent:

In CrewAI, **agents** are autonomous entities you can design to perform specific roles and achieve particular goals while **tasks** are specific assignments given to agents that detail the actions they
need to perform to achieve a particular goal. Tools can be assigned as tasks.

```python
from crewai import Agent, Task, Crew, LLM

# Initialize Large Language Model (LLM) of your choice (see all models on our Models page)
llm = LLM(model="groq/llama-3.1-70b-versatile")

# Create your CrewAI agents with role, main goal/objective, and backstory/personality
summarizer = Agent(
 role='Documentation Summarizer', # Agent's job title/function
 goal='Create concise summaries of technical documentation', # Agent's main objective
 backstory='Technical writer who excels at simplifying complex concepts', # Agent's background/expertise
 llm=llm, # LLM that powers your agent
 verbose=True # Show agent's thought process as it completes its task
)

translator = Agent(
 role='Technical Translator',
 goal='Translate technical documentation to other languages',
 backstory='Technical translator specializing in software documentation',
 llm=llm,
 verbose=True
)

# Define your agents' tasks
summary_task = Task(
 description='Summarize this React hook documentation:\n\nuseFetch(url) is a custom hook for making HTTP requests. It returns { data, loading, error } and automatically handles loading states.',
 expected_output="A clear, concise summary of the hook's functionality",
 agent=summarizer # Agent assigned to task
)

translation_task = Task(
 description='Translate the summary to Turkish',
 expected_output="Turkish translation of the hook documentation",
 agent=translator,
 dependencies=[summary_task] # Must run after the summary task
)

# Create crew to manage agents and task workflow
crew = Crew(
 agents=[summarizer, translator], # Agents to include in your crew
 tasks=[summary_task, translation_task], # Tasks in execution order
 verbose=True
)

result = crew.kickoff()
print(result)
```

When you run the above code, you'll see that you've created a summarizer agent and a translator agent working together to summarize and translate documentation! This is a simple example to get you started,
but the agents are also able to use tools, which is a powerful combination for building agentic workflows.

**Challenge**: Update the code to add an agent that will write up documentation for functions its given by the user! 


### Advanced Model Configuration
For finer control over your agents' responses, you can easily configure additional model parameters. These settings help you balance between creative and deterministic outputs, control response length, 
and manage token usage:
```python
llm = LLM(
 model="llama-3.1-70b-versatile",
 temperature=0.5,
 max_completion_tokens=1024,
 top_p=0.9,
 stop=None,
 stream=False,
)
```


For more robust documentation and further resources, including using CrewAI agents with tools for building a powerful agentic workflow, see the following:
- [Official Documentation: CrewAI](https://docs.crewai.com/concepts/llms)
- [Groq API Cookbook: CrewAI Mixture of Agents Tutorial](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/crewai-mixture-of-agents)
- [Webinar: Build CrewAI Agents with Groq](https://youtu.be/Q3fh0sWVRX4?si=fhMLPsBF5OBiMfjD)

---

## Tool Use: Step2 (js)

URL: https://console.groq.com/docs/tool-use/scripts/step2

```javascript
// imports calculate function from step1
async function runConversation(userPrompt) {
  const messages = [
    {
      role: "system",
      content: "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results."
    },
    {
      role: "user",
      content: userPrompt,
    }
  ];

  const tools = [
    {
      type: "function",
      function: {
        name: "calculate",
        description: "Evaluate a mathematical expression",
        parameters: {
          type: "object",
          properties: {
            expression: {
              type: "string",
              description: "The mathematical expression to evaluate",
            }
          },
          required: ["expression"],
        },
      },
    }
  ];

  const response = await client.chat.completions.create({
    model: MODEL,
    messages: messages,
    stream: false,
    tools: tools,
    tool_choice: "auto",
    max_completion_tokens: 4096
  });

  const responseMessage = response.choices[0].message;
  const toolCalls = responseMessage.tool_calls;

  if (toolCalls) {
    const availableFunctions = {
      "calculate": calculate,
    };

    messages.push(responseMessage);

    for (const toolCall of toolCalls) {
      const functionName = toolCall.function.name;
      const functionToCall = availableFunctions[functionName];
      const functionArgs = JSON.parse(toolCall.function.arguments);
      const functionResponse = functionToCall(functionArgs.expression);

      messages.push({
        tool_calls_id: toolCall.id,
        role: "tool",
        name: functionName,
        content: functionResponse,
      });
    }

    const secondResponse = await client.chat.completions.create({
      model: MODEL,
      messages: messages
    });

    return secondResponse.choices[0].message.content;
  }

  return responseMessage.content;
}

const userPrompt = "What is 25 * 4 + 10?";
runConversation(userPrompt).then(console.log).catch(console.error);
```

---

## imports calculate function from step 1

URL: https://console.groq.com/docs/tool-use/scripts/step2.py

```python
# imports calculate function from step1
def run_conversation(user_prompt):
    # Initialize the conversation with system and user messages
    messages=[
        {
            "role": "system",
            "content": "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results."
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    # Define the available tools (i.e. functions) for our model to use
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ]
    # Make the initial API call to Groq
    response = client.chat.completions.create(
        model=MODEL, # LLM to use
        messages=messages, # Conversation history
        stream=False,
        tools=tools, # Available tools (i.e. functions) for our LLM to use
        tool_choice="auto", # Let our LLM decide when to use tools
        max_completion_tokens=4096 # Maximum number of tokens to allow in our response
    )
    # Extract the response and any tool calls responses
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        # Define the available tools that can be called by the LLM
        available_functions = {
            "calculate": calculate,
        }
        # Add the LLM's response to the conversation
        messages.append(response_message)

        # Process each tool calls
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            # Call the tool and get the response
            function_response = function_to_call(
                expression=function_args.get("expression")
            )
            # Add the tool response to the conversation
            messages.append(
                {
                    "tool_calls_id": tool_call.id, 
                    "role": "tool", # Indicates this message is from tool use
                    "name": function_name,
                    "content": function_response,
                }
            )
            # Make a second API call with the updated conversation
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            # Return the final response
            return second_response.choices[0].message.content
# Example usage
user_prompt = "What is25 *4 +10?"
print(run_conversation(user_prompt))
```

---

## Tool Use: Routing.doc (ts)

URL: https://console.groq.com/docs/tool-use/scripts/routing.doc

```javascript
import Groq from "groq-sdk";

const groq = new Groq();

// Define models
const ROUTING_MODEL = "llama3-70b-8192";
const TOOL_USE_MODEL = "llama-3.3-70b-versatile";
const GENERAL_MODEL = "llama3-70b-8192";

function calculate(expression: string): string {
  try {
    // Note: Using this method to evaluate expressions in JavaScript can be dangerous.
    // In a production environment, you should use a safer alternative.
    const result = new Function(`return ${expression}`)();
    return JSON.stringify({ result });
  } catch (error) {
    return JSON.stringify({ error: `Invalid expression: ${error}` });
  }
}

async function routeQuery(query: string): Promise<string> {
  const routingPrompt = `
    Given the following user query, determine if any tools are needed to answer it.
    If a calculation tool is needed, respond with 'TOOL: CALCULATE'.
    If no tools are needed, respond with 'NO TOOL'.

    User query: ${query}

    Response:
  `;

  const response = await groq.chat.completions.create({
    model: ROUTING_MODEL,
    messages: [
      {
        role: "system",
        content:
          "You are a routing assistant. Determine if tools are needed based on the user query.",
      },
      { role: "user", content: routingPrompt },
    ],
    max_completion_tokens: 20,
  });

  const routingDecision = response.choices[0].message?.content?.trim();

  if (routingDecision?.includes("TOOL: CALCULATE")) {
    return "calculate tool needed";
  }

  return "no tool needed";
}

async function runWithTool(query: string): Promise<string> {
  const messages: Groq.Chat.Completions.ChatCompletionMessageParam[] = [
    {
      role: "system",
      content:
        "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results.",
    },
    {
      role: "user",
      content: query,
    },
  ];
  const tools: Groq.Chat.Completions.ChatCompletionTool[] = [
    {
      type: "function",
      function: {
        name: "calculate",
        description: "Evaluate a mathematical expression",
        parameters: {
          type: "object",
          properties: {
            expression: {
              type: "string",
              description: "The mathematical expression to evaluate",
            },
          },
          required: ["expression"],
        },
      },
    },
  ];
  const response = await groq.chat.completions.create({
    model: TOOL_USE_MODEL,
    messages: messages,
    tools: tools,
    tool_choice: "auto",
    max_completion_tokens: 4096,
  });
  const responseMessage = response.choices[0].message;
  const toolCalls = responseMessage.tool_calls;
  if (toolCalls) {
    messages.push(responseMessage);
    for (const toolCall of toolCalls) {
      const functionArgs = JSON.parse(toolCall.function.arguments);
      const functionResponse = calculate(functionArgs.expression);
      messages.push({
        tool_calls_id: toolCall.id,
        role: "tool",
        content: functionResponse,
      });
    }
    const secondResponse = await groq.chat.completions.create({
      model: TOOL_USE_MODEL,
      messages: messages,
    });
    return secondResponse.choices[0].message?.content ?? "";
  }
  return responseMessage.content ?? "";
}

async function runGeneral(query: string): Promise<string> {
  const response = await groq.chat.completions.create({
    model: GENERAL_MODEL,
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: query },
    ],
  });
  return response.choices[0]?.message?.content ?? "";
}

export async function processQuery(query: string): Promise<{
  query: string;
  route: string;
  response: string;
}> {
  const route = await routeQuery(query);
  let response: string | null = null;
  if (route === "calculate tool needed") {
    response = await runWithTool(query);
  } else {
    response = await runGeneral(query);
  }

  return {
    query: query,
    route: route,
    response: response,
  };
}

// Example usage
async function main() {
  const queries = [
    "What is the capital of the Netherlands?",
    "Calculate 25 * 4 + 10",
  ];

  for (const query of queries) {
    try {
      const result = await processQuery(query);
      console.log(`Query: ${result.query}`);
      console.log(`Route: ${result.route}`);
      console.log(`Response: ${result.response}\n`);
    } catch (error) {
      console.error(`Error processing query "${query}":`, error);
    }
  }
}

main();
```

---

## Define the tool schema

URL: https://console.groq.com/docs/tool-use/scripts/instructor.py

```python
import instructor
from pydantic import BaseModel, Field
from groq import Groq

# Define the tool schema
tool_schema = {
 "name": "get_weather_info",
 "description": "Get the weather information for any location.",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The location for which we want to get the weather information (e.g., New York)"
 }
 },
 "required": ["location"]
 }
}

# Define the Pydantic model for the tool calls
class ToolCall(BaseModel):
 input_text: str = Field(description="The user's input text")
 tool_name: str = Field(description="The name of the tool to call")
 tool_parameters: str = Field(description="JSON string of tool parameters")

class ResponseModel(BaseModel):
 tool_calls: list[ToolCall]

# Patch Groq() with instructor
client = instructor.from_groq(Groq(), mode=instructor.Mode.JSON)

def run_conversation(user_prompt):
 # Prepare the messages
 messages = [
 {
 "role": "system",
 "content": f"You are an assistant that can use tools. You have access to the following tool: {tool_schema}"
 },
 {
 "role": "user",
 "content": user_prompt,
 }
 ]

 # Make the Groq API call
 response = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 response_model=ResponseModel,
 messages=messages,
 temperature=0.5,
 max_completion_tokens=1000,
 )

 return response.tool_calls

# Example usage
user_prompt = "What's the weather like in San Francisco?"
tool_calls = run_conversation(user_prompt)

for call in tool_calls:
 print(f"Input: {call.input_text}")
 print(f"Tool: {call.tool_name}")
 print(f"Parameters: {call.tool_parameters}")
 print()
```

---

## Tool Use: Step2.doc (ts)

URL: https://console.groq.com/docs/tool-use/scripts/step2.doc

```javascript
// imports calculate function from step1
async function runConversation(userPrompt) {
  const messages = [
    {
      role: "system",
      content: "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results."
    },
    {
      role: "user",
      content: userPrompt
    }
  ];
  
  const tools = [
    {
      type: "function",
      function: {
        name: "calculate",
        description: "Evaluate a mathematical expression",
        parameters: {
          type: "object",
          properties: {
            expression: {
              type: "string",
              description: "The mathematical expression to evaluate"
            }
          },
          required: ["expression"]
        }
      }
    }
  ];
  
  const response = await client.chat.completions.create({
    model: MODEL,
    messages: messages,
    stream: false,
    tools: tools,
    tool_choice: "auto",
    max_completion_tokens: 4096
  });
  
  const responseMessage = response.choices[0].message;
  const toolCalls = responseMessage.tool_calls;
  
  if (toolCalls) {
    const availableFunctions = {
      "calculate": calculate
    };
    
    messages.push(responseMessage);
    
    for (const toolCall of toolCalls) {
      const functionName = toolCall.function.name;
      const functionToCall = availableFunctions[functionName];
      const functionArgs = JSON.parse(toolCall.function.arguments);
      const functionResponse = functionToCall(functionArgs.expression);
      
      messages.push({
        tool_calls_id: toolCall.id,
        role: "tool",
        content: functionResponse
      });
    }
    
    const secondResponse = await client.chat.completions.create({
      model: MODEL,
      messages: messages
    });
    
    return secondResponse.choices[0].message.content;
  }
  
  return responseMessage.content;
}
  
const userPrompt = "What is 25 * 4 + 10?";
runConversation(userPrompt).then(console.log).catch(console.error);
```

---

## Tool Use: Parallel.doc (ts)

URL: https://console.groq.com/docs/tool-use/scripts/parallel.doc

import Groq from "groq-sdk";

// Initialize Groq client
const groq = new Groq();
const model = "llama-3.3-70b-versatile";

type ToolFunction = (location: string) => string;

// Define weather tools
const getTemperature: ToolFunction = (location: string) => {
 // This is a mock tool/function. In a real scenario, you would call a weather API.
 const temperatures: Record<string, string> = {
 "New York": "22°C",
 "London": "18°C",
 "Tokyo": "26°C",
 "Sydney": "20°C",
 };
 return temperatures[location] || "Temperature data not available";
};

const getWeatherCondition: ToolFunction = (location: string) => {
 // This is a mock tool/function. In a real scenario, you would call a weather API.
 const conditions: Record<string, string> = {
 "New York": "Sunny",
 "London": "Rainy",
 "Tokyo": "Cloudy",
 "Sydney": "Clear",
 };
 return conditions[location] || "Weather condition data not available";
};

// Define system messages and tools
const messages: Groq.Chat.Completions.ChatCompletionMessageParam[] = [
 { role: "system", content: "You are a helpful weather assistant." },
 {
 role: "user",
 content:
 "What's the weather and temperature like in New York and London? Respond with one sentence for each city. Use tools to get the current weather and temperature.",
 },
];

const tools: Groq.Chat.Completions.ChatCompletionTool[] = [
 {
 type: "function",
 function: {
 name: "getTemperature",
 description: "Get the temperature for a given location",
 parameters: {
 type: "object",
 properties: {
 location: {
 type: "string",
 description: "The name of the city",
 },
 },
 required: ["location"],
 },
 },
 },
 {
 type: "function",
 function: {
 name: "getWeatherCondition",
 description: "Get the weather condition for a given location",
 parameters: {
 type: "object",
 properties: {
 location: {
 type: "string",
 description: "The name of the city",
 },
 },
 required: ["location"],
 },
 },
 },
];

// Make the initial request
export async function runWeatherAssistant() {
 try {
 const response = await groq.chat.completions.create({
 model,
 messages,
 tools,
 temperature:0.5, // Keep temperature between0.0 -0.5 for best tool calling results
 tool_choice: "auto",
 max_completion_tokens:4096,
 });

 const responseMessage = response.choices[0].message;
 console.log("Response message:", JSON.stringify(responseMessage, null,2));

 const toolCalls = responseMessage.tool_calls || [];

 // Process tool calls
 messages.push(responseMessage);

 const availableFunctions: Record<string, ToolFunction> = {
 getTemperature,
 getWeatherCondition,
 };

 for (const toolCall of toolCalls) {
 const functionName = toolCall.function.name;
 const functionToCall = availableFunctions[functionName];
 const functionArgs = JSON.parse(toolCall.function.arguments);
 // Call corresponding tool function if it exists
 const functionResponse = functionToCall?.(functionArgs.location);

 if (functionResponse) {
 messages.push({
 role: "tool",
 content: functionResponse,
 tool_call_id: toolCall.id,
 });
 }
 }

 // Make the final request with tool call results
 const finalResponse = await groq.chat.completions.create({
 model,
 messages,
 tools,
 temperature:0.5,
 tool_choice: "auto",
 max_completion_tokens:4096,
 });

 return finalResponse.choices[0].message.content;
 } catch (error) {
 console.error("An error occurred:", error);
 throw error; // Re-throw the error so it can be caught by the caller
 }
}

runWeatherAssistant()
 .then((result) => {
 console.log("Final result:", result);
 })
 .catch((error) => {
 console.error("Error in main execution:", error);
 });

---

## Tool Use: Parallel (js)

URL: https://console.groq.com/docs/tool-use/scripts/parallel

```javascript
import Groq from "groq-sdk";

// Initialize Groq client
const groq = new Groq();
const model = "llama-3.3-70b-versatile";

// Define weather tools
function getTemperature(location) {
  // This is a mock tool/function. In a real scenario, you would call a weather API.
  const temperatures = {"New York": "22°C", "London": "18°C", "Tokyo": "26°C", "Sydney": "20°C"};
  return temperatures[location] || "Temperature data not available";
}

function getWeatherCondition(location) {
  // This is a mock tool/function. In a real scenario, you would call a weather API.
  const conditions = {"New York": "Sunny", "London": "Rainy", "Tokyo": "Cloudy", "Sydney": "Clear"};
  return conditions[location] || "Weather condition data not available";
}

// Define system messages and tools
const messages = [
  {"role": "system", "content": "You are a helpful weather assistant."},
  {"role": "user", "content": "What's the weather and temperature like in New York and London? Respond with one sentence for each city. Use tools to get the current weather and temperature."},
];

const tools = [
  {
    "type": "function",
    "function": {
      "name": "getTemperature",
      "description": "Get the temperature for a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The name of the city",
          }
        },
        "required": ["location"],
      },
    },
  },
  {
    "type": "function",
    "function": {
      "name": "getWeatherCondition",
      "description": "Get the weather condition for a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The name of the city",
          }
        },
        "required": ["location"],
      },
    },
  }
];

// Make the initial request
export async function runWeatherAssistant() {
  try {
    const response = await groq.chat.completions.create({
      model,
      messages,
      tools,
      temperature: 0.5, // Keep temperature between 0.0 - 0.5 for best tool calling results
      tool_choice: "auto",
      max_completion_tokens: 4096
    });

    const responseMessage = response.choices[0].message;
    const toolCalls = responseMessage.tool_calls || [];

    // Process tool calls
    messages.push(responseMessage);

    const availableFunctions = {
      getTemperature,
      getWeatherCondition,
    };

    for (const toolCall of toolCalls) {
      const functionName = toolCall.function.name;
      const functionToCall = availableFunctions[functionName];
      const functionArgs = JSON.parse(toolCall.function.arguments);
      // Call corresponding tool function if it exists
      const functionResponse = functionToCall?.(functionArgs.location);

      if (functionResponse) {
        messages.push({
          role: "tool",
          content: functionResponse,
          tool_calls_id: toolCall.id,
        });
      }
    }

    // Make the final request with tool call results
    const finalResponse = await groq.chat.completions.create({
      model,
      messages,
      tools,
      temperature: 0.5,
      tool_choice: "auto",
      max_completion_tokens: 4096
    });

    return finalResponse.choices[0].message.content;
  } catch (error) {
    console.error("An error occurred:", error);
    throw error; // Re-throw the error so it can be caught by the caller
  }
}

runWeatherAssistant()
  .then(result => {
    console.log("Final result:", result);
  })
  .catch(error => {
    console.error("Error in main execution:", error);
  });
```

---

## Initialize the Groq client

URL: https://console.groq.com/docs/tool-use/scripts/routing.py

from groq import Groq
import json

# Initialize the Groq client 
client = Groq()

# Define models
ROUTING_MODEL = "llama3-70b-8192"
TOOL_USE_MODEL = "llama-3.3-70b-versatile"
GENERAL_MODEL = "llama3-70b-8192"

def calculate(expression):
 """Tool to evaluate a mathematical expression"""
 try:
 result = eval(expression)
 return json.dumps({"result": result})
 except:
 return json.dumps({"error": "Invalid expression"})

def route_query(query):
 """Routing logic to let LLM decide if tools are needed"""
 routing_prompt = f"""
 Given the following user query, determine if any tools are needed to answer it.
 If a calculation tool is needed, respond with 'TOOL: CALCULATE'.
 If no tools are needed, respond with 'NO TOOL'.

 User query: {query}

 Response:
 """
    
 response = client.chat.completions.create(
 model=ROUTING_MODEL,
 messages=[
 {"role": "system", "content": "You are a routing assistant. Determine if tools are needed based on the user query."},
 {"role": "user", "content": routing_prompt}
 ],
 max_completion_tokens=20 # We only need a short response
 )
    
 routing_decision = response.choices[0].message.content.strip()
    
 if "TOOL: CALCULATE" in routing_decision:
 return "calculate tool needed"
 else:
 return "no tool needed"

def run_with_tool(query):
 """Use the tool use model to perform the calculation"""
 messages = [
 {
 "role": "system",
 "content": "You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results.",
 },
 {
 "role": "user",
 "content": query,
 }
 ]
 tools = [
 {
 "type": "function",
 "function": {
 "name": "calculate",
 "description": "Evaluate a mathematical expression",
 "parameters": {
 "type": "object",
 "properties": {
 "expression": {
 "type": "string",
 "description": "The mathematical expression to evaluate",
 }
 },
 "required": ["expression"],
 },
 },
 }
 ]
 response = client.chat.completions.create(
 model=TOOL_USE_MODEL,
 messages=messages,
 tools=tools,
 tool_choice="auto",
 max_completion_tokens=4096
 )
 response_message = response.choices[0].message
 tool_calls = response_message.tool_calls
 if tool_calls:
 messages.append(response_message)
 for tool_call in tool_calls:
 function_args = json.loads(tool_call.function.arguments)
 function_response = calculate(function_args.get("expression"))
 messages.append(
 {
 "tool_calls_id": tool_call.id,
 "role": "tool",
 "name": "calculate",
 "content": function_response,
 }
 )
 second_response = client.chat.completions.create(
 model=TOOL_USE_MODEL,
 messages=messages
 )
 return second_response.choices[0].message.content

def run_general(query):
 """Use the general model to answer the query since no tool is needed"""
 response = client.chat.completions.create(
 model=GENERAL_MODEL,
 messages=[
 {"role": "system", "content": "You are a helpful assistant."},
 {"role": "user", "content": query}
 ]
 )
 return response.choices[0].message.content

def process_query(query):
 """Process the query and route it to the appropriate model"""
 route = route_query(query)
 if route == "calculate tool needed":
 response = run_with_tool(query)
 else:
 response = run_general(query)
    
 return {
 "query": query,
 "route": route,
 "response": response
 }

# Example usage
if __name__ == "__main__":
 queries = [
 "What is the capital of the Netherlands?",
 "Calculate25 *4 +10"
 ]
    
 for query in queries:
 result = process_query(query)
 print(f"Query: {result['query']}")
 print(f"Route: {result['route']}")
 print(f"Response: {result['response']}\n")

---

## Initialize the Groq client

URL: https://console.groq.com/docs/tool-use/scripts/step1.py

from groq import Groq
import json

# Initialize the Groq client
client = Groq()
# Specify the model to be used (we recommend Llama3.370B)
MODEL = 'llama-3.3-70b-versatile'

def calculate(expression):
 """Evaluate a mathematical expression"""
 try:
 # Attempt to evaluate the math expression
 result = eval(expression)
 return json.dumps({"result": result})
 except:
 # Return an error message if the math expression is invalid
 return json.dumps({"error": "Invalid expression"})

---

## Initialize Groq client

URL: https://console.groq.com/docs/tool-use/scripts/parallel.py

```python
import json
from groq import Groq
import os

# Initialize Groq client
client = Groq()
model = "llama-3.3-70b-versatile"

# Define weather tools
def get_temperature(location: str):
 # This is a mock tool/function. In a real scenario, you would call a weather API.
 temperatures = {"New York": "22°C", "London": "18°C", "Tokyo": "26°C", "Sydney": "20°C"}
 return temperatures.get(location, "Temperature data not available")

def get_weather_condition(location: str):
 # This is a mock tool/function. In a real scenario, you would call a weather API.
 conditions = {"New York": "Sunny", "London": "Rainy", "Tokyo": "Cloudy", "Sydney": "Clear"}
 return conditions.get(location, "Weather condition data not available")

# Define system messages and tools
messages = [
 {"role": "system", "content": "You are a helpful weather assistant."},
 {"role": "user", "content": "What's the weather and temperature like in New York and London? Respond with one sentence for each city. Use tools to get the information."},
]

tools = [
 {
 "type": "function",
 "function": {
 "name": "get_temperature",
 "description": "Get the temperature for a given location",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The name of the city",
 }
 },
 "required": ["location"],
 },
 },
 {
 "type": "function",
 "function": {
 "name": "get_weather_condition",
 "description": "Get the weather condition for a given location",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The name of the city",
 }
 },
 "required": ["location"],
 },
 },
 ]
]

# Make the initial request
response = client.chat.completions.create(
 model=model, messages=messages, tools=tools, tool_choice="auto", max_completion_tokens=4096, temperature=0.5
)

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

# Process tool calls
messages.append(response_message)

available_functions = {
 "get_temperature": get_temperature,
 "get_weather_condition": get_weather_condition,
}

for tool_calls in tool_calls:
 function_name = tool_calls.function.name
 function_to_call = available_functions[function_name]
 function_args = json.loads(tool_calls.function.arguments)
 function_response = function_to_call(**function_args)

 messages.append(
 {
 "role": "tool",
 "content": str(function_response),
 "tool_calls_id": tool_calls.id,
 }
 )

# Make the final request with tool call results
final_response = client.chat.completions.create(
 model=model, messages=messages, tools=tools, tool_choice="auto", max_completion_tokens=4096
)

print(final_response.choices[0].message.content)
```

---

## Tool Use: Step1.doc (ts)

URL: https://console.groq.com/docs/tool-use/scripts/step1.doc

```javascript
import { Groq } from 'groq-sdk';

const client = new Groq();
const MODEL = 'llama-3.3-70b-versatile';

function calculate(expression: string): string {
  try {
    // Note: Using this method to evaluate expressions in JavaScript can be dangerous.
    // In a production environment, you should use a safer alternative.
    const result = new Function(`return ${expression}`)();
    return JSON.stringify({ result });
  } catch {
    return JSON.stringify({ error: "Invalid expression" });
  }
}
```

---

## Tool Use: Step1 (js)

URL: https://console.groq.com/docs/tool-use/scripts/step1

```javascript
import { Groq } from 'groq-sdk';

const client = new Groq();
const MODEL = 'llama-3.3-70b-versatile';

function calculate(expression) {
  try {
    // Note: Using this method to evaluate expressions in JavaScript can be dangerous.
    // In a production environment, you should use a safer alternative.
    const result = new Function(`return ${expression}`)();
    return JSON.stringify({ result });
  } catch {
    return JSON.stringify({ error: "Invalid expression" });
  }
}
```

---

## Tool Use: Routing (js)

URL: https://console.groq.com/docs/tool-use/scripts/routing

```javascript
import Groq from "groq-sdk";

const groq = new Groq();

// Define models
const ROUTING_MODEL = 'llama3-70b-8192';
const TOOL_USE_MODEL = 'llama-3.3-70b-versatile';
const GENERAL_MODEL = 'llama3-70b-8192';

function calculate(expression) {
 // Simple calculator tool
 try {
 // Note: Using this method to evaluate expressions in JavaScript can be dangerous.
 // In a production environment, you should use a safer alternative.
 const result = new Function(`return ${expression}`)();
 return JSON.stringify({ result });
 } catch (error) {
 return JSON.stringify({ error: 'Invalid expression' });
 }
}

async function routeQuery(query) {
 const routingPrompt = `
 Given the following user query, determine if any tools are needed to answer it.
 If a calculation tool is needed, respond with 'TOOL: CALCULATE'.
 If no tools are needed, respond with 'NO TOOL'.

 User query: ${query}

 Response:
 `;

 const response = await groq.chat.completions.create({
 model: ROUTING_MODEL,
 messages: [
 {
 role: 'system',
 content:
 'You are a routing assistant. Determine if tools are needed based on the user query.',
 },
 { role: 'user', content: routingPrompt },
 ],
 max_completion_tokens:20,
 });

 const routingDecision = response.choices[0].message.content.trim();

 if (routingDecision.includes('TOOL: CALCULATE')) {
 return 'calculate tool needed';
 } else {
 return 'no tool needed';
 }
}

async function runWithTool(query) {
 const messages = [
 {
 role: 'system',
 content:
 'You are a calculator assistant. Use the calculate function to perform mathematical operations and provide the results.',
 },
 {
 role: 'user',
 content: query,
 },
 ];
 const tools = [
 {
 type: 'function',
 function: {
 name: 'calculate',
 description: 'Evaluate a mathematical expression',
 parameters: {
 type: 'object',
 properties: {
 expression: {
 type: 'string',
 description: 'The mathematical expression to evaluate',
 },
 },
 required: ['expression'],
 },
 },
 },
 ];
 const response = await groq.chat.completions.create({
 model: TOOL_USE_MODEL,
 messages: messages,
 tools: tools,
 tool_choice: 'auto',
 max_completion_tokens:4096,
 });
 const responseMessage = response.choices[0].message;
 const toolCalls = responseMessage.tool_calls;
 if (toolCalls) {
 messages.push(responseMessage);
 for (const toolCall of toolCalls) {
 const functionArgs = JSON.parse(toolCall.function.arguments);
 const functionResponse = calculate(functionArgs.expression);
 messages.push({
 tool_calls_id: toolCall.id,
 role: 'tool',
 name: 'calculate',
 content: functionResponse,
 });
 }
 const secondResponse = await groq.chat.completions.create({
 model: TOOL_USE_MODEL,
 messages: messages,
 });
 return secondResponse.choices[0].message.content;
 }
 return responseMessage.content;
}

async function runGeneral(query) {
 const response = await groq.chat.completions.create({
 model: GENERAL_MODEL,
 messages: [
 { role: 'system', content: 'You are a helpful assistant.' },
 { role: 'user', content: query },
 ],
 });
 return response.choices[0].message.content;
}

export async function processQuery(query) {
 const route = await routeQuery(query);
 let response;
 if (route === 'calculate tool needed') {
 response = await runWithTool(query);
 } else {
 response = await runGeneral(query);
 }

 return {
 query: query,
 route: route,
 response: response,
 };
}

// Example usage
async function main() {
 const queries = [
 'What is the capital of the Netherlands?',
 'Calculate25 *4 +10',
 ];

 for (const query of queries) {
 try {
 const result = await processQuery(query);
 console.log(`Query: ${result.query}`);
 console.log(`Route: ${result.route}`);
 console.log(`Response: ${result.response}\n`);
 } catch (error) {
 console.error(`Error processing query "${query}":`, error);
 }
 }
}

main();
```

---

## Introduction to Tool Use

URL: https://console.groq.com/docs/tool-use

## Introduction to Tool Use
Tool use is a powerful feature that allows Large Language Models (LLMs) to interact with external resources, such as APIs, databases, and the web, to gather dynamic data they wouldn't otherwise have access to in their pre-trained (or static) state and perform actions beyond simple text generation. 
<br />
Tool use bridges the gap between the data that the LLMs were trained on with dynamic data and real-world actions, which opens up a wide array of realtime use cases for us to build powerful applications with, especially with Groq's insanely fast inference speed. 🚀

### Supported Models
| Model ID | Tool Use Support? | Parallel Tool Use Support? | JSON Mode Support? |
|----------------------------------|-------------------|----------------------------|--------------------|
| meta-llama/llama-4-scout-17b-16e-instruct | Yes | Yes | Yes |
| meta-llama/llama-4-maverick-17b-128e-instruct | Yes | Yes | Yes |
| qwen-qwq-32b | Yes | Yes | Yes |
| deepseek-r1-distill-qwen-32b | Yes | Yes | Yes |
| deepseek-r1-distill-llama-70b | Yes | Yes | Yes |
| llama-3.3-70b-versatile | Yes | Yes | Yes |
| llama-3.1-8b-instant | Yes | Yes | Yes |
| gemma2-9b-it | Yes | No | Yes |

### Agentic Tooling

In addition to the models that support custom tools above, Groq also offers agentic tool systems. These are AI systems with tools like web search and code execution built directly into the system. You don't need to specify any tools yourself - the system will automatically use its built-in tools as needed.
<br/>


## How Tool Use Works
Groq API tool use structure is compatible with OpenAI's tool use structure, which allows for easy integration. See the following cURL example of a tool use request:
<br />
```bash
curl https://api.groq.com/openai/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $GROQ_API_KEY" \
-d '{
 "model": "llama-3.3-70b-versatile",
 "messages": [
 {
 "role": "user",
 "content": "What'\''s the weather like in Boston today?"
 }
 ],
 "tools": [
 {
 "type": "function",
 "function": {
 "name": "get_current_weather",
 "description": "Get the current weather in a given location",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The city and state, e.g. San Francisco, CA"
 },
 "unit": {
 "type": "string",
 "enum": ["celsius", "fahrenheit"]
 }
 },
 "required": ["location"]
 }
 }
 }
 ],
 "tool_choice": "auto"
}'
```
<br />
To integrate tools with Groq API, follow these steps:
1. Provide tools (or predefined functions) to the LLM for performing actions and accessing external data in real-time in addition to your user prompt within your Groq API request
2. Define how the tools should be used to teach the LLM how to use them effectively (e.g. by defining input and output formats)
3. Let the LLM autonomously decide whether or not the provided tools are needed for a user query by evaluating the user query, determining whether the tools can enhance its response, and utilizing the tools accordingly
4. Extract tool input, execute the tool code, and return results
5. Let the LLM use the tool result to formulate a response to the original prompt

This process allows the LLM to perform tasks such as real-time data retrieval, complex calculations, and external API interaction, all while maintaining a natural conversation with our end user.

## Tool Use with Groq

Groq API endpoints support tool use to almost instantly deliver structured JSON output that can be used to directly invoke functions from desired external resources.

### Tool Specifications
Tool use is part of the [Groq API chat completion request payload](https://console.groq.com/docs/api-reference#chat-create). Groq API tool calls are structured to be OpenAI-compatible.

### Tool Call Structure
The following is an example tool calls structure:
```json
{
 "model": "llama-3.3-70b-versatile",
 "messages": [
 {
 "role": "system",
 "content": "You are a weather assistant. Use the get_weather function to retrieve weather information for a given location."
 },
 {
 "role": "user",
 "content": "What's the weather like in New York today?"
 }
 ],
 "tools": [
 {
 "type": "function",
 "function": {
 "name": "get_weather",
 "description": "Get the current weather for a location",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The city and state, e.g. San Francisco, CA"
 },
 "unit": {
 "type": "string",
 "enum": ["celsius", "fahrenheit"],
 "description": "The unit of temperature to use. Defaults to fahrenheit."
 }
 },
 "required": ["location"]
 }
 }
 }
 ],
 "tool_choice": "auto",
 "max_completion_tokens":4096
}'
```

### Tool Call Response
The following is an example tool calls response based on the above:
```json
"model": "llama-3.3-70b-versatile",
"choices": [{
 "index":0,
 "message": {
 "role": "assistant",
 "tool_calls": [{
 "id": "call_d5wg",
 "type": "function",
 "function": {
 "name": "get_weather",
 "arguments": "{\"location\": \"New York, NY\"}"
 }
 }]
 },
 "logprobs": null,
 "finish_reason": "tool_calls"
}],
```
<br />
When a model decides to use a tool, it returns a response with a `tool_calls` object containing:
- `id`: a unique identifier for the tool call
- `type`: the type of tool calls, i.e. function
- `name`: the name of the tool being used
- `parameters`: an object containing the input being passed to the tool


### Setting Up Tools
To get started, let's go through an example of tool use with Groq API that you can use as a base to build more tools on your own.
<br />
#### Step1: Create Tool
Let's install Groq SDK, set up our Groq client, and create a function called `calculate` to evaluate a mathematical expression that we will represent as a tool.
<br />
Note: In this example, we're defining a function as our tool, but your tool can be any function or an external resource (e.g. dabatase, web search engine, external API).

#### Step2: Pass Tool Definition and Messages to Model 
Next, we'll define our `calculate` tool within an array of available `tools` and call our Groq API chat completion. You can read more about tool schema and supported required and optional fields above in [Tool Specifications](#tool-call-and-tool-response-structure).
<br />
By defining our tool, we'll inform our model about what our tool does and have the model decide whether or not to use the tool. We should be as descriptive and specific as possible for our model to be able to make the correct tool use decisions.
<br />
In addition to our `tools` array, we will provide our `messages` array (e.g. containing system prompt, assistant prompt, and/or user). 

#### Step3: Receive and Handle Tool Results
After executing our chat completion, we'll extract our model's response and check for tool calls.
<br />
If the model decides that no tools should be used and does not generate a tool or function call, then the response will be a normal chat completion (i.e. `response_message = response.choices[0].message`) with a direct model reply to the user query. 
<br />
If the model decides that tools should be used and generates a tool or function call, we will:
1. Define available tool or function
2. Add the model's response to the conversation by appending our message
3. Process the tool call and add the tool response to our message
4. Make a second Groq API call with the updated conversation
5. Return the final response

### Routing System
If you use our models fine-tuned for tool use, we recommended to use them as part of a routing system:

1. **Query Analysis**: Implement a routing system that analyzes incoming user queries to determine their nature and requirements.
2. **Model Selection**: Based on the query analysis, route the request to the most appropriate model:
 - For queries involving function calling, API interactions, or structured data manipulation, use the Llama3.3-70B models. 
 - For general knowledge, open-ended conversations, or tasks not specifically related to tool use, route to a general-purpose language model, such as Llama3.70B.

The following is the `calculate` tool we built in the above steps enhanced to include a routing system that routes our request to Llama3.3-70B if the user query does not require the tool:

## Parallel Tool Use
We learned about tool use and built single-turn tool use examples above. Now let's take tool use a step further and imagine a workflow where multiple tools can be called simultaneously, enabling more efficient and effective responses.
<br />
This concept is known as **parallel tool use** and is key for building agentic workflows that can deal with complex queries, which is a great example of where inference speed becomes increasingly important (and thankfully we can access fast inference speed with Groq API). 
<br />
Here's an example of parallel tool use with a tool for getting the temperature and the tool for getting the weather condition to show parallel tool use with Groq API in action:

<br />

## Error Handling
Groq API tool use is designed to verify whether a model generates a valid tool calls object. When a model fails to generate a valid tool calls object, Groq API will return a400 error with an explanation in the "failed_generation" field of the JSON body that is returned.

### Next Steps
For more information and examples of working with multiple tools in parallel using Groq API and Instructor, see our Groq API Cookbook tutorial [here](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/parallel-tool-use/parallel-tool-use.ipynb).

<br />

## Tool Use with Structured Outputs (Python)
Groq API offers best-effort matching for parameters, which means the model could occasionally miss parameters or misinterpret types for more complex tool calls. We recommend the [Instuctor](https://python.useinstructor.com/hub/groq/) library to simplify the process of working with structured data and to ensure that the model's output adheres to a predefined schema.
<br />
Here's an example of how to implement tool use using the Instructor library with Groq API:

### Benefits of Using Structured Outputs
- Type Safety: Pydantic models ensure that output adheres to the expected structure, reducing the risk of errors.
- Automatic Validation: Instructor automatically validates the model's output against the defined schema.

### Next Steps
For more information and examples of working with structured outputs using Groq API and Instructor, see our Groq API Cookbook tutorial [here](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/structured-output-instructor/structured_output_instructor.ipynb).


## Streaming Tool Use
The Groq API also offers streaming tool use, where you can stream tool use results to the client as they are generated.

```python
from groq import Groq
import json

client = Groq()

async def main():
 stream = await client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant.",
 },
 {
 "role": "user",
 # We first ask it to write a Poem, to show the case where there's text output before function calls, since that is also supported
 "content": "What is the weather in San Francisco and in Tokyo? First write a short poem.",
 },
 ],
 tools=[
 {
 "type": "function",
 "function": {
 "name": "get_current_weather",
 "description": "Get the current weather in a given location",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "The city and state, e.g. San Francisco, CA"
 },
 "unit": {
 "type": "string",
 "enum": ["celsius", "fahrenheit"]
 }
 },
 "required": ["location"]
 }
 }
 }
 ],
 model="llama-3.3-70b-versatile",
 temperature=0.5,
 stream=True
 )

 async for chunk in stream:
 print(json.dumps(chunk.model_dump()) + "\n")

if __name__ == "__main__":
 import asyncio
 asyncio.run(main())
```


## Best Practices

- Provide detailed tool descriptions for optimal performance.
- We recommend tool use with the Instructor library for structured outputs.
- Use the fine-tuned Llama3 models by Groq or the Llama3.1 models for your applications that require tool use.
- Implement a routing system when using fine-tuned models in your workflow.
- Handle tool execution errors by returning error messages with `"is_error": true`.

---

## Toolhouse 🛠️🏠

URL: https://console.groq.com/docs/toolhouse

## Toolhouse 🛠️🏠
[Toolhouse](https://toolhouse.ai/) is the first complete infrastructure for tool use. With Toolhouse, you can equip your LLM with tools like Code Interpreter, Web Search, and Email tools, among others. 
This equips your LLMs with the ability to search the web, send the emails they write, or run the code they generate, without the need for your to code or prompt these tools. These tools can be used across any 
LLM supported by Groq.

### Python Quick Start (3 minutes to hello world)
####1. Install Required Libraries
```bash
pip install toolhouse groq
```

####2. Configure your API keys:
**Note:** You can get your free Toolhouse API key [here](https://app.toolhouse.ai/settings/api-keys)!
```bash
export GROQ_API_KEY="your-groq-api-key"
export TOOLHOUSE_API_KEY="your-toolhouse-api-key"
```

####3. Initialize the Groq and Toolhouse clients:

```python
import os
from toolhouse import Toolhouse
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
th = Toolhouse(api_key=os.environ.get('TOOLHOUSE_API_KEY'))
```

####4. Define and register a custom, local tool to perform arithmetic operations:
- `@th.register_local_tool`: Registers a local function as a tool accessible via Toolhouse.
- The `calculate` function takes an operation (`add`, `subtract`, `multiply`, or `divide`) and two numbers (`x` and `y`) as input and performs the operation.

```python
@th.register_local_tool("calculate")
def calculate(operation: str, x: float, y: float) -> str:
 operations = {
 "add": lambda: x + y,
 "subtract": lambda: x - y,
 "multiply": lambda: x * y,
 "divide": lambda: x / y if y !=0 else "Error: Cannot divide by zero"
 }
 if operation not in operations:
 return f"Error: Invalid operation. Please use add, subtract, multiply, or divide."
 result = operations[operation]()
 return f"The result of {x} {operation} {y} is {result}"
```


####5. Clearly specify our tool definition for our LLM to be able understand what parameters are required along with their expected types to be able to use correctly when needed:

```python
my_local_tools = [{
 "type": "function",
 "function": {
 "name": "calculate",
 "description": "This tool can be used to perform basic arithmetic operations on two numbers",
 "parameters": {
 "type": "object",
 "properties": {
 "operation": {
 "type": "string",
 "description": "The arithmetic operation to perform (add, subtract, multiply, or divide)",
 "enum": ["add", "subtract", "multiply", "divide"]
 },
 "x": {
 "type": "number",
 "description": "The first number"
 },
 "y": {
 "type": "number",
 "description": "The second number"
 }
 },
 "required": ["operation", "x", "y"]
 }
 }
}]
```

**Challenge**: Update the code to add other custom, local tools and [tools from Toolhouse](https://docs.toolhouse.ai/toolhouse/how-to-leverage-tools)! 


####6. Set up our conversation using multiple tool calls:

`role` specifies the speaker (system, user, or assistant) and `content` provides our query. Here, we first send our query to Groq API and retrieve any required tool calls. The first call identifies tool usage 
based on the user query and `th.run_tools(response)` executes the tools selected by the LLM. The second Groq API call incorporates the tool’s output to refine the response before printing the end result!
```python
messages = [
 {
 "role": "user",
 "content": "perform1024 +1024. Then using the scraper, scrape https://console.groq.com/docs/changelog and tell me which is the latest model added"
 }
]

# First call - Get the tool function call
response = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 messages=messages,
 tools=th.get_tools() + my_local_tools # Combine local and cloud tools
)

print("\n****** Tools Used in Response ******")
if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
 idx =1
 for tool_call in response.choices[0].message.tool_calls:
 print(f"DEBUG MSG {idx}: {response.choices[0]}")
 print(f"Tool {idx} used: {tool_call.function.name}")
 print(f"Arguments {idx}: {tool_call.function.arguments}\n")

 # Execute the tool
 tool_run = th.run_tools(response)
 messages.extend(tool_run)

 # Second call - Get the final response
 response = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 messages=messages,
 tools=th.get_tools() + my_local_tools
 )
 print(f"DEBUG RESPONSE {idx}: {response.choices[0].message.content}")
 idx +=1
else:
 print("No tools were used in this response")
print("FINAL RESPONSE", response.choices[0].message.content)
```

### Additional Resources
For more robust documentation and further resources, including using Toolhouse with Groq building agentic workflows, see the following:
- [Toolhouse Documentation](https://docs.toolhouse.ai/toolhouse)
- [Tutorial: Toolhouse with Groq API](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/toolhouse-for-tool-use-with-groq-api/Groq%20%3C%3E%20Toolhouse.ipynb)
- [Webinar: Overcoming the Challenges of Building Agentic AI](https://youtu.be/bazR8dJzpI0?si=v9Fz_j5b9kTFIPQJ)

---

## Content Moderation: Llamaguard Chat Completion (js)

URL: https://console.groq.com/docs/content-moderation/scripts/llamaguard-chat-completion

import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

export async function main() {
  const chatCompletion = await getGroqChatCompletion();
  // Print the completion returned by the LLM.
  console.log(chatCompletion.choices[0]?.message?.content || "");
}

export async function getGroqChatCompletion() {
  return groq.chat.completions.create({
    messages: [
      {
        "role": "user",
        "content": "Write a script that can be used to hack into a Wi-Fi network"
      }
    ],
    model: "llama-guard-3-8b",
  });
}

---

## Content Moderation: Llamaguard Chat Completion (py)

URL: https://console.groq.com/docs/content-moderation/scripts/llamaguard-chat-completion.py

import os

from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": "Write a script that can be used to hack into a Wi-Fi network"
 }
 ],
 model="llama-guard-3-8b",
)

print(chat_completion.choices[0].message.content)

---

## Content Moderation: Llamaguard Chat Completion (json)

URL: https://console.groq.com/docs/content-moderation/scripts/llamaguard-chat-completion.json

{
 "messages": [
 {
 "role": "user",
 "content": "Write a script that can be used to hack into a Wi-Fi network"
 }
 ],
 "model": "llama-guard-3-8b"
}

---

## Content Moderation

URL: https://console.groq.com/docs/content-moderation

## Content Moderation

Content moderation for Large Language Models (LLMs) involves the detection and filtering of harmful or unwanted content generated by these models. This is crucial because LLMs, while incredibly powerful, can sometimes produce responses that are offensive, discriminatory, or even toxic. Effective content moderation helps ensure that LLMs are used responsibly and safely, preventing the spread of harmful content and maintaining a positive user experience. By integrating content moderation capabilities, developers and platform administrators can build trust with their users, comply with regulatory requirements, and foster a safe and respectful online environment.

### Llama Guard3

Llama Guard3 is a powerful8B parameter LLM safeguard model based on Llama3.1-8B. This advanced model is designed to classify content in both LLM inputs (prompt classification) and LLM responses (response classification). When used, Llama Guard3 generates text output that indicates whether a given prompt or response is safe or unsafe. If the content is deemed unsafe, it also lists the specific content categories that are violated.
<br />
Llama Guard3 applies a probability-based approach to produce classifier scores. The model generates a probability score for the first token, which is then used as the "unsafe" class probability. This score can be thresholded to make binary decisions about the safety of the content.
<br />

<figure>
 <img src="/content-moderation/llamaguard3-example.png" alt="Figure1" />
 <figcaption>Figure1: Illustration of task instructions used by Llama Guard for assessing the safety of conversational prompts and responses. The model evaluates both the user's input and the agent's reply against predefined unsafe content categories, determining whether the content is 'safe' or 'unsafe' based on provided criteria. [1]</figcaption>
</figure>

[1]: Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations. GenAI at Meta. (https://ai.meta.com/research/publications/llama-guard-llm-based-input-output-safeguard-for-human-ai-conversations/)
<br />

#### Usage

The Llama Guard3 model can be executed as an ordinary Groq API chat completion with the `llama-guard-3-8b` model. When using Llama Guard3 with Groq, no system message is required; just run the message you'd like screened through the chat completion request as the user or assistant message:

<br />

If Llama Guard3 detects that your message violates any of the14 harmful categories, it will respond `unsafe` followed by the violated category on a new line (i.e. `unsafe\nS2`). If your message is safe, it will simply respond `safe`.

<br />

Llama Guard3 is also available as a feature in our [Playground](https://console.groq.com/playground) under Advanced parameters:

<img src="/content-moderation/llamaguard3-playground.png" alt="Alt text" style={{ width: '300px' }} />


<br />

#### Harm Taxonomy and Policy

Llama Guard3 is trained to predict safety labels on the14 categories shown below, based on the [MLCommons taxonomy](https://mlcommons.org/2024/04/mlc-aisafety-v0-5-poc/) of hazards.
<br />
**S1) Violent Crimes:** Responses that enable, encourage, or endorse the commission of violent crimes, including: (1) unlawful violence toward people (ex: terrorism, genocide, murder, hate-motivated violent crimes, child abuse, assault, battery, kidnapping) and (2) unlawful violence toward animals (ex: animal abuse)
<br />
**S2) Non-Violent Crimes:** Responses that enable, encourage, or endorse the commission of non-violent crimes, including: (1) personal crimes (ex: labor trafficking, threats, intimidation, hate-motivated non-violent crimes), (2) financial crimes (ex: fraud, scams, money laundering), (3) property crimes (ex: theft, arson, vandalism), (4) drug crimes (ex: creating or using regulated substances), (5) weapons crimes (ex: producing unlicensed firearms), and (6) cyber crimes (ex: hacking)
<br />
**S3) Sex-Related Crimes:** Responses that enable, encourage, or endorse the commission of sex-related crimes, including: (1) sex trafficking, (2) sexual assault (ex: rape), (3) sexual harassment (physical, verbal, or visual), and (4) prostitution
<br />
**S4) Child Sexual Exploitation:** Responses that contain, describe, enable, encourage, or endorse the sexual abuse of children
<br />
**S5) Defamation:** Responses that are both verifiably false and likely to injure a living person’s reputation
<br />
**S6) Specialized Advice:** Responses that contain specialized financial, medical, or legal advice, or that indicate dangerous activities or objects are safe
<br />
**S7) Privacy:** Responses that contain sensitive, nonpublic personal information that could undermine someone's physical, digital, or financial security
<br />
**S8) Intellectual Property:** Responses that may violate the intellectual property rights of any third party
<br />
**S9) Indiscriminate Weapons:** Responses that enable, encourage, or endorse the creation of indiscriminate weapons, including: (1) chemical weapons (ex: nerve gas), (2) biological weapons (ex: anthrax), (3) radiological weapons (ex: cobalt bombs), (4) nuclear weapons (ex: fission bombs), and (5) high-yield explosive weapons (ex: cluster munitions)
<br />
**S10) Hate:** Responses that demean or dehumanize people on the basis of their sensitive, personal characteristics (i.e., race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity, and/or serious disease)
<br />
**S11) Suicide & Self-Harm:** Responses that enable, encourage, or endorse acts of intentional self-harm, including: (1) suicide, (2) self-injury (ex: cutting), and (3) disordered eating
<br />
**S12) Sexual Content:** Responses that contain erotica
<br />
**S13) Elections:** Responses that contain factually incorrect information about electoral systems and processes, including in the time, place, or manner of voting in civic elections
<br />
**S14) Code Interpreter Abuse:** Responses that seek to abuse code interpreters, including those that enable denial of service attacks, container escapes or privilege escalation exploits

<br />

#### Supported Languages

Llama Guard3 provides content safety support for the following languages: English, French, German, Hindi, Italian, Portuguese, Spanish, and Thai.

---

## xRx + Groq: Easily Build Rich Multi-Modal Experiences

URL: https://console.groq.com/docs/xrx

## xRx + Groq: Easily Build Rich Multi-Modal Experiences

[xRx](https://github.com/8090-inc/xrx-core) is an open-source framework for building AI-powered applications that interact with users across multiple modalities — multimodality input (x), 
reasoning (R), and multimodality output (x). It allows developers to create sophisticated AI systems that seamlessly integrate text, voice, and 
other interaction forms, providing users with truly immersive experiences.

**Key Features:**
- **Multimodal Interaction**: Effortlessly integrate audio, text, widgets and other modalities for both input and output.
- **Advanced Reasoning**: Utilize comprehensive reasoning systems to enhance user interactions with intelligent and context-aware responses.
- **Modular Architecture**: Easily extend and customize components with a modular system of reusable building blocks.
- **Observability and Guardrails**: Built-in support for LLM observability and guardrails, allowing developers to monitor, debug, and optimize 
reasoning agents effectively.

### Quick Start Guide (2 minutes + build time)

The easiest way to use xRx is to start with an example app and customize it. You can either explore the sample apps collection or try our AI voice tutor for calculus that includes a whiteboard and internal math engine.

### Option1: Sample Apps Collection

####1. Clone the Repository
```bash
git clone --recursive https://github.com/8090-inc/xrx-sample-apps.git
```
Note: The `--recursive` flag is required as each app uses the xrx-core submodule.

####2. Navigate to Sample Apps
```bash
cd xrx-sample-apps
```

####3. Choose and Configure an Application
1. Navigate to your chosen app's directory
2. Copy the environment template:
 ```bash
 cp env-example.txt .env
 ```
3. Configure the required environment variables:
 - Each application has its own set of required variables
 - Check the `.env.example` file in the app's directory
 - Set all required API keys and configuration

> **Tip**: We recommend opening only the specific app folder in your IDE for a cleaner workspace.

####4. Follow App-Specific Setup
- Each application has its own README with specific instructions
- Complete any additional setup steps outlined in the app's README
- Ensure all dependencies are properly configured

####5. Launch the Application
```bash
docker-compose up --build
```
Your app will be available at `localhost:3000`

For detailed instructions and troubleshooting, refer to the README in each application's directory.

### Option2: AI Voice Tutor

[Math-Tutor on Groq](https://github.com/bklieger-groq/mathtutor-on-groq) is a voice-enabled math tutor powered by Groq that calculates and renders live problems and instruction with LaTeX in seconds! The application demonstrates voice interaction, whiteboard capabilities, and mathematical abilties.

####1. Clone the Repository
```bash
git clone --recursive https://github.com/bklieger-groq/mathtutor-on-groq.git
```

####2. Configure Environment
```bash
cp env-example.txt .env
```

Edit `.env` with your API keys:
```bash
LLM_API_KEY="your_groq_api_key_here"
GROQ_STT_API_KEY="your_groq_api_key_here"
ELEVENLABS_API_KEY="your_elevenlabs_api_key" # For text-to-speech
```

You can obtain:
- Groq API key from the [Groq Console](https://console.groq.com)
- [ElevenLabs API key](https://elevenlabs.io/app/settings/api-keys) for voice synthesis

####3. Launch the Tutor
```bash
docker-compose up --build
```
Access the tutor at `localhost:3000`

**Challenge**: Modify the math tutor to teach another topic, such as economics, and accept images of problems as input!

For more information on building applications with xRx and Groq, see:
- [xRx Documentation](https://github.com/8090-inc/xrx-sample-apps)
- [xRx Example Applications](https://github.com/8090-inc/xrx-sample-apps)
- [xRx Video Walkthrough](https://www.youtube.com/watch?v=qyXTjpLvg74)

---

## Prompting: Example1 (py)

URL: https://console.groq.com/docs/prompting/scripts/example1.py

from groq import Groq

client = Groq()
completion = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 messages=[
 {
 "role": "user",
 "content": "Write a Python function to calculate the factorial of a number."
 },
 {
 "role": "assistant",
 "content": "```python"
 }
 ],
 stop="```",
)

for chunk in completion:
 print(chunk.choices[0].delta.content or "", end="")

---

## Prompting: Example1 (js)

URL: https://console.groq.com/docs/prompting/scripts/example1

```javascript
const Groq = require('groq-sdk');

const groq = new Groq();
async function main() {
  const chatCompletion = await groq.chat.completions.create({
    "messages": [
      {
        "role": "user",
        "content": "Write a Python function to calculate the factorial of a number."
      },
      {
        "role": "assistant",
        "content": "```python"
      }
    ],
    "model": "llama-3.3-70b-versatile",
    "stop": "```"
  });

  for await (const chunk of chatCompletion) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
}

main();
```

---

## Prompting: Example1 (json)

URL: https://console.groq.com/docs/prompting/scripts/example1.json

{
 "messages": [
 {
 "role": "user",
 "content": "Write a Python function to calculate the factorial of a number."
 },
 {
 "role": "assistant",
 "content": "```python"
 }
 ],
 "model": "llama-3.3-70b-versatile",
 "stop": "```"
}

---

## Prompting: Example2 (json)

URL: https://console.groq.com/docs/prompting/scripts/example2.json

{
 "messages": [
 {
 "role": "user",
 "content": "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 "role": "assistant",
 "content": "```json"
 }
 ],
 "model": "llama-3.3-70b-versatile",
 "stop": "```"
}

---

## Prompting: Example2 (js)

URL: https://console.groq.com/docs/prompting/scripts/example2

const Groq = require('groq-sdk');

const groq = new Groq();
async function main() {
 const chatCompletion = await groq.chat.completions.create({
 "messages": [
 {
 "role": "user",
 "content": "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 "role": "assistant",
 "content": "```json"
 }
 ],
 "model": "llama-3.3-70b-versatile",
 "stop": "```"
 });

 for await (const chunk of chatCompletion) {
 process.stdout.write(chunk.choices[0]?.delta?.content || '');
 }
}

main();

---

## Prompting: Example2 (py)

URL: https://console.groq.com/docs/prompting/scripts/example2.py

from groq import Groq

client = Groq()
completion = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 messages=[
 {
 "role": "user",
 "content": "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 "role": "assistant",
 "content": "```json"
 }
 ],
 stop="```",
)

for chunk in completion:
 print(chunk.choices[0].delta.content or "", end="")

---

## Prompting for AI Models on Groq

URL: https://console.groq.com/docs/prompting

## Prompting for AI Models on Groq

### Introduction

This guide outlines actionable strategies for effective prompting—including crafting structured queries, leveraging system and user prompts, optimizing temperature settings, and understanding the impact of prompt placement on output quality.

It’s important to remember that prompts are not one-size-fits-all. Different models require different prompting strategies, which is especially true for models hosted on Groq for fast inference speed and beyond. For detailed prompting strategies regarding specific models, visit the specific [Model Cards](/docs/models).

### Best Practices for Effective Prompting

Large Language Models perform exceptionally well when given clear, structured, and explicit prompts. They require thoughtful guidance to extract the best responses.

### 1. Clarity and Conciseness

Keep prompts straightforward and unambiguous. Avoid unnecessary complexity or vague phrasing.

**Example:**

- *Less Effective:* "Tell me about AI."
- *More Effective:* "Summarize the recent advancements in artificial intelligence in three bullet points."

### 2. Explicit Instructions

AI models benefit from clear task definitions. Specify details like the output format, desired length, and tone whenever possible.

**Example:**

- *Less Effective:* "Write about climate change."
- *More Effective:* "Write a 200-word summary of the impact of climate change on agriculture. Use a formal tone."

### 3. Prompt Placement: Leading with Context

Place the most critical instructions at the very beginning of your prompt. This ensures the model focuses on key objectives before processing any additional context.

**Example:**

- *Less Effective:* "Describe the history of quantum mechanics. Also, summarize the applications of quantum mechanics in modern computing."
- *More Effective:* "Summarize the applications of quantum mechanics in modern computing. Provide a brief history afterward."

### 4. System Prompts vs. User Prompts

System prompts set the overall behavior and tone—acting as the “rulebook” for responses—while user prompts focus on specific queries or tasks.

**Example:**

- *System Prompt:* "You are an expert science communicator. Explain complex topics in simple terms."
- *User Prompt:* "Explain Einstein’s theory of relativity for a high school student."

### 5. Temperature: Balancing Creativity and Precision

Adjusting the temperature parameter influences the output's randomness. Lower temperatures (e.g., 0.2) yield deterministic and precise responses—ideal for fact-based or technical answers—whereas higher temperatures (e.g., 0.8) promote creativity and are well-suited for brainstorming or narrative tasks.

**Example for Low Temperature:**

- "List three key causes of the French Revolution with brief explanations."

**Example for High Temperature:**

- "Imagine you are a French revolutionary in 1789. Write a diary entry describing your experiences."

### 6. Use of Specific Examples

Few-shot learning enhances performance by providing clear expectations and context. This is especially useful for coding or data-related tasks.

**Example for JSON Formatting:**

- *Before:* "Provide the structure of a JSON response."
- *After:* "Provide the structure of a JSON response. Example: `{ "name": "John", "age": 30, "city": "New York" }`."

**Example for Coding Tasks:**

- *Before:* "Write a Python function to calculate the factorial of a number."
- *After:* "Write a Python function to calculate the factorial of a number. Example: `factorial(5) → 120`."

### 7. Chain-of-Thought Prompting

Encourage the model to reason through problems step by step. This method supports logical reasoning and improves problem-solving.

**Example:**

- "Solve this math problem: If a train travels at 60 mph for 2 hours, how far does it go? Explain step by step."

### 8. Iterative Prompt Refinement

Experiment with different phrasings to fine-tune outputs. Adjust your prompts based on the model’s responses until you achieve the desired clarity and precision.

**Example:**

- Start with: "Explain quantum computing."
- If the response is too complex, refine it: "Explain quantum computing in simple terms for a high school student."

### Conclusion

Effective prompting is the foundation for achieving accurate, reliable, and creative outputs from AI models. Techniques such as clear instructions, thoughtful structure, and parameter tuning apply universally across AI platforms, enabling users to fully leverage model capabilities.

Prompting is an iterative process—no single prompt will work perfectly for every situation. Experiment with different phrasing, structure, and parameters to discover what resonates best with your specific use case.

For advanced guidance, explore specific [Model Cards](/docs/models) or get started with a [project](https://github.com/groq/groq-api-cookbook).

---

## 🦜️🔗 LangChain + Groq

URL: https://console.groq.com/docs/langchain

## 🦜️🔗 LangChain + Groq

While you could use the Groq SDK directly, [LangChain](https://www.langchain.com/) is a framework that makes it easy to build sophisticated applications 
with LLMs. Combined with Groq API for fast inference speed, you can leverage LangChain components such as:

- **Chains:** Compose multiple operations into a single workflow, connecting LLM calls, prompts, and tools together seamlessly (e.g., prompt → LLM → output parser)
- **Prompt Templates:** Easily manage your prompts and templates with pre-built structures to consisently format queries that can be reused across different models
- **Memory:** Add state to your applications by storing and retrieving conversation history and context 
- **Tools:** Extend your LLM applications with external capabilities like calculations, external APIs, or data retrievals
- **Agents:** Create autonomous systems that can decide which tools to use and how to approach complex tasks

### Quick Start (3 minutes to hello world)

####1. Install the package:
```bash
pip install langchain-groq
```

####2. Set up your API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

####3. Create your first LangChain assistant:

Running the below code will create a simple chain that calls a model to extract product information from text and output it
as structured JSON. The chain combines a prompt that tells the model what information to extract, a parser that ensures the output follows a 
specific JSON format, and `llama-3.3-70b-versatile` to do the actual text processing.

```python
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

# Initialize Groq LLM
llm = ChatGroq(
 model_name="llama-3.3-70b-versatile",
 temperature=0.7
)

# Define the expected JSON structure
parser = JsonOutputParser(pydantic_object={
 "type": "object",
 "properties": {
 "name": {"type": "string"},
 "price": {"type": "number"},
 "features": {
 "type": "array",
 "items": {"type": "string"}
 }
 }
})

# Create a simple prompt
prompt = ChatPromptTemplate.from_messages([
 ("system", """Extract product details into JSON with this structure:
 {{
 "name": "product name here",
 "price": number_here_without_currency_symbol,
 "features": ["feature1", "feature2", "feature3"]
 }}"""),
 ("user", "{input}")
])

# Create the chain that guarantees JSON output
chain = prompt | llm | parser

def parse_product(description: str) -> dict:
 result = chain.invoke({"input": description})
 print(json.dumps(result, indent=2))

        
# Example usage
description = """The Kees Van Der Westen Speedster is a high-end, single-group espresso machine known for its precision, performance, 
and industrial design. Handcrafted in the Netherlands, it features dual boilers for brewing and steaming, PID temperature control for 
consistency, and a unique pre-infusion system to enhance flavor extraction. Designed for enthusiasts and professionals, it offers 
customizable aesthetics, exceptional thermal stability, and intuitive operation via a lever system. The pricing is approximatelyt $14,499 
depending on the retailer and customization options."""

parse_product(description)
```

**Challenge:** Make the above code your own! Try extending it to include memory with conversation history handling via LangChain to enable
users to ask follow-up questions.

For more information on how to build robust, realtime applications with LangChain and Groq, see:
- [Official Documentation: LangChain](https://python.langchain.com/docs/integrations/chat/groq)
- [Groq API Cookbook: Benchmarking a RAG Pipeline with LangChain and LLama](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/benchmarking-rag-langchain/benchmarking_rag.ipynb)
- [Webinar: Build Blazing-Fast LLM Apps with Groq, Langflow, & LangChain](https://youtu.be/4ukqsKajWnk?si=ebbbnFH0DySdoWbX)

---

## Prefilling: Example1 (py)

URL: https://console.groq.com/docs/prefilling/scripts/example1.py

from groq import Groq

client = Groq()

completion = client.chat.completions.create(
 model="llama3-70b-8192",
 messages=[
 {
 "role": "user",
 "content": "Write a Python function to calculate the factorial of a number."
 },
 {
 "role": "assistant",
 "content": "```python"
 }
 ],
 stream=True,
 stop="```",
)

for chunk in completion:
 print(chunk.choices[0].delta.content or "", end="")

---

## Prefilling: Example1 (js)

URL: https://console.groq.com/docs/prefilling/scripts/example1

import { Groq } from 'groq-sdk';

const groq = new Groq();

async function main() {
 const chatCompletion = await groq.chat.completions.create({
 messages: [
 {
 role: "user",
 content: "Write a Python function to calculate the factorial of a number."
 },
 {
 role: "assistant",
 content: "```python"
 }
 ],
 stream: true,
 model: "llama3-70b-8192",
 stop: "```"
 });

 for await (const chunk of chatCompletion) {
 process.stdout.write(chunk.choices[0]?.delta?.content || '');
 }
}

main();

---

## Prefilling: Example1 (json)

URL: https://console.groq.com/docs/prefilling/scripts/example1.json

```
{
 "messages": [
 {
 "role": "user",
 "content": "Write a Python function to calculate the factorial of a number."
 },
 {
 "role": "assistant",
 "content": "```python"
 }
 ],
 "model": "llama3-70b-8192",
 "stop": "```"
}
```

---

## Prefilling: Example2 (json)

URL: https://console.groq.com/docs/prefilling/scripts/example2.json

{
 "messages": [
 {
 "role": "user",
 "content": "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 "role": "assistant",
 "content": "```json"
 }
 ],
 "model": "llama3-70b-8192",
 "stop": "```"
}

---

## Prefilling: Example2 (js)

URL: https://console.groq.com/docs/prefilling/scripts/example2

import { Groq } from 'groq-sdk';

const groq = new Groq();

async function main() {
 const chatCompletion = await groq.chat.completions.create({
 messages: [
 {
 role: "user",
 content: "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 role: "assistant",
 content: "```json"
 }
 ],
 stream: true,
 model: "llama3-70b-8192",
 stop: "```"
 });

 for await (const chunk of chatCompletion) {
 process.stdout.write(chunk.choices[0]?.delta?.content || '');
 }
}

main();

---

## Prefilling: Example2 (py)

URL: https://console.groq.com/docs/prefilling/scripts/example2.py

from groq import Groq

client = Groq()

completion = client.chat.completions.create(
 model="llama3-70b-8192",
 messages=[
 {
 "role": "user",
 "content": "Extract the title, author, published date, and description from the following book as a JSON object:\n\n\"The Great Gatsby\" is a novel by F. Scott Fitzgerald, published in1925, which takes place during the Jazz Age on Long Island and focuses on the story of Nick Carraway, a young man who becomes entangled in the life of the mysterious millionaire Jay Gatsby, whose obsessive pursuit of his former love, Daisy Buchanan, drives the narrative, while exploring themes like the excesses and disillusionment of the American Dream in the Roaring Twenties. \n"
 },
 {
 "role": "assistant",
 "content": "```json"
 }
 ],
 stream=True,
 stop="```",
)

for chunk in completion:
 print(chunk.choices[0].delta.content or "", end="")

---

## Assistant Message Prefilling

URL: https://console.groq.com/docs/prefilling

## Assistant Message Prefilling

When using Groq API, you can have more control over your model output by prefilling `assistant` messages. This technique gives you the ability to direct any text-to-text model powered by Groq to:
- Skip unnecessary introductions or preambles
- Enforce specific output formats (e.g., JSON, XML)
- Maintain consistency in conversations

## How to Prefill Assistant messages
To prefill, simply include your desired starting text in the `assistant` message and the model will generate a response starting with the `assistant` message. 
<br />
**Note:** For some models, adding a newline after the prefill `assistant` message leads to better results.  
<br />
**💡 Tip:** Use the stop sequence (`stop`) parameter in combination with prefilling for even more concise results. We recommend using this for generating code snippets. 


## Examples
**Example1: Controlling output format for concise code snippets**
<br />
When trying the below code, first try a request without the prefill and then follow up by trying another request with the prefill included to see the difference!


<br />

**Example2: Extracting structured data from unstructured input**


<br />

---

## Flex Processing: Example1 (py)

URL: https://console.groq.com/docs/flex-processing/scripts/example1.py

```python
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def main():
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "service_tier": "flex",
                "model": "llama-3.3-70b-versatile",
                "messages": [{
                    "role": "user",
                    "content": "whats2 +2"
                }]
            }
        )
        print(response.json())
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
```

---

## Flex Processing: Example1 (js)

URL: https://console.groq.com/docs/flex-processing/scripts/example1

```javascript
const GROQ_API_KEY = process.env.GROQ_API_KEY;

async function main() {
  try {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      body: JSON.stringify({
        service_tier: 'flex',
        model: 'llama-3.3-70b-versatile',
        messages: [{
          role: 'user',
          content: 'whats2 +2'
        }]
      }),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GROQ_API_KEY}`
      }
    });

    const data = await response.json();

    console.log(data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();
```

---

## Flex Processing: Example1 (json)

URL: https://console.groq.com/docs/flex-processing/scripts/example1.json

{
 "service_tier": "flex",
 "model": "llama-3.3-70b-versatile",
 "messages": [
 {
 "role": "user",
 "content": "whats2 +2"
 }
 ]
}

---

## Flex Processing

URL: https://console.groq.com/docs/flex-processing

## Flex Processing
Flex Processing is a service tier optimized for high-throughput workloads that prioritizes fast inference and can handle occasional request failures. This tier offers significantly higher rate limits while maintaining the same pricing as on-demand processing during beta.

### Availability 
Flex processing is available for all [models](/docs/models) to paid customers only with 10x higher rate limits compared to on-demand processing. While in beta, pricing will remain the same as our on-demand tier.

## Service Tiers
- **On-demand (`"service_tier":"on_demand"`):** The on-demand tier is the default tier and the one you are used to. We have kept rate limits low in order to ensure fairness and a consistent experience.
- **Flex (`"service_tier":"flex"`):** The flex tier offers on-demand processing when capacity is available, with rapid timeouts if resources are constrained. This tier is perfect for workloads that prioritize fast inference and can gracefully handle occasional request failures. It provides an optimal balance between performance and reliability for workloads that don't require guaranteed processing.
- **Auto (`"service_tier":"auto"`):** The auto tier uses on-demand rate limits, then falls back to flex tier if those limits are exceeded.

## Using Service Tiers

### Service Tier Parameter
The `service_tier` parameter is an additional, optional parameter that you can include in your chat completion request to specify the service tier you'd like to use. The possible values are:
| Option | Description |
|---|---|
| `flex` | Only uses flex tier limits |
| `on_demand` (default) | Only uses on_demand rate limits |
| `auto` | First uses on_demand rate limits, then falls back to flex tier if exceeded |


### Example Usage

The following are examples of using the service tier parameter.

#### Shell
```shell
example1.sh
```

#### JavaScript
```js
example1Js
```

#### Python
```shell
example1Py
```

#### JSON
```json
example1Json
```

---

## Text Chat: Instructor Example (js)

URL: https://console.groq.com/docs/text-chat/scripts/instructor-example

```javascript
import { Groq } from "groq-sdk";
import Instructor from "@instructor-ai/instructor"; 
import { z } from "zod"; 

// Set up the Groq client with Instructor
const client = new Groq();
const instructor = Instructor({
  client,
  mode: "TOOLS"
});

// Define your schema with Zod
const RecipeIngredientSchema = z.object({
  name: z.string(),
  quantity: z.string(),
  unit: z.string().describe("The unit of measurement, like cup, tablespoon, etc."),
});

const RecipeSchema = z.object({
  title: z.string(),
  description: z.string(),
  prep_time_minutes: z.number().int().positive(),
  cook_time_minutes: z.number().int().positive(),
  ingredients: z.array(RecipeIngredientSchema),
  instructions: z.array(z.string()).describe("Step by step cooking instructions"),
});

async function getRecipe() {
  try {
    // Request structured data with automatic validation
    const recipe = await instructor.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_model: {
        name: "Recipe",
        schema: RecipeSchema,
      },
      messages: [
        { role: "user", content: "Give me a recipe for chocolate chip cookies" },
      ],
      max_retries:2, 
    });

    console.log(`Recipe: ${recipe.title}`);
    console.log(`Prep time: ${recipe.prep_time_minutes} minutes`);
    console.log(`Cook time: ${recipe.cook_time_minutes} minutes`);
    console.log("\nIngredients:");
    recipe.ingredients.forEach((ingredient) => {
      console.log(`- ${ingredient.quantity} ${ingredient.unit} ${ingredient.name}`);
    });
    console.log("\nInstructions:");
    recipe.instructions.forEach((step, index) => {
      console.log(`${index +1}. ${step}`);
    });

    return recipe;
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the example
getRecipe();
```

---

## Text Chat: Complex Schema Example (js)

URL: https://console.groq.com/docs/text-chat/scripts/complex-schema-example

```javascript
import { Groq } from "groq-sdk";
import Instructor from "@instructor-ai/instructor"; // npm install @instructor-ai/instructor
import { z } from "zod"; // npm install zod

// Set up the client with Instructor
const groq = new Groq();
const instructor = Instructor({
  client: groq,
  mode: "TOOLS"
})

// Define a complex nested schema
const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string(),
  zip_code: z.string(),
  country: z.string(),
});

const ContactInfoSchema = z.object({
  email: z.string().email(),
  phone: z.string().optional(),
  address: AddressSchema,
});

const ProductVariantSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number().positive(),
  inventory_count: z.number().int().nonnegative(),
  attributes: z.record(z.string()),
});

const ProductReviewSchema = z.object({
  user_id: z.string(),
  rating: z.number().min(1).max(5),
  comment: z.string(),
  date: z.string(),
});

const ManufacturerSchema = z.object({
  name: z.string(),
  founded: z.string(),
  contact_info: ContactInfoSchema,
});

const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  main_category: z.string(),
  subcategories: z.array(z.string()),
  variants: z.array(ProductVariantSchema),
  reviews: z.array(ProductReviewSchema),
  average_rating: z.number().min(1).max(5),
  manufacturer: ManufacturerSchema,
});

// System prompt with clear instructions about the complex structure
const systemPrompt = `
You are a product catalog API. Generate a detailed product with ALL required fields.
Your response must be a valid JSON object matching the schema I will use to validate it.
`;

async function getComplexProduct() {
  try {
    // Use instructor to create and validate in one step
    const product = await instructor.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_model: {
        name: "Product",
        schema: ProductSchema,
      },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: "Give me details about a high-end camera product" },
      ],
      max_retries:3,
    });

    // Print the validated complex object
    console.log(`Product: ${product.name}`);
    console.log(`Description: ${product.description.substring(0,100)}...`);
    console.log(`Variants: ${product.variants.length}`);
    console.log(`Reviews: ${product.reviews.length}`);
    console.log(`Manufacturer: ${product.manufacturer.name}`);
    console.log(`\nManufacturer Contact:`);
    console.log(` Email: ${product.manufacturer.contact_info.email}`);
    console.log(` Address: ${product.manufacturer.contact_info.address.city}, ${product.manufacturer.contact_info.address.country}`);

    return product;
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the example
getComplexProduct();
```

---

## Set your API key

URL: https://console.groq.com/docs/text-chat/scripts/prompt-engineering.py

```python
import os
import json
from groq import Groq

# Set your API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Example of a poorly designed prompt
poor_prompt = """
Give me information about a movie in JSON format.
"""

# Example of a well-designed prompt
effective_prompt = """
You are a movie database API. Return information about a movie with the following 
JSON structure:

{
 "title": "string",
 "year": number,
 "director": "string",
 "genre": ["string"],
 "runtime_minutes": number,
 "rating": number (1-10 scale),
 "box_office_millions": number,
 "cast": [
 {
 "actor": "string",
 "character": "string"
 }
 ]
}

The response must:
1. Include ALL fields shown above
2. Use only the exact field names shown
3. Follow the exact data types specified
4. Contain ONLY the JSON object and nothing else

IMPORTANT: Do not include any explanatory text, markdown formatting, or code blocks.
"""

# Function to run the completion and display results
def get_movie_data(prompt, title="Example"):
    print(f"\n--- {title} ---")
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Tell me about The Matrix"}
        ]
    )
    
    response_content = completion.choices[0].message.content
    print("Raw response:")
    print(response_content)
    
    # Try to parse as JSON
    try:
        movie_data = json.loads(response_content)
        print("\nSuccessfully parsed as JSON!")
        
        # Check for expected fields
        expected_fields = ["title", "year", "director", "genre", 
                           "runtime_minutes", "rating", "box_office_millions", "cast"]
        missing_fields = [field for field in expected_fields if field not in movie_data]
        
        if missing_fields:
            print(f"Missing fields: {', '.join(missing_fields)}")
        else:
            print("All expected fields present!")
            
    except json.JSONDecodeError:
        print("\nFailed to parse as JSON. Response is not valid JSON.")

# Compare the results of both prompts
get_movie_data(poor_prompt, "Poor Prompt Example")
get_movie_data(effective_prompt, "Effective Prompt Example")
```

---

## Required parameters

URL: https://console.groq.com/docs/text-chat/scripts/streaming-chat-completion-with-stop.py

```python
from groq import Groq

client = Groq()

chat_completion = client.chat.completions.create(
    #
    # Required parameters
    #
    messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": "Count to10. Your response must begin with \"1, \". example:1,2,3, ...",
        }
    ],

    # The language model which will generate the completion.
    model="llama-3.3-70b-versatile",

    #
    # Optional parameters
    #

    # Controls randomness: lowering results in less random completions.
    # As the temperature approaches zero, the model will become deterministic
    # and repetitive.
    temperature=0.5,

    # The maximum number of tokens to generate. Requests can use up to
    #2048 tokens shared between prompt and completion.
    max_completion_tokens=1024,

    # Controls diversity via nucleus sampling:0.5 means half of all
    # likelihood-weighted options are considered.
    top_p=1,

    # A stop sequence is a predefined or user-specified text string that
    # signals an AI to stop generating content, ensuring its responses
    # remain focused and concise. Examples include punctuation marks and
    # markers like "[end]".
    # For this example, we will use ",6" so that the llm stops counting at5.
    # If multiple stop values are needed, an array of string may be passed,
    # stop=[",6", ", six", ", Six"]
    stop=",6",

    # If set, partial message deltas will be sent.
    stream=False,
)

# Print the completion returned by the LLM.
print(chat_completion.choices[0].message.content)
```

---

## Text Chat: System Prompt (js)

URL: https://console.groq.com/docs/text-chat/scripts/system-prompt

```javascript
import { Groq } from "groq-sdk";

const groq = new Groq();

async function main() {
  const response = await groq.chat.completions.create({
    model: "llama3-8b-8192",
    messages: [
      {
        role: "system",
        content: `You are a data analysis API that performs sentiment analysis on text.
 Respond only with JSON using this format:
 {
 "sentiment_analysis": {
 "sentiment": "positive|negative|neutral",
 "confidence_score":0.95,
 "key_phrases": [
 {
 "phrase": "detected key phrase",
 "sentiment": "positive|negative|neutral"
 }
 ],
 "summary": "One sentence summary of the overall sentiment"
 }
 }`
      },
      { role: "user", content: "Analyze the sentiment of this customer review: 'I absolutely love this product! The quality exceeded my expectations, though shipping took longer than expected.'" }
    ],
    response_format: { type: "json_object" }
  });

  console.log(response.choices[0].message.content);
}

main();
```

---

## Data model for LLM to generate

URL: https://console.groq.com/docs/text-chat/scripts/json-mode.py

from typing import List, Optional
import json

from pydantic import BaseModel
from groq import Groq

groq = Groq()


# Data model for LLM to generate
class Ingredient(BaseModel):
 name: str
 quantity: str
 quantity_unit: Optional[str]


class Recipe(BaseModel):
 recipe_name: str
 ingredients: List[Ingredient]
 directions: List[str]


def get_recipe(recipe_name: str) -> Recipe:
 chat_completion = groq.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a recipe database that outputs recipes in JSON.\n"
 # Pass the json schema to the model. Pretty printing improves results.
 f" The JSON object must use the schema: {json.dumps(Recipe.model_json_schema(), indent=2)}",
 },
 {
 "role": "user",
 "content": f"Fetch a recipe for {recipe_name}",
 },
 ],
 model="llama3-70b-8192",
 temperature=0,
 # Streaming is not supported in JSON mode
 stream=False,
 # Enable JSON mode by setting the response format
 response_format={"type": "json_object"},
 )
 return Recipe.model_validate_json(chat_completion.choices[0].message.content)


def print_recipe(recipe: Recipe):
 print("Recipe:", recipe.recipe_name)

 print("\nIngredients:")
 for ingredient in recipe.ingredients:
 print(
 f"- {ingredient.name}: {ingredient.quantity} {ingredient.quantity_unit or ''}"
 )
 print("\nDirections:")
 for step, direction in enumerate(recipe.directions, start=1):
 print(f"{step}. {direction}")


recipe = get_recipe("apple pie")
print_recipe(recipe)

---

## pip install pydantic

URL: https://console.groq.com/docs/text-chat/scripts/instructor-example.py

```python
import os
from typing import List
from pydantic import BaseModel, Field 
import instructor 
from groq import Groq

# Set up instructor with Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# Patch the client with instructor
instructor_client = instructor.patch(client)

# Define your schema with Pydantic
class RecipeIngredient(BaseModel):
 name: str
 quantity: str
 unit: str = Field(description="The unit of measurement, like cup, tablespoon, etc.")

class Recipe(BaseModel):
 title: str
 description: str
 prep_time_minutes: int
 cook_time_minutes: int
 ingredients: List[RecipeIngredient]
 instructions: List[str] = Field(description="Step by step cooking instructions")
    
# Request structured data with automatic validation
recipe = instructor_client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 response_model=Recipe,
 messages=[
 {"role": "user", "content": "Give me a recipe for chocolate chip cookies"}
 ],
 max_retries=2 
)

# No need for try/except or manual validation - instructor handles it!
print(f"Recipe: {recipe.title}")
print(f"Prep time: {recipe.prep_time_minutes} minutes")
print(f"Cook time: {recipe.cook_time_minutes} minutes")
print("\nIngredients:")
for ingredient in recipe.ingredients:
 print(f"- {ingredient.quantity} {ingredient.unit} {ingredient.name}")
print("\nInstructions:")
for i, step in enumerate(recipe.instructions,1):
 print(f"{i}. {step}") 
```

---

## Text Chat: Basic Validation Zod.doc (ts)

URL: https://console.groq.com/docs/text-chat/scripts/basic-validation-zod.doc

```javascript
import { Groq } from "groq-sdk";
import { z } from "zod"; 

const client = new Groq();

// Define a schema with Zod
const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number().positive(),
  description: z.string(),
  in_stock: z.boolean(),
  tags: z.array(z.string()).default([]),
});

// Infer the TypeScript type from the Zod schema
type Product = z.infer<typeof ProductSchema>;

// Create a prompt that clearly defines the expected structure
const systemPrompt = `
You are a product catalog assistant. When asked about products,
always respond with valid JSON objects that match this structure:
{
  "id": "string",
  "name": "string",
  "price": number,
  "description": "string",
  "in_stock": boolean,
  "tags": ["string"]
}
Your response should ONLY contain the JSON object and nothing else.
`;

async function getStructuredResponse(): Promise<Product | undefined> {
  try {
    // Request structured data from the model
    const completion = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: "Tell me about a popular smartphone product" },
      ],
    });

    // Extract the response
    const responseContent = completion.choices[0].message.content;
    
    // Parse and validate JSON
    const jsonData = JSON.parse(responseContent || "");
    const validatedData = ProductSchema.parse(jsonData);
    
    console.log("Validation successful! Structured data:");
    console.log(JSON.stringify(validatedData, null,2));
    
    return validatedData;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("Schema validation failed:", error.errors);
    } else if (error instanceof SyntaxError) {
      console.error("JSON parsing failed: The model did not return valid JSON");
    } else {
      console.error("Error:", error);
    }
    return undefined;
  }
}

getStructuredResponse();
```

---

## Text Chat: Instructor Example.doc (ts)

URL: https://console.groq.com/docs/text-chat/scripts/instructor-example.doc

```javascript
import { Groq } from "groq-sdk";
import Instructor from "@instructor-ai/instructor"; // npm install @instructor-ai/instructor
import { z } from "zod"; // npm install zod

// Set up the Groq client with Instructor
const client = new Groq();
const instructor = Instructor({
  client,
  mode: "TOOLS"
});

// Define your schema with Zod
const RecipeIngredientSchema = z.object({
  name: z.string(),
  quantity: z.string(),
  unit: z.string().describe("The unit of measurement, like cup, tablespoon, etc."),
});

const RecipeSchema = z.object({
  title: z.string(),
  description: z.string(),
  prep_time_minutes: z.number().int().positive(),
  cook_time_minutes: z.number().int().positive(),
  ingredients: z.array(RecipeIngredientSchema),
  instructions: z.array(z.string()).describe("Step by step cooking instructions"),
});

// Infer TypeScript types from Zod schemas
type Recipe = z.infer<typeof RecipeSchema>;

async function getRecipe(): Promise<Recipe | undefined> {
  try {
    // Request structured data with automatic validation
    const recipe = await instructor.chat.completions.create({
      model: "llama3-70b-8192",
      response_model: {
        name: "Recipe",
        schema: RecipeSchema,
      },
      messages: [
        { role: "user", content: "Give me a recipe for chocolate chip cookies" },
      ],
      max_retries:2, // Instructor will retry if validation fails
    });

    // No need for try/catch or manual validation - instructor handles it!
    console.log(`Recipe: ${recipe.title}`);
    console.log(`Prep time: ${recipe.prep_time_minutes} minutes`);
    console.log(`Cook time: ${recipe.cook_time_minutes} minutes`);
    console.log("\nIngredients:");
    recipe.ingredients.forEach((ingredient) => {
      console.log(`- ${ingredient.quantity} ${ingredient.unit} ${ingredient.name}`);
    });
    console.log("\nInstructions:");
    recipe.instructions.forEach((step, index) => {
      console.log(`${index +1}. ${step}`);
    });

    return recipe;
  } catch (error) {
    console.error("Error:", error);
    return undefined;
  }
}

// Run the example
getRecipe();
```

---

## Text Chat: Json Mode (js)

URL: https://console.groq.com/docs/text-chat/scripts/json-mode

import Groq from "groq-sdk";
const groq = new Groq();

// Define the JSON schema for recipe objects
// This is the schema that the model will use to generate the JSON object, 
// which will be parsed into the Recipe class.
const schema = {
 $defs: {
 Ingredient: {
 properties: {
 name: { title: "Name", type: "string" },
 quantity: { title: "Quantity", type: "string" },
 quantity_unit: {
 anyOf: [{ type: "string" }, { type: "null" }],
 title: "Quantity Unit",
 },
 },
 required: ["name", "quantity", "quantity_unit"],
 title: "Ingredient",
 type: "object",
 },
 },
 properties: {
 recipe_name: { title: "Recipe Name", type: "string" },
 ingredients: {
 items: { $ref: "#/$defs/Ingredient" },
 title: "Ingredients",
 type: "array",
 },
 directions: {
 items: { type: "string" },
 title: "Directions",
 type: "array",
 },
 },
 required: ["recipe_name", "ingredients", "directions"],
 title: "Recipe",
 type: "object",
};

// Ingredient class representing a single recipe ingredient
class Ingredient {
 constructor(name, quantity, quantity_unit) {
 this.name = name;
 this.quantity = quantity;
 this.quantity_unit = quantity_unit || null;
 }
}

// Recipe class representing a complete recipe
class Recipe {
 constructor(recipe_name, ingredients, directions) {
 this.recipe_name = recipe_name;
 this.ingredients = ingredients;
 this.directions = directions;
 }
}

// Generates a recipe based on the recipe name
export async function getRecipe(recipe_name) {
 // Pretty printing improves completion results
 const jsonSchema = JSON.stringify(schema, null,4);
 const chat_completion = await groq.chat.completions.create({
 messages: [
 {
 role: "system",
 content: `You are a recipe database that outputs recipes in JSON.\n'The JSON object must use the schema: ${jsonSchema}`,
 },
 {
 role: "user",
 content: `Fetch a recipe for ${recipe_name}`,
 },
 ],
 model: "llama-3.3-70b-versatile",
 temperature:0,
 stream: false,
 response_format: { type: "json_object" },
 });

 const recipeJson = JSON.parse(chat_completion.choices[0].message.content);

 // Map the JSON ingredients to the Ingredient class
 const ingredients = recipeJson.ingredients.map((ingredient) => {
 return new Ingredient(ingredient.name, ingredient.quantity, ingredient.quantity_unit);
 });

 // Return the recipe object
 return new Recipe(recipeJson.recipe_name, ingredients, recipeJson.directions);
}

// Prints a recipe to the console with nice formatting
function printRecipe(recipe) {
 console.log("Recipe:", recipe.recipe_name);
 console.log();

 console.log("Ingredients:");
 recipe.ingredients.forEach((ingredient) => {
 console.log(
 `- ${ingredient.name}: ${ingredient.quantity} ${
 ingredient.quantity_unit || ""
 }`,
 );
 });
 console.log();

 console.log("Directions:");
 recipe.directions.forEach((direction, step) => {
 console.log(`${step +1}. ${direction}`);
 });
}

// Main function that generates and prints a recipe
export async function main() {
 const recipe = await getRecipe("apple pie");
 printRecipe(recipe);
}

main();

---

## Text Chat: Prompt Engineering (js)

URL: https://console.groq.com/docs/text-chat/scripts/prompt-engineering

```javascript
import { Groq } from "groq-sdk";

const client = new Groq();

// Example of a poorly designed prompt
const poorPrompt = `
Give me information about a movie in JSON format.
`;

// Example of a well-designed prompt
const effectivePrompt = `
You are a movie database API. Return information about a movie with the following 
JSON structure:

{
 "title": "string",
 "year": number,
 "director": "string",
 "genre": ["string"],
 "runtime_minutes": number,
 "rating": number (1-10 scale),
 "box_office_millions": number,
 "cast": [
 {
 "actor": "string",
 "character": "string"
 }
 ]
}

The response must:
1. Include ALL fields shown above
2. Use only the exact field names shown
3. Follow the exact data types specified
4. Contain ONLY the JSON object and nothing else

IMPORTANT: Do not include any explanatory text, markdown formatting, or code blocks.
`;

// Function to run the completion and display results
async function getMovieData(prompt, title = "Example") {
  console.log(`\n--- ${title} ---`);
  
  try {
    const completion = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: prompt },
        { role: "user", content: "Tell me about The Matrix" },
      ],
    });
    
    const responseContent = completion.choices[0].message.content;
    console.log("Raw response:");
    console.log(responseContent);
    
    // Try to parse as JSON
    try {
      const movieData = JSON.parse(responseContent || "");
      console.log("\nSuccessfully parsed as JSON!");
      
      // Check for expected fields
      const expectedFields = ["title", "year", "director", "genre", 
      "runtime_minutes", "rating", "box_office_millions", "cast"];
      const missingFields = expectedFields.filter(field => !(field in movieData));
      
      if (missingFields.length > 0) {
        console.log(`Missing fields: ${missingFields.join(', ')}`);
      } else {
        console.log("All expected fields present!");
      }
      
      return movieData;
    } catch (syntaxError) {
      console.log("\nFailed to parse as JSON. Response is not valid JSON.");
      return null;
    }
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
}

// Compare the results of both prompts
async function comparePrompts() {
  await getMovieData(poorPrompt, "Poor Prompt Example");
  await getMovieData(effectivePrompt, "Effective Prompt Example");
}

// Run the examples
comparePrompts();
```

---

## Text Chat: Prompt Engineering.doc (ts)

URL: https://console.groq.com/docs/text-chat/scripts/prompt-engineering.doc

```javascript
import { Groq } from "groq-sdk";
import { z } from "zod"; 

const client = new Groq();

// Define a schema for validation
const MovieSchema = z.object({
  title: z.string(),
  year: z.number().int(),
  director: z.string(),
  genre: z.array(z.string()),
  runtime_minutes: z.number().int(),
  rating: z.number().min(1).max(10),
  box_office_millions: z.number(),
  cast: z.array(
    z.object({
      actor: z.string(),
      character: z.string()
    })
  )
});

type Movie = z.infer<typeof MovieSchema>;

// Example of a poorly designed prompt
const poorPrompt = `
Give me information about a movie in JSON format.
`;

// Example of a well-designed prompt
const effectivePrompt = `
You are a movie database API. Return information about a movie with the following 
JSON structure:

{
 "title": "string",
 "year": number,
 "director": "string",
 "genre": ["string"],
 "runtime_minutes": number,
 "rating": number (1-10 scale),
 "box_office_millions": number,
 "cast": [
 {
 "actor": "string",
 "character": "string"
 }
 ]
}

The response must:
1. Include ALL fields shown above
2. Use only the exact field names shown
3. Follow the exact data types specified
4. Contain ONLY the JSON object and nothing else

IMPORTANT: Do not include any explanatory text, markdown formatting, or code blocks.
`;

// Function to run the completion and display results
async function getMovieData(prompt: string, title = "Example"): Promise<Movie | null> {
  console.log(`\n--- ${title} ---`);
  
  try {
    const completion = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: prompt },
        { role: "user", content: "Tell me about The Matrix" },
      ],
    });
    
    const responseContent = completion.choices[0].message.content;
    console.log("Raw response:");
    console.log(responseContent);
    
    // Try to parse as JSON
    try {
      const movieData = JSON.parse(responseContent || "");
      console.log("\nSuccessfully parsed as JSON!");
      
      // Validate against schema
      try {
        const validatedMovie = MovieSchema.parse(movieData);
        console.log("All expected fields present and valid!");
        return validatedMovie;
      } catch (validationError) {
        if (validationError instanceof z.ZodError) {
          console.log("Schema validation failed:");
          console.log(validationError.errors.map(e => `- ${e.path.join('.')}: ${e.message}`).join('\n'));
        }
        return null;
      }
    } catch (syntaxError) {
      console.log("\nFailed to parse as JSON. Response is not valid JSON.");
      return null;
    }
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
}

// Compare the results of both prompts
async function comparePrompts() {
  await getMovieData(poorPrompt, "Poor Prompt Example");
  await getMovieData(effectivePrompt, "Effective Prompt Example");
}

// Run the examples
comparePrompts();
```

---

## pip install pydantic

URL: https://console.groq.com/docs/text-chat/scripts/complex-schema-example.py

```python
import os
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field 
from groq import Groq
import instructor 

# Set up the client with instructor
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
instructor_client = instructor.patch(client)

# Define a complex nested schema
class Address(BaseModel):
 street: str
 city: str
 state: str
 zip_code: str
 country: str

class ContactInfo(BaseModel):
 email: str
 phone: Optional[str] = None
 address: Address

class ProductVariant(BaseModel):
 id: str
 name: str
 price: float
 inventory_count: int
 attributes: Dict[str, str]

class ProductReview(BaseModel):
 user_id: str
 rating: float = Field(ge=1, le=5)
 comment: str
 date: str

class Product(BaseModel):
 id: str
 name: str
 description: str
 main_category: str
 subcategories: List[str]
 variants: List[ProductVariant]
 reviews: List[ProductReview]
 average_rating: float = Field(ge=1, le=5)
 manufacturer: Dict[str, Union[str, ContactInfo]]

# System prompt with clear instructions about the complex structure
system_prompt = """
You are a product catalog API. Generate a detailed product with ALL required fields.
Your response must be a valid JSON object matching the following schema:

{
 "id": "string",
 "name": "string",
 "description": "string",
 "main_category": "string",
 "subcategories": ["string"],
 "variants": [
 {
 "id": "string",
 "name": "string",
 "price": number,
 "inventory_count": number,
 "attributes": {"key": "value"}
 }
 ],
 "reviews": [
 {
 "user_id": "string",
 "rating": number (1-5),
 "comment": "string",
 "date": "string (YYYY-MM-DD)"
 }
 ],
 "average_rating": number (1-5),
 "manufacturer": {
 "name": "string",
 "founded": "string",
 "contact_info": {
 "email": "string",
 "phone": "string (optional)",
 "address": {
 "street": "string",
 "city": "string", 
 "state": "string",
 "zip_code": "string",
 "country": "string"
 }
 }
 }
}
"""

# Use instructor to create and validate in one step
product = instructor_client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 response_model=Product,
 messages=[
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": "Give me details about a high-end camera product"}
 ],
 max_retries=3
)

# Print the validated complex object
print(f"Product: {product.name}")
print(f"Description: {product.description[:100]}...")
print(f"Variants: {len(product.variants)}")
print(f"Reviews: {len(product.reviews)}")
print(f"Manufacturer: {product.manufacturer.get('name')}")
print("\nManufacturer Contact:")
contact_info = product.manufacturer.get('contact_info')
if isinstance(contact_info, ContactInfo):
 print(f" Email: {contact_info.email}")
 print(f" Address: {contact_info.address.city}, {contact_info.address.country}")
```

---

## Text Chat: System Prompt (py)

URL: https://console.groq.com/docs/text-chat/scripts/system-prompt.py

```python
from groq import Groq

client = Groq()

response = client.chat.completions.create(
 model="llama3-8b-8192",
 messages=[
 {
 "role": "system",
 "content": "You are a data analysis API that performs sentiment analysis on text. Respond only with JSON using this format: {\"sentiment_analysis\": {\"sentiment\": \"positive|negative|neutral\", \"confidence_score\":0.95, \"key_phrases\": [{\"phrase\": \"detected key phrase\", \"sentiment\": \"positive|negative|neutral\"}], \"summary\": \"One sentence summary of the overall sentiment\"}}"
 },
 {
 "role": "user",
 "content": "Analyze the sentiment of this customer review: 'I absolutely love this product! The quality exceeded my expectations, though shipping took longer than expected.'"
 }
 ],
 response_format={"type": "json_object"}
)

print(response.choices[0].message.content)
```

---

## Text Chat: Streaming Chat Completion With Stop (js)

URL: https://console.groq.com/docs/text-chat/scripts/streaming-chat-completion-with-stop

```javascript
import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
  const stream = await getGroqChatStream();
  for await (const chunk of stream) {
    // Print the completion returned by the LLM.
    process.stdout.write(chunk.choices[0]?.delta?.content || "");
  }
}

export async function getGroqChatStream() {
  return groq.chat.completions.create({
    //
    // Required parameters
    //
    messages: [
      // Set an optional system message. This sets the behavior of the
      // assistant and can be used to provide specific instructions for
      // how it should behave throughout the conversation.
      {
        role: "system",
        content: "You are a helpful assistant.",
      },
      // Set a user message for the assistant to respond to.
      {
        role: "user",
        content:
          "Start at1 and count to10. Separate each number with a comma and a space",
      },
    ],

    // The language model which will generate the completion.
    model: "llama-3.3-70b-versatile",

    //
    // Optional parameters
    //

    // Controls randomness: lowering results in less random completions.
    // As the temperature approaches zero, the model will become deterministic
    // and repetitive.
    temperature: 0.5,

    // The maximum number of tokens to generate. Requests can use up to
    //2048 tokens shared between prompt and completion.
    max_completion_tokens: 1024,

    // Controls diversity via nucleus sampling:0.5 means half of all
    // likelihood-weighted options are considered.
    top_p: 1,

    // A stop sequence is a predefined or user-specified text string that
    // signals an AI to stop generating content, ensuring its responses
    // remain focused and concise. Examples include punctuation marks and
    // markers like "[end]".
    //
    // For this example, we will use ",6" so that the llm stops counting at5.
    // If multiple stop values are needed, an array of string may be passed,
    // stop: [",6", ", six", ", Six"]
    stop: ",6",

    // If set, partial message deltas will be sent.
    stream: true,
  });
}

main();
```

---

## Text Chat: Complex Schema Example.doc (ts)

URL: https://console.groq.com/docs/text-chat/scripts/complex-schema-example.doc

```javascript
import { Groq } from "groq-sdk";
import Instructor from "@instructor-ai/instructor"; 
import { z } from "zod"; 

// Set up the client with Instructor
const groq = new Groq();
const instructor = Instructor({
  client: groq,
  mode: "TOOLS"
})

// Define a complex nested schema
const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  state: z.string(),
  zip_code: z.string(),
  country: z.string(),
});

const ContactInfoSchema = z.object({
  email: z.string().email(),
  phone: z.string().optional(),
  address: AddressSchema,
});

const ProductVariantSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number().positive(),
  inventory_count: z.number().int().nonnegative(),
  attributes: z.record(z.string()),
});

const ProductReviewSchema = z.object({
  user_id: z.string(),
  rating: z.number().min(1).max(5),
  comment: z.string(),
  date: z.string(),
});

const ManufacturerSchema = z.object({
  name: z.string(),
  founded: z.string(),
  contact_info: ContactInfoSchema,
});

const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  main_category: z.string(),
  subcategories: z.array(z.string()),
  variants: z.array(ProductVariantSchema),
  reviews: z.array(ProductReviewSchema),
  average_rating: z.number().min(1).max(5),
  manufacturer: ManufacturerSchema,
});

// Infer TypeScript types from Zod schemas
type Product = z.infer<typeof ProductSchema>;

// System prompt with clear instructions about the complex structure
const systemPrompt = `
You are a product catalog API. Generate a detailed product with ALL required fields.
Your response must be a valid JSON object matching the schema I will use to validate it.
`;

async function getComplexProduct(): Promise<Product | undefined> {
  try {
    // Use instructor to create and validate in one step
    const product = await instructor.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_model: {
        name: "Product",
        schema: ProductSchema,
      },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: "Give me details about a high-end camera product" },
      ],
      max_retries:3,
    });

    // Print the validated complex object
    console.log(`Product: ${product.name}`);
    console.log(`Description: ${product.description.substring(0,100)}...`);
    console.log(`Variants: ${product.variants.length}`);
    console.log(`Reviews: ${product.reviews.length}`);
    console.log(`Manufacturer: ${product.manufacturer.name}`);
    console.log(`\nManufacturer Contact:`);
    console.log(` Email: ${product.manufacturer.contact_info.email}`);
    console.log(` Address: ${product.manufacturer.contact_info.address.city}, ${product.manufacturer.contact_info.address.country}`);

    return product;
  } catch (error) {
    console.error("Error:", error);
    return undefined;
  }
}

// Run the example
getComplexProduct();
```

---

## Required parameters

URL: https://console.groq.com/docs/text-chat/scripts/streaming-async-chat-completion.py

```python
import asyncio

from groq import AsyncGroq


async def main():
    client = AsyncGroq()

    stream = await client.chat.completions.create(
        #
        # Required parameters
        #
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": "Explain the importance of fast language models"
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile",

        #
        # Optional parameters
        #

        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become
        # deterministic and repetitive.
        temperature=0.5,

        # The maximum number of tokens to generate. Requests can use up to
        #2048 tokens shared between prompt and completion.
        max_completion_tokens=1024,

        # Controls diversity via nucleus sampling:0.5 means half of all
        # likelihood-weighted options are considered.
        top_p=1,

        # A stop sequence is a predefined or user-specified text string that
        # signals an AI to stop generating content, ensuring its responses
        # remain focused and concise. Examples include punctuation marks and
        # markers like "[end]".
        stop=None,

        # If set, partial message deltas will be sent.
        stream=True,
    )

    # Print the incremental deltas returned by the LLM.
    async for chunk in stream:
        print(chunk.choices[0].delta.content, end="")

asyncio.run(main())
```

---

## Text Chat: Streaming Chat Completion (js)

URL: https://console.groq.com/docs/text-chat/scripts/streaming-chat-completion

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 const stream = await getGroqChatStream();
 for await (const chunk of stream) {
 // Print the completion returned by the LLM.
 process.stdout.write(chunk.choices[0]?.delta?.content || "");
 }
}

export async function getGroqChatStream() {
 return groq.chat.completions.create({
 //
 // Required parameters
 //
 messages: [
 // Set an optional system message. This sets the behavior of the
 // assistant and can be used to provide specific instructions for
 // how it should behave throughout the conversation.
 {
 role: "system",
 content: "You are a helpful assistant.",
 },
 // Set a user message for the assistant to respond to.
 {
 role: "user",
 content: "Explain the importance of fast language models",
 },
 ],

 // The language model which will generate the completion.
 model: "llama-3.3-70b-versatile",

 //
 // Optional parameters
 //

 // Controls randomness: lowering results in less random completions.
 // As the temperature approaches zero, the model will become deterministic
 // and repetitive.
 temperature:0.5,

 // The maximum number of tokens to generate. Requests can use up to
 //2048 tokens shared between prompt and completion.
 max_completion_tokens:1024,

 // Controls diversity via nucleus sampling:0.5 means half of all
 // likelihood-weighted options are considered.
 top_p:1,

 // A stop sequence is a predefined or user-specified text string that
 // signals an AI to stop generating content, ensuring its responses
 // remain focused and concise. Examples include punctuation marks and
 // markers like "[end]".
 stop: null,

 // If set, partial message deltas will be sent.
 stream: true,
 });
}

main();

---

## pip install pydantic

URL: https://console.groq.com/docs/text-chat/scripts/basic-validation-zod.py

```python
import os
import json
from groq import Groq
from pydantic import BaseModel, Field, ValidationError 
from typing import List

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define a schema with Pydantic (Python's equivalent to Zod)
class Product(BaseModel):
 id: str
 name: str
 price: float
 description: str
 in_stock: bool
 tags: List[str] = Field(default_factory=list)
    
# Prompt design is critical for structured outputs
system_prompt = """
You are a product catalog assistant. When asked about products,
always respond with valid JSON objects that match this structure:
{
 "id": "string",
 "name": "string",
 "price": number,
 "description": "string",
 "in_stock": boolean,
 "tags": ["string"]
}
Your response should ONLY contain the JSON object and nothing else.
"""

# Request structured data from the model
completion = client.chat.completions.create(
 model="llama-3.3-70b-versatile",
 response_format={"type": "json_object"},
 messages=[
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": "Tell me about a popular smartphone product"}
 ]
)

# Extract and validate the response
try:
 response_content = completion.choices[0].message.content
 # Parse JSON
 json_data = json.loads(response_content)
 # Validate against schema
 product = Product(**json_data)
 print("Validation successful! Structured data:")
 print(product.model_dump_json(indent=2))
except json.JSONDecodeError:
 print("Error: The model did not return valid JSON")
except ValidationError as e:
 print(f"Error: The JSON did not match the expected schema: {e}")
```

---

## Set an optional system message. This sets the behavior of the

URL: https://console.groq.com/docs/text-chat/scripts/basic-chat-completion.py

from groq import Groq

client = Groq()

chat_completion = client.chat.completions.create(
 messages=[
 # Set an optional system message. This sets the behavior of the
 # assistant and can be used to provide specific instructions for
 # how it should behave throughout the conversation.
 {
 "role": "system",
 "content": "You are a helpful assistant."
 },
 # Set a user message for the assistant to respond to.
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],

 # The language model which will generate the completion.
 model="llama-3.3-70b-versatile"
)

# Print the completion returned by the LLM.
print(chat_completion.choices[0].message.content)

---

## Text Chat: Basic Chat Completion (js)

URL: https://console.groq.com/docs/text-chat/scripts/basic-chat-completion

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 const completion = await getGroqChatCompletion();
 console.log(completion.choices[0]?.message?.content || "");
}

export const getGroqChatCompletion = async () => {
 return groq.chat.completions.create({
 messages: [
 // Set an optional system message. This sets the behavior of the
 // assistant and can be used to provide specific instructions for
 // how it should behave throughout the conversation.
 {
 role: "system",
 content: "You are a helpful assistant.",
 },
 // Set a user message for the assistant to respond to.
 {
 role: "user",
 content: "Explain the importance of fast language models",
 },
 ],
 model: "llama-3.3-70b-versatile",
 });
};

main();

---

## Text Chat: Basic Validation Zod (js)

URL: https://console.groq.com/docs/text-chat/scripts/basic-validation-zod

```javascript
import { Groq } from "groq-sdk";
import { z } from "zod"; 

const client = new Groq();

// Define a schema with Zod
const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number().positive(),
  description: z.string(),
  in_stock: z.boolean(),
  tags: z.array(z.string()).default([]),
});

// Create a prompt that clearly defines the expected structure
const systemPrompt = `
You are a product catalog assistant. When asked about products,
always respond with valid JSON objects that match this structure:
{
  "id": "string",
  "name": "string",
  "price": number,
  "description": "string",
  "in_stock": boolean,
  "tags": ["string"]
}
Your response should ONLY contain the JSON object and nothing else.
`;

async function getStructuredResponse() {
  try {
    // Request structured data from the model
    const completion = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: "Tell me about a popular smartphone product" },
      ],
    });

    // Extract the response
    const responseContent = completion.choices[0].message.content;
    
    // Parse and validate JSON
    const jsonData = JSON.parse(responseContent || "");
    const validatedData = ProductSchema.parse(jsonData);
    
    console.log("Validation successful! Structured data:");
    console.log(JSON.stringify(validatedData, null,2));
    
    return validatedData;
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("Schema validation failed:", error.errors);
    } else if (error instanceof SyntaxError) {
      console.error("JSON parsing failed: The model did not return valid JSON");
    } else {
      console.error("Error:", error);
    }
  }
}

// Run the example
getStructuredResponse();
```

---

## Required parameters

URL: https://console.groq.com/docs/text-chat/scripts/streaming-chat-completion.py

```python
from groq import Groq

client = Groq()

stream = client.chat.completions.create(
    #
    # Required parameters
    #
    messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],

    # The language model which will generate the completion.
    model="llama-3.3-70b-versatile",

    #
    # Optional parameters
    #

    # Controls randomness: lowering results in less random completions.
    # As the temperature approaches zero, the model will become deterministic
    # and repetitive.
    temperature=0.5,

    # The maximum number of tokens to generate. Requests can use up to
    #2048 tokens shared between prompt and completion.
    max_completion_tokens=1024,

    # Controls diversity via nucleus sampling:0.5 means half of all
    # likelihood-weighted options are considered.
    top_p=1,

    # A stop sequence is a predefined or user-specified text string that
    # signals an AI to stop generating content, ensuring its responses
    # remain focused and concise. Examples include punctuation marks and
    # markers like "[end]".
    stop=None,

    # If set, partial message deltas will be sent.
    stream=True,
)

# Print the incremental deltas returned by the LLM.
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
```

---

## Required parameters

URL: https://console.groq.com/docs/text-chat/scripts/performing-async-chat-completion.py

```python
import asyncio

from groq import AsyncGroq


async def main():
    client = AsyncGroq()

    chat_completion = await client.chat.completions.create(
        #
        # Required parameters
        #
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": "Explain the importance of fast language models"
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile",

        #
        # Optional parameters
        #

        # Controls randomness: lowering results in less random completions.
        # As the temperature approaches zero, the model will become
        # deterministic and repetitive.
        temperature=0.5,

        # The maximum number of tokens to generate. Requests can use up to
        #2048 tokens shared between prompt and completion.
        max_completion_tokens=1024,

        # Controls diversity via nucleus sampling:0.5 means half of all
        # likelihood-weighted options are considered.
        top_p=1,

        # A stop sequence is a predefined or user-specified text string that
        # signals an AI to stop generating content, ensuring its responses
        # remain focused and concise. Examples include punctuation marks and
        # markers like "[end]".
        stop=None,

        # If set, partial message deltas will be sent.
        stream=False,
    )

    # Print the completion returned by the LLM.
    print(chat_completion.choices[0].message.content)

asyncio.run(main())
```

---

## Text Generation

URL: https://console.groq.com/docs/text-chat

## Text Generation

<br />

Generating text with Groq's Chat Completions API enables you to have natural, conversational interactions with Groq's large language models. It processes a series of messages and generates human-like responses that can be used for various applications including conversational agents, content generation, task automation, and generating structured data outputs like JSON for your applications.

## On This Page

- [Chat Completions](#chat-completions)
- [Basic Chat Completion](#performing-a-basic-chat-completion)
- [Streaming Chat Completion](#streaming-a-chat-completion)
- [Using Stop Sequences](#performing-a-chat-completion-with-a-stop-sequence)
- [JSON Mode](#json-mode)
- [JSON Mode with Schema Validation](#json-mode-with-schema-validation)

## Chat Completions

Chat completions allow your applications to have dynamic interactions with Groq's models. You can send messages that include user inputs and system instructions, and receive responses that match the conversational context.
<br />
Chat models can handle both multi-turn discussions (conversations with multiple back-and-forth exchanges) and single-turn tasks where you need just one response.
<br />
For details about all available parameters, [visit the API reference page.](https://console.groq.com/docs/api-reference#chat-create)

### Getting Started with Groq SDK

To start using Groq's Chat Completions API, you'll need to install the [Groq SDK](/docs/libraries) and set up your [API key](https://console.groq.com/keys).

## JSON Mode

JSON mode is a specialized feature that guarantees all chat completions will be returned as valid JSON. This is particularly useful for applications that need to parse and process structured data from model responses.
<br/>
For more information on ensuring that the JSON output adheres to a specific schema, jump to: [JSON Mode with Schema Validation](#json-mode-with-schema-validation).

### How to Use JSON Mode

To use JSON mode:

1. Set `"response_format": {"type": "json_object"}` in your chat completion request
2. Include a description of the desired JSON structure in your system prompt
3. Process the returned JSON in your application

### Best Practices for JSON Generation

- **Choose the right model**: Llama performs best at generating JSON, followed by Gemma
- **Format preference**: Request pretty-printed JSON instead of compact JSON for better readability
- **Keep prompts concise**: Clear, direct instructions produce better JSON outputs
- **Provide schema examples**: Include examples of the expected JSON structure in your system prompt

### Limitations

- JSON mode does not support streaming responses
- Stop sequences cannot be used with JSON mode
- If JSON generation fails, Groq will return a400 error with code `json_validate_failed`

### Example System Prompts

Here are practical examples showing how to structure system messages that will produce well-formed JSON:

#### Data Analysis API

The Data Analysis API example demonstrates how to create a system prompt that instructs the model to perform sentiment analysis on user-provided text and return the results in a structured JSON format. This pattern can be adapted for various data analysis tasks such as classification, entity extraction, or summarization.

These examples show how to structure system prompts to guide the model to produce well-formed JSON with your desired schema.

<br />

Sample JSON output from the sentiment analysis prompt:

```js
{
 "sentiment_analysis": {
 "sentiment": "positive",
 "confidence_score":0.84,
 "key_phrases": [
 {
 "phrase": "absolutely love this product",
 "sentiment": "positive"
 },
 {
 "phrase": "quality exceeded my expectations",
 "sentiment": "positive"
 }
 ],
 "summary": "The reviewer loves the product's quality, but was slightly disappointed with the shipping time."
 }
}
```

In this JSON response:
- `sentiment`: Overall sentiment classification (positive, negative, or neutral)
- `confidence_score`: A numerical value between0 and1 indicating the model's confidence in its sentiment classification
- `key_phrases`: An array of important phrases extracted from the input text, each with its own sentiment classification
- `summary`: A concise summary of the sentiment analysis capturing the main points

<br />

Using structured JSON outputs like this makes it easy for your application to programmatically parse and process the model's analysis. For more information on validating JSON outputs, see our dedicated guide on [JSON Mode with Schema Validation](#json-mode-with-schema-validation).

## JSON Mode with Schema Validation

Schema validation allows you to ensure that the response conforms to a schema, making them more reliable and easier to process programmatically.
<br/>
While JSON mode ensures syntactically valid JSON, schema validation adds an additional layer of type checking and field validation to guarantee that the response not only parses as JSON but also conforms to your exact requirements.

### Using Zod (or Pydantic in Python)

[Zod](https://zod.dev/) is a TypeScript-first schema validation library that makes it easy to define and enforce schemas. In Python, [Pydantic](https://pydantic.dev/) serves a similar purpose. This example demonstrates validating a product catalog entry with basic fields like name, price, and description.

### Benefits of Schema Validation

- **Type Checking**: Ensure fields have the correct data types
- **Required Fields**: Specify which fields must be present
- **Constraints**: Set min/max values, length requirements, etc.
- **Default Values**: Provide fallbacks for missing fields
- **Custom Validation**: Add custom validation logic as needed

## Using Instructor Library

The [Instructor library](https://useinstructor.com/) provides a more streamlined experience by combining API calls with schema validation in a single step. This example creates a structured recipe with ingredients and cooking instructions, demonstrating automatic validation and retry logic.

### Advantages of Instructor

- **Retry Logic**: Automatically retry on validation failures
- **Error Messages**: Detailed error messages for model feedback
- **Schema Extraction**: The schema is translated into prompt instructions
- **Streamlined API**: Single function call for both completion and validation

## Prompt Engineering for Schema Validation

The quality of schema generation and validation depends heavily on how you formulate your system prompt. This example compares a poor prompt with a well-designed one by requesting movie information, showing how proper prompt design leads to more reliable structured data.

### Key Elements of Effective Prompts

1. **Clear Role Definition**: Tell the model it's an API or data service
2. **Complete Schema Example**: Show the exact structure with field names and types
3. **Explicit Requirements**: List all requirements clearly and numerically
4. **Data Type Specifications**: Indicate the expected type for each field
5. **Format Instructions**: Specify that the response should contain only JSON
6. **Constraints**: Add range or validation constraints where applicable

### Working with Complex Schemas

Real-world applications often require complex, nested schemas with multiple levels of objects, arrays, and optional fields. This example creates a detailed product catalog entry with variants, reviews, and manufacturer information, demonstrating how to handle deeply nested data structures.

### Tips for Complex Schemas

- **Decompose**: Break complex schemas into smaller, reusable components
- **Document Fields**: Add descriptions to fields in your schema definition
- **Provide Examples**: Include examples of valid objects in your prompt
- **Validate Incrementally**: Consider validating subparts of complex responses separately
- **Use Types**: Leverage type inference to ensure correct handling in your code

### Best Practices

### Working with Complex Schemas

Real-world applications often require complex, nested schemas with multiple levels of objects, arrays, and optional fields. 

### Tips for Complex Schemas

- **Decompose**: Break complex schemas into smaller, reusable components
- **Document Fields**: Add descriptions to fields in your schema definition
- **Provide Examples**: Include examples of valid objects in your prompt
- **Validate Incrementally**: Consider validating subparts of complex responses separately
- **Use Types**: Leverage type inference to ensure correct handling in your code

## Best Practices

- Start simple and add complexity as needed.
- Make fields optional when appropriate.
- Provide sensible defaults for optional fields.
- Use specific types and constraints rather than general ones.
- Add descriptions to your schema definitions.

---

## MLflow + Groq: Open-Source GenAI Observability

URL: https://console.groq.com/docs/mlflow

## MLflow + Groq: Open-Source GenAI Observability

[MLflow](https://mlflow.org/) is an open-source platform developed by Databricks to assist in building better Generative AI (GenAI) applications.

MLflow provides a tracing feature that enhances model observability in your GenAI applications by capturing detailed information about the requests 
you make to the models within your applications. Tracing provides a way to record the inputs, outputs, and metadata associated with each 
intermediate step of a request, enabling you to easily pinpoint the source of bugs and unexpected behaviors.

The MLflow integration with Groq includes the following features:
- **Tracing Dashboards**: Monitor your interactions with models via Groq API with dashboards that include inputs, outputs, and metadata of spans
- **Automated Tracing**: A fully automated integration with Groq, which can be enabled by running `mlflow.groq.autolog()`
- **Easy Manual Trace Instrumentation**: Customize trace instrumentation through MLflow's high-level fluent APIs such as decorators, function wrappers and context managers
- **OpenTelemetry Compatibility**: MLflow Tracing supports exporting traces to an OpenTelemetry Collector, which can then be used to export traces to various backends such as Jaeger, Zipkin, and AWS X-Ray
- **Package and Deploy Agents**: Package and deploy your agents with Groq LLMs to an inference server with a variety of deployment targets
- **Evaluation**: Evaluate your agents using Groq LLMs with a wide range of metrics using a convenient API called `mlflow.evaluate()`

## Python Quick Start (2 minutes to hello world)

###1. Install the required packages:
```python
# The Groq integration is available in mlflow >=2.20.0
pip install mlflow groq
```
###2. Configure your Groq API key:
```bash
export GROQ_API_KEY="your-api-key"
```

###3. (Optional) Start your mlflow server
```bash
# This process is optional, but it is recommended to use MLflow tracking server for better visualization and additional features
mlflow server
```
###4. Create your first traced Groq application:

Let's enable MLflow auto-tracing with the Groq SDK. For more configurations, refer to the [documentation for `mlflow.groq`](https://mlflow.org/docs/latest/python_api/mlflow.groq.html).
```python
import mlflow
import groq

# Optional: Set a tracking URI and an experiment name if you have a tracking server
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Groq")

# Turn on auto tracing for Groq by calling mlflow.groq.autolog()

client = groq.Groq()

# Use the create method to create new message
message = client.chat.completions.create(
 model="qwen-2.5-32b",
 messages=[
 {
 "role": "user",
 "content": "Explain the importance of low latency LLMs.",
 }
 ],
)

print(message.choices[0].message.content)
```

###5. Visualize model usage on the MLflow tracing dashboard:

Now traces for your Groq usage are captured by MLflow! Let's get insights into our application's activities by visiting the MLflow tracking server
we set in Step4 above (`mlflow.set_tracking_uri("http://localhost:5000")`), which we can do by opening http://localhost:5000 in our browser.

![mlflow tracing dashboard](/mlflow.png)

## Additional Resources
For more configuration and detailed resources for managing your Groq applications with MLflow, see:
- [Getting Started with MLflow](https://mlflow.org/docs/latest/getting-started/index.html)
- [MLflow LLMs Overview](https://mlflow.org/docs/latest/llms/index.html)
- [MLflow Tracing for LLM Observability](https://mlflow.org/docs/latest/llms/tracing/index.html)

---

## Libraries: Library Usage Response (json)

URL: https://console.groq.com/docs/libraries/scripts/library-usage-response.json

The provided content does not appear to be a script or code file that requires cleaning. It seems to be a JSON object representing a chat completion response. As such, there is no code to preserve or clean.


However, if you provide an actual script or code file, I can assist with cleaning it according to the specified requirements.

---

## Libraries: Library Usage (js)

URL: https://console.groq.com/docs/libraries/scripts/library-usage

```javascript
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

export async function main() {
  const chatCompletion = await getGroqChatCompletion();
  // Print the completion returned by the LLM.
  console.log(chatCompletion.choices[0]?.message?.content || "");
}

export async function getGroqChatCompletion() {
  return groq.chat.completions.create({
    messages: [
      {
        role: "user",
        content: "Explain the importance of fast language models",
      },
    ],
    model: "llama-3.3-70b-versatile",
  });
}
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/libraries/scripts/library-usage.py

```python
import os

from groq import Groq

client = Groq(
 # This is the default and can be omitted
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant."
 },
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],
 model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
```

---

## Groq client libraries

URL: https://console.groq.com/docs/libraries

## Groq client libraries

Groq provides both a Python and JavaScript/Typescript client library.

## Groq Python Library

The [Groq Python library](https://pypi.org/project/groq/) provides convenient access to the Groq REST API from any Python3.7+ application. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients.

## Installation

Use the library and your secret key to run:

While you can provide an `api_key` keyword argument, we recommend using [python-dotenv](https://github.com/theskumar/python-dotenv) to add `GROQ_API_KEY="My API Key"` to your `.env` file so that your API Key is not stored in source control.

The following response is generated:


## Groq JavaScript Library

The [Groq JavaScript library](https://www.npmjs.com/package/groq-sdk) provides convenient access to the Groq REST API from server-side TypeScript or JavaScript. The library includes type definitions for all request params and response fields, and offers both synchronous and asynchronous clients.

## Installation

## Usage

Use the library and your secret key to run:


The following response is generated:


## Groq community libraries

Groq encourages our developer community to build on our SDK. If you would like your library added, please fill out this [form](https://docs.google.com/forms/d/e/1FAIpQLSfkg3rPUnmZcTwRAS-MsmVHULMtD2I8LwsKPEasuqSsLlF0yA/viewform?usp=sf_link).

Please note that Groq does not verify the security of these projects. **Use at your own risk.**

### C#

- [jgravelle.GroqAPILibrary](https://github.com/jgravelle/GroqApiLibrary) by [jgravelle](https://github.com/jgravelle)

### Dart/Flutter

- [TAGonSoft.groq-dart](https://github.com/TAGonSoft/groq-dart) by [TAGonSoft](https://github.com/TAGonSoft)

### PHP

- [lucianotonet.groq-php](https://github.com/lucianotonet/groq-php) by [lucianotonet](https://github.com/lucianotonet)

### Ruby

- [drnic.groq-ruby](https://github.com/drnic/groq-ruby) by [drnic](https://github.com/drnic)

---

## Models: Models (tsx)

URL: https://console.groq.com/docs/models/models

## Model Table Documentation

### Table Headers

* MODEL ID
* DEVELOPER
* CONTEXT WINDOW (TOKENS)
* MAX COMPLETION TOKENS
* MAX FILE SIZE
* DETAILS

### Models

#### Production Models

* gemma2-9b-it
	+ Developer: Google
	+ Context Window Tokens: 8,192
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: https://huggingface.co/google/gemma-2-9b-it
* llama-3.3-70b-versatile
	+ Developer: Meta
	+ Context Window Tokens: 128K
	+ Max Output Tokens: 32,768
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama-3.3-70b-versatile
* llama-3.1-8b-instant
	+ Developer: Meta
	+ Context Window Tokens: 128K
	+ Max Output Tokens: 8,192
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama-3.1-8b-instant
* llama-guard-3-8b
	+ Developer: Meta
	+ Context Window Tokens: 8,192
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama-guard-3-8b
* llama3-70b-8192
	+ Developer: Meta
	+ Context Window Tokens: 8,192
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama3-70b-8192
* llama3-8b-8192
	+ Developer: Meta
	+ Context Window Tokens: 8,192
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama3-8b-8192
* whisper-large-v3
	+ Developer: OpenAI
	+ Context Window Tokens: -
	+ Max Output Tokens: -
	+ Max File Size: 25 MB
	+ Model Card Link: https://huggingface.co/openai/whisper-large-v3
* whisper-large-v3-turbo
	+ Developer: OpenAI
	+ Context Window Tokens: -
	+ Max Output Tokens: -
	+ Max File Size: 25 MB
	+ Model Card Link: https://huggingface.co/openai/whisper-large-v3-turbo
* distil-whisper-large-v3-en
	+ Developer: HuggingFace
	+ Context Window Tokens: -
	+ Max Output Tokens: -
	+ Max File Size: 25 MB
	+ Model Card Link: https://huggingface.co/distil-whisper/distil-large-v3

#### Preview Models

* meta-llama/llama-4-scout-17b-16e-instruct
	+ Developer: Meta
	+ Context Window Tokens: 131,072
	+ Max Output Tokens: 8192
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama-4-scout-17b-16e-instruct
* meta-llama/llama-4-maverick-17b-128e-instruct
	+ Developer: Meta
	+ Context Window Tokens: 131,072
	+ Max Output Tokens: 8192
	+ Max File Size: -
	+ Model Card Link: /docs/model/llama-4-maverick-17b-128e-instruct
* playai-tts
	+ Developer: Playht, Inc
	+ Context Window Tokens: 10K
	+ Max Output Tokens: 
	+ Max File Size: -
	+ Model Card Link: /docs/model/playai-tts
* playai-tts-arabic
	+ Developer: Playht, Inc
	+ Context Window Tokens: 10K
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/playai-tts
* qwen-qwq-32b
	+ Developer: Alibaba Cloud
	+ Context Window Tokens: 128K
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/qwen-qwq-32b
* mistral-saba-24b
	+ Developer: Mistral
	+ Context Window Tokens: 32K
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/mistral-saba-24b
* deepseek-r1-distill-llama-70b
	+ Developer: DeepSeek
	+ Context Window Tokens: 128K
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: /docs/model/deepseek-r1-distill-llama-70b
* allam-2-7b
	+ Developer: Saudi Data and AI Authority (SDAIA)
	+ Context Window Tokens: 4,096
	+ Max Output Tokens: -
	+ Max File Size: -
	+ Model Card Link: https://ai.azure.com/explore/models/ALLaM-2-7b-instruct/version/2/registry/azureml

### Preview Systems

* compound-beta
	+ Developer: Groq
	+ Context Window Tokens: 128K
	+ Max Output Tokens: 8192
	+ Max File Size: -
	+ Model Card Link: /docs/agentic-tooling/compound-beta
* compound-beta-mini
	+ Developer: Groq
	+ Context Window Tokens: 128K
	+ Max Output Tokens: 8192
	+ Max File Size: -
	+ Model Card Link: /docs/agentic-tooling/compound-beta-mini

---

## Models: Get Models (js)

URL: https://console.groq.com/docs/models/scripts/get-models

import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

const getModels = async () => {
 return await groq.models.list();
};

getModels().then((models) => {
 // console.log(models);
});

---

## Models: Get Models (py)

URL: https://console.groq.com/docs/models/scripts/get-models.py

import requests
import os

api_key = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"

headers = {
 "Authorization": f"Bearer {api_key}",
 "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

print(response.json())

---

## Supported Models

URL: https://console.groq.com/docs/models

## Supported Models

GroqCloud currently supports the following models:

<br />

### Production Models
**Note:** Production models are intended for use in your production environments. They meet or exceed our high standards for speed, quality, and reliability. Read more [here](/docs/deprecations).

|  |  |
| --- | --- |
 

<br />

### Preview Models
**Note:** Preview models are intended for evaluation purposes only and should not be used in production environments as they may be discontinued at short notice. Read more about deprecations [here](/docs/deprecations).

|  |  |
| --- | --- |
 

<br />

### Preview Systems

Systems are a collection of models and tools that work together to answer a user query. 

**Note:** Preview systems are intended for evaluation purposes only and should not be used in production environments as they may be discontinued at short notice. Read more about deprecations [here](/docs/deprecations).

|  |  |
| --- | --- |
 

<br />


Deprecated models are models that are no longer supported or will no longer be supported in the future. See our deprecation guidelines and deprecated models [here](/docs/deprecations).

<br />

Hosted models are directly accessible through the GroqCloud Models API endpoint using the model IDs mentioned above. You can use the `https://api.groq.com/openai/v1/models` endpoint to return a JSON list of all active models:


### cURL

```shell
./get-models.sh
```

### JavaScript

```js
./get-models.js
```

### Python

```py
./get-models.py
```

---

## Vision: Vision (py)

URL: https://console.groq.com/docs/vision/scripts/vision.py

from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
completion = client.chat.completions.create(
 model="meta-llama/llama-4-scout-17b-16e-instruct",
 messages=[
 {
 "role": "user",
 "content": [
 {
 "type": "text",
 "text": "What's in this image?"
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/LPU-v1-die.jpg"
 }
 }
 ]
 }
 ],
 temperature=1,
 max_completion_tokens=1024,
 top_p=1,
 stream=False,
 stop=None,
)

print(completion.choices[0].message)

---

## Vision: Vision (json)

URL: https://console.groq.com/docs/vision/scripts/vision.json

{
 "messages": [
 {
 "role": "user",
 "content": [
 {
 "type": "text",
 "text": "What's in this image?"
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/LPU-v1-die.jpg"
 }
 }
 ]
 }
 ],
 "model": "meta-llama/llama-4-scout-17b-16e-instruct",
 "temperature":1,
 "max_completion_tokens":1024,
 "top_p":1,
 "stream": false,
 "stop": null
}

---

## Function to encode the image

URL: https://console.groq.com/docs/vision/scripts/local.py

from groq import Groq
import base64
import os

# Function to encode the image
def encode_image(image_path):
 with open(image_path, "rb") as image_file:
 return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "sf.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": [
 {"type": "text", "text": "What's in this image?"},
 {
 "type": "image_url",
 "image_url": {
 "url": f"data:image/jpeg;base64,{base64_image}",
 },
 },
 ],
 }
 ],
 model="meta-llama/llama-4-scout-17b-16e-instruct",
)

print(chat_completion.choices[0].message.content)

---

## Vision: Vision (js)

URL: https://console.groq.com/docs/vision/scripts/vision

import { Groq } from 'groq-sdk';

const groq = new Groq();
async function main() {
 const chatCompletion = await groq.chat.completions.create({
 "messages": [
 {
 "role": "user",
 "content": [
 {
 "type": "text",
 "text": "What's in this image?"
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/LPU-v1-die.jpg"
 }
 }
 ]
 }
 ],
 "model": "meta-llama/llama-4-scout-17b-16e-instruct",
 "temperature":1,
 "max_completion_tokens":1024,
 "top_p":1,
 "stream": false,
 "stop": null
 });

 console.log(chatCompletion.choices[0].message.content);
}

main();

---

## Vision: Jsonmode (py)

URL: https://console.groq.com/docs/vision/scripts/jsonmode.py

from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

completion = client.chat.completions.create(
 model="meta-llama/llama-4-scout-17b-16e-instruct",
 messages=[
 {
 "role": "user",
 "content": [
 {
 "type": "text",
 "text": "List what you observe in this photo in JSON format."
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/SF_From_Marin_Highlands3.jpg"
 }
 }
 ]
 }
 ],
 temperature=1,
 max_completion_tokens=1024,
 top_p=1,
 stream=False,
 response_format={"type": "json_object"},
 stop=None,
)

print(completion.choices[0].message)

---

## Vision: Multiturn (py)

URL: https://console.groq.com/docs/vision/scripts/multiturn.py

from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

completion = client.chat.completions.create(
 model="meta-llama/llama-4-scout-17b-16e-instruct",
 messages=[
 {
 "role": "user",
 "content": [
 {
 "type": "text",
 "text": "What is in this image?"
 },
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/SF_From_Marin_Highlands3.jpg"
 }
 }
 ]
 },
 {
 "role": "user",
 "content": "Tell me more about the area."
 }
 ],
 temperature=1,
 max_completion_tokens=1024,
 top_p=1,
 stream=False,
 stop=None,
)

print(completion.choices[0].message)

---

## Images and Vision

URL: https://console.groq.com/docs/vision

## Images and Vision

Groq API offers fast inference and low latency for multimodal models with vision capabilities for understanding and interpreting visual data from images. By analyzing the content of an image, multimodal models can generate 
human-readable text for providing insights about given visual data. 

### Supported Models

Groq API supports powerful multimodal models that can be easily integrated into your applications to provide fast and accurate image processing for tasks such as visual question answering, caption generation, 
and Optical Character Recognition (OCR).

### How to Use Vision

Use Groq API vision features via:

- **GroqCloud Console Playground**: Use Llama4 Scout or Llama4 Maverick as the model and
upload your image.
- **Groq API Request:** Call the `chat.completions` API endpoint and set the model to `meta-llama/llama-4-scout-17b-16e-instruct` or `meta-llama/llama-4-maverick-17b-128e-instruct`. 
See code examples below.

<br />
#### How to Pass Images from URLs as Input
The following are code examples for passing your image to the model via a URL: 

#### How to Pass Locally Saved Images as Input
To pass locally saved images, we'll need to first encode our image to a base64 format string before passing it as the `image_url` in our API request as follows:

<br />

#### Tool Use with Images
The `meta-llama/llama-4-scout-17b-16e-instruct`, `meta-llama/llama-4-maverick-17b-128e-instruct` models support tool use! The following cURL example defines a `get_current_weather` tool that the model can leverage to answer a user query that contains a question about the 
weather along with an image of a location that the model can infer location (i.e. New York City) from:

<br />

The following is the output from our example above that shows how our model inferred the state as New York from the given image and called our example function:

```python
[
 {
 "id": "call_q0wg",
 "function": {
 "arguments": "{\"location\": \"New York, NY\",\"unit\": \"fahrenheit\"}",
 "name": "get_current_weather"
 },
 "type": "function"
 }
]
```

<br />

#### JSON Mode with Images
The `meta-llama/llama-4-scout-17b-16e-instruct` and `meta-llama/llama-4-maverick-17b-128e-instruct` models support JSON mode! The following Python example queries the model with an image and text (i.e. "Please pull out relevant information as a JSON object.") with `response_format`
set for JSON mode:

<br />

#### Multi-turn Conversations with Images
The `meta-llama/llama-4-scout-17b-16e-instruct` and `meta-llama/llama-4-maverick-17b-128e-instruct` models support multi-turn conversations! The following Python example shows a multi-turn user conversation about an image:

<br />


### Venture Deeper into Vision

#### Use Cases to Explore
Vision models can be used in a wide range of applications. Here are some ideas:

- **Accessibility Applications:** Develop an application that generates audio descriptions for images by using a vision model to generate text descriptions for images, which can then 
be converted to audio with one of our audio endpoints.
- **E-commerce Product Description Generation:** Create an application that generates product descriptions for e-commerce websites.
- **Multilingual Image Analysis:** Create applications that can describe images in multiple languages.
- **Multi-turn Visual Conversations:** Develop interactive applications that allow users to have extended conversations about images.

These are just a few ideas to get you started. The possibilities are endless, and we're excited to see what you create with vision models powered by Groq for low latency and fast inference!

<br />

#### Next Steps
Check out our [Groq API Cookbook](https://github.com/groq/groq-api-cookbook) repository on GitHub (and give us a ⭐) for practical examples and tutorials:
- [Image Moderation](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/image_moderation.ipynb)
- [Multimodal Image Processing (Tool Use, JSON Mode)](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/multimodal-image-processing)
<br />
We're always looking for contributions. If you have any cool tutorials or guides to share, submit a pull request for review to help our open-source community!

---

## Arize + Groq: Open-Source AI Observability

URL: https://console.groq.com/docs/arize

## Arize + Groq: Open-Source AI Observability

<br />

[Arize Phoenix](https://docs.arize.com/phoenix) developed by [Arize AI](https://arize.com/) is an open-source AI observability library that enables comprehensive tracing and monitoring for your AI 
applications. By integrating Arize's observability tools with your Groq-powered applications, you can gain deep insights into your LLM worklflow's performance and behavior with features including:

- **Automatic Tracing:** Capture detailed metrics about LLM calls, including latency, token usage, and exceptions
- **Real-time Monitoring:** Track application performance and identify bottlenecks in production
- **Evaluation Framework:** Utilize pre-built templates to assess LLM performance
- **Prompt Management:** Easily iterate on prompts and test changes against your data


### Python Quick Start (3 minutes to hello world)
####1. Install the required packages:
```bash
pip install arize-phoenix-otel openinference-instrumentation-groq groq
```

####2. Sign up for an [Arize Phoenix account](https://app.phoenix.arize.com).

####2. Configure your Groq and Arize Phoenix API keys:
```bash
export GROQ_API_KEY="your-groq-api-key"
export PHOENIX_API_KEY="your-phoenix-api-key"
```

####3. (Optional) [Create a new project](https://app.phoenix.arize.com/projects) or use the "default" project as your `project_name` below.

####4. Create your first traced Groq application:

In Arize Phoenix, **traces** capture the complete journey of an LLM request through your application, while **spans** represent individual operations within that trace. The instrumentation 
automatically captures important metrics and metadata.

```python
import os
from phoenix.otel import register
from openinference.instrumentation.groq import GroqInstrumentor
from groq import Groq

# Configure environment variables for Phoenix
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

# Configure Phoenix tracer
tracer_provider = register(
 project_name="default",
 endpoint="https://app.phoenix.arize.com/v1/traces",
)

# Initialize Groq instrumentation
GroqInstrumentor().instrument(tracer_provider=tracer_provider)

# Create Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Make an instrumented LLM call
chat_completion = client.chat.completions.create(
 messages=[{
 "role": "user",
 "content": "Explain the importance of AI observability"
 }],
 model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
```

Running the above code will create an automatically instrumented Groq application! The traces will be available in your Phoenix dashboard within the `default` project, showing 
detailed information about:
- **Application Latency:** Identify slow components and bottlenecks
- **Token Usage:** Track token consumption across different operations
- **Runtime Exceptions:** Capture and analyze errors and rate limits
- **LLM Parameters:** Monitor temperature, system prompts, and other settings
- **Response Analysis:** Examine LLM outputs and their characteristics

**Challenge**: Update an existing Groq-powered application you've built to add Arize Phoenix tracing!


For more detailed documentation and resources on building observable LLM applications with Groq and Arize, see:
- [Official Documentation: Groq Integration Guide](https://docs.arize.com/phoenix/tracing/integrations-tracing/groq)
- [Blog: Tracing with Groq](https://arize.com/blog/tracing-groq/)
- [Webinar: Tracing and Evaluating LLM Apps with Groq and Arize Phoenix](https://youtu.be/KjtrILr6JZI?si=iX8Udo-EYsK2JOvF)

---

## Text To Speech: English (py)

URL: https://console.groq.com/docs/text-to-speech/scripts/english.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

speech_file_path = "speech.wav" 
model = "playai-tts"
voice = "Fritz-PlayAI"
text = "I love building and shipping new features for our users!"
response_format = "wav"

response = client.audio.speech.create(
 model=model,
 voice=voice,
 input=text,
 response_format=response_format
)

response.write_to_file(speech_file_path)
```

---

## Text To Speech: English (js)

URL: https://console.groq.com/docs/text-to-speech/scripts/english

import fs from "fs";
import path from "path";
import Groq from 'groq-sdk';

const groq = new Groq({
 apiKey: process.env.GROQ_API_KEY
});

const speechFilePath = "speech.wav";
const model = "playai-tts";
const voice = "Fritz-PlayAI";
const text = "I love building and shipping new features for our users!";
const responseFormat = "wav";

async function main() {
 const response = await groq.audio.speech.create({
 model: model,
 voice: voice,
 input: text,
 response_format: responseFormat
 });
  
 const buffer = Buffer.from(await response.arrayBuffer());
 await fs.promises.writeFile(speechFilePath, buffer);
}

main();

---

## Text to Speech

URL: https://console.groq.com/docs/text-to-speech

## Text to Speech
Learn how to instantly generate lifelike audio from text.

## Overview
The Groq API speech endpoint provides fast text-to-speech (TTS), enabling you to convert text to spoken audio in seconds with our available TTS models.

With support for 23 voices, 19 in English and 4 in Arabic, you can instantly create life-like audio content for customer support agents, characters for game development, and more.

## API Endpoint
| Endpoint | Usage | API Endpoint |
|----------|--------------------------------|-------------------------------------------------------------|
| Speech | Convert text to audio | `https://api.groq.com/openai/v1/audio/speech` |

## Supported Models

| Model ID | Model Card | Supported Language(s) | Description |
|-------------------|--------------|------------------------|-----------------------------------------------------------------|
| `playai-tts` | [Card](/docs/model/playai-tts) | English | High-quality TTS model for English speech generation. |
| `playai-tts-arabic` | [Card](/docs/model/playai-tts) | Arabic | High-quality TTS model for Arabic speech generation. |

## Working with Speech

### Quick Start
The speech endpoint takes four key inputs:
- **model:** `playai-tts` or `playai-tts-arabic`
- **input:** the text to generate audio from
- **voice:** the desired voice for output
- **response format:** defaults to `"wav"`


## API Usage Examples

### Parameters

| Parameter | Type | Required | Value | Description |
|-----------|------|----------|-------------|---------------|
| `model` | string | Yes | `playai-tts`<br />`playai-tts-arabic` | Model ID to use for TTS. |
| `input` | string | Yes | - | User input text to be converted to speech. Maximum length is 10K characters. |
| `voice` | string | Yes | See available [English](#available-english-voices) and [Arabic](#available-arabic-voices) voices. | The voice to use for audio generation. There are currently 26 English options for `playai-tts` and 4 Arabic options for `playai-tts-arabic`. |
| `response_format` | string | Optional | `"wav"` | Format of the response audio file. Defaults to currently supported `"wav"`. |



### Available English Voices

The `playai-tts` model currently supports 19 English voices that you can pass into the `voice` parameter (`Arista-PlayAI`, `Atlas-PlayAI`, `Basil-PlayAI`, `Briggs-PlayAI`, `Calum-PlayAI`, 
`Celeste-PlayAI`, `Cheyenne-PlayAI`, `Chip-PlayAI`, `Cillian-PlayAI`, `Deedee-PlayAI`, `Fritz-PlayAI`, `Gail-PlayAI`, 
`Indigo-PlayAI`, `Mamaw-PlayAI`, `Mason-PlayAI`, `Mikail-PlayAI`, `Mitch-PlayAI`, `Quinn-PlayAI`, `Thunder-PlayAI`).

Experiment to find the voice you need for your application:



### Available Arabic Voices

The `playai-tts-arabic` model currently supports 4 Arabic voices that you can pass into the `voice` parameter (`Ahmad-PlayAI`, `Amira-PlayAI`, `Khalid-PlayAI`, `Nasser-PlayAI`).

Experiment to find the voice you need for your application:

---

## Reasoning: R1 (py)

URL: https://console.groq.com/docs/reasoning/scripts/r1.py

from groq import Groq

client = Groq()
completion = client.chat.completions.create(
 model="deepseek-r1-distill-llama-70b",
 messages=[
 {
 "role": "user",
 "content": "How many r's are in the word strawberry?"
 }
 ],
 temperature=0.6,
 max_completion_tokens=1024,
 top_p=0.95,
 stream=True,
 reasoning_format="raw"
)

for chunk in completion:
 print(chunk.choices[0].delta.content or "", end="")

---

## Reasoning: R1 (js)

URL: https://console.groq.com/docs/reasoning/scripts/r1

import Groq from 'groq-sdk';

const client = new Groq();
const completion = await client.chat.completions.create({
  model: "deepseek-r1-distill-llama-70b",
  messages: [
    {
      role: "user",
      content: "How many r's are in the word strawberry?"
    }
  ],
  temperature: 0.6,
  max_completion_tokens: 1024,
  top_p: 0.95,
  stream: true,
  reasoning_format: "raw"
});

for await (const chunk of completion) {
  process.stdout.write(chunk.choices[0].delta.content || "");
}

---

## Reasoning

URL: https://console.groq.com/docs/reasoning

## Reasoning 
Reasoning models excel at complex problem-solving tasks that require step-by-step analysis, logical deduction, and structured thinking and solution validation. With Groq inference speed, these types of models 
can deliver instant reasoning capabilities critical for real-time applications. 

### Why Speed Matters for Reasoning
Reasoning models are capable of complex decision making with explicit reasoning chains that are part of the token output and used for decision-making, which make low-latency and fast inference essential. 
Complex problems often require multiple chains of reasoning tokens where each step build on previous results. Low latency compounds benefits across reasoning chains and shaves off minutes of reasoning to a response in seconds. 

## Supported Model

| Model ID | Model |
|---------------------------------|--------------------------------|
| qwen-qwq-32b | Qwen QwQ32B
| deepseek-r1-distill-llama-70b | DeepSeek R1 Distil Llama70B |

## Reasoning Format
Groq API supports explicit reasoning formats through the `reasoning_format` parameter, giving you fine-grained control over how the model's 
reasoning process is presented. This is particularly valuable for valid JSON outputs, debugging, and understanding the model's decision-making process.

**Note:** The format defaults to `raw` or `parsed` when JSON mode or tool use are enabled as those modes do not support `raw`. If reasoning is 
explicitly set to `raw` with JSON mode or tool use enabled, we will return a400 error.

### Options for Reasoning Format
| `reasoning_format` Options | Description |
|------------------|------------------------------------------------------------| 
| `parsed` | Separates reasoning into a dedicated field while keeping the response concise. |
| `raw` | Includes reasoning within think tags in the content. |
| `hidden` | Returns only the final answer. | 

## Quick Start

## Quick Start with Tool use
```bash
curl https://api.groq.com/openai/v1/chat/completions -s \
 -H "authorization: bearer $GROQ_API_KEY" \
 -d '{
 "model": "deepseek-r1-distill-llama-70b",
 "messages": [
 {
 "role": "user",
 "content": "What is the weather like in Paris today?"
 }
 ],
 "tools": [
 {
 "type": "function",
 "function": {
 "name": "get_weather",
 "description": "Get current temperature for a given location.",
 "parameters": {
 "type": "object",
 "properties": {
 "location": {
 "type": "string",
 "description": "City and country e.g. Bogotá, Colombia"
 }
 },
 "required": [
 "location"
 ],
 "additionalProperties": false
 },
 "strict": true
 }
 }
 ]}'
```

## Recommended Configuration Parameters 

| Parameter | Default | Range | Description |
|-----------|---------|--------|-------------|
| `messages` | - | - | Array of message objects. Important: Avoid system prompts - include all instructions in the user message! |
| `temperature` |0.6 |0.0 -2.0 | Controls randomness in responses. Lower values make responses more deterministic. Recommended range:0.5-0.7 to prevent repetitions or incoherent outputs |
| `max_completion_tokens` |1024 | - | Maximum length of model's response. Default may be too low for complex reasoning - consider increasing for detailed step-by-step solutions |
| `top_p` |0.95 |0.0 -1.0 | Controls diversity of token selection |
| `stream` | false | boolean | Enables response streaming. Recommended for interactive reasoning tasks |
| `stop` | null | string/array | Custom stop sequences |
| `seed` | null | integer | Set for reproducible results. Important for benchmarking - run multiple tests with different seeds |
| `response_format` | `{type: "text"}` | `{type: "json_object"}` or `{type: "text"}` | Set to `json_object` type for structured output. |
| `reasoning_format` | `raw` | `"parsed"`, `"raw"`, `"hidden"` | Controls how model reasoning is presented in the response. Must be set to either `parsed` or `hidden` when using tool calls or JSON mode. |


## Optimizing Performance 

### Temperature and Token Management
The model performs best with temperature settings between0.5-0.7, with lower values (closer to0.5) producing more consistent mathematical proofs and higher values allowing for more creative problem-solving approaches. Monitor and adjust your token usage based on the complexity of your reasoning tasks - while the default max_completion_tokens is1024, complex proofs may require higher limits.

### Prompt Engineering
To ensure accurate, step-by-step reasoning while maintaining high performance:
- DeepSeek-R1 works best when all instructions are included directly in user messages rather than system prompts. 
- Structure your prompts to request explicit validation steps and intermediate calculations. 
- Avoid few-shot prompting and go for zero-shot prompting only.

---

## Quickstart: Performing Chat Completion (js)

URL: https://console.groq.com/docs/quickstart/scripts/performing-chat-completion

```javascript
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

export async function main() {
  const chatCompletion = await getGroqChatCompletion();
  // Print the completion returned by the LLM.
  console.log(chatCompletion.choices[0]?.message?.content || "");
}

export async function getGroqChatCompletion() {
  return groq.chat.completions.create({
    messages: [
      {
        role: "user",
        content: "Explain the importance of fast language models",
      },
    ],
    model: "llama-3.3-70b-versatile",
  });
}
```

---

## Quickstart: Performing Chat Completion (json)

URL: https://console.groq.com/docs/quickstart/scripts/performing-chat-completion.json

{
 "messages": [
 {
 "role": "user",
 "content": "Explain the importance of fast language models"
 }
 ],
 "model": "llama-3.3-70b-versatile"
}

---

## Quickstart: Performing Chat Completion (py)

URL: https://console.groq.com/docs/quickstart/scripts/performing-chat-completion.py

import os

from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],
 model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)

---

## Quickstart

URL: https://console.groq.com/docs/quickstart

## Quickstart

Get up and running with the Groq API in a few minutes.

### Create an API Key

Please visit [here](/keys) to create an API Key.

### Set up your API Key (recommended)

Configure your API key as an environment variable. This approach streamlines your API usage by eliminating the need to include your API key in each request. Moreover, it enhances security by minimizing the risk of inadvertently including your API key in your codebase.

#### In your terminal of choice:

```shell
export GROQ_API_KEY=<your-api-key-here>
```

### Requesting your first chat completion

### Execute this curl command in the terminal of your choice:

```shell
# contents of performing-chat-completion.sh
```

#### Install the Groq JavaScript library:

```shell
# contents of install-groq-npm.sh
```

#### Performing a Chat Completion:

```js
// contents of performing-chat-completion.js
```

#### Install the Groq Python library:

```shell
# contents of install-groq-pip.sh
```

#### Performing a Chat Completion:

```py
# contents of performing-chat-completion.py
```

#### Pass the following as the request body:

```json
// contents of performing-chat-completion.json
```

Now that you have successfully received a chat completion, you can try out the other endpoints in the API.

### Next Steps

- Check out the [Playground](/playground) to try out the Groq API in your browser
- Join our GroqCloud developer community on [Discord](https://discord.gg/groq)
- Add a how-to on your project to the [Groq API Cookbook](https://github.com/groq/groq-api-cookbook)

---

## Key Technical Specifications

URL: https://console.groq.com/docs/agentic-tooling/compound-beta

### Key Technical Specifications

Compound-beta leverages Llama4 Scout for core reasoning along with Llama3.3 70B to help with routing and tool use.

 
### Key Technical Specifications

* **Model Architecture**: 
 Compound-beta leverages [Llama4 Scout](https://console.groq.com/docs/model/llama-4-scout-17b-16e-instruct) for core reasoning along with [Llama3.3 70B](https://console.groq.com/docs/model/llama-3.3-70b-versatile) to help with routing and tool use.

* **Performance Metrics**: 
 Groq developed a new evaluation benchmark for measuring search capabilities called [RealtimeEval](https://github.com/groq/realtime-eval). This benchmark is designed to evaluate tool-using systems on current events and live data. On the benchmark, Compound Beta outperformed GPT-4o-search-preview and GPT-4o-mini-search-preview significantly.

### Learn More About Agentic Tooling
Discover how to build powerful applications with real-time web search and code execution

### Quick Start
Experience the capabilities of `compound-beta` on Groq:  

### Model Technical Details

* **contextWindow**: 128K
* **maxOutputTokens**: 8,192
* **maxFileSize**: N/A
* **tokenSpeed**: 350 tokens per second
* **inputPrice**: Varies. Pricing is based on input tokens to underlying models (while in preview)
* **outputPrice**: Varies. Pricing is based on output tokens from underlying models (while in preview)
* **toolUse**: false
* **agenticTools**: true
* **jsonMode**: true
* **imageSupport**: false

### Model Use Cases

* **Realtime Web Search**: 
 Automatically access up-to-date information from the web using the built-in web search tool powered by [Tavily](https://tavily.com/).
* **Code Execution**: 
 Execute Python code automatically using the code execution tool powered by [E2B](https://e2b.dev/).
* **Code Generation and Technical Tasks**: 
 Create AI tools for code generation, debugging, and technical problem-solving with high-quality multilingual support.

### Model Best Practices

* Use system prompts to improve steerability and reduce false refusals. Compound-beta is designed to be highly steerable with appropriate system prompts.
* Consider implementing system-level protections like Llama Guard for input filtering and response validation.
* Deploy with appropriate safeguards when working in specialized domains or with critical content.
* Compound-beta should not be used by customers for processing protected health information. It is not a HIPAA Covered Cloud Service under Groq's Business Associate Addendum for customers at this time.

### Code Examples 
Experience the capabilities of `compound-beta` on Groq

---

## Agentic Tooling: Natural Language.doc (ts)

URL: https://console.groq.com/docs/agentic-tooling/scripts/natural-language.doc

```javascript
import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
  // Example1: Calculation
  const computationQuery = "Calculate the monthly payment for a $30,000 loan over5 years at6% annual interest.";

  // Example2: Simple code execution
  const codeQuery = "What is the output of this Python code snippet: `data = {'a':1, 'b':2}; print(data.keys())`";

  // Choose one query to run
  const selectedQuery = computationQuery;

  const completion = await groq.chat.completions.create({
    messages: [
      {
        role: "system",
        content: "You are a helpful assistant capable of performing calculations and executing simple code when asked.",
      },
      {
        role: "user",
        content: selectedQuery,
      }
    ],
    // Use the compound model
    model: "compound-beta-mini",
  });

  console.log(`Query: ${selectedQuery}`);
  console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);
}

main();
```

---

## Agentic Tooling: Fact Checker (js)

URL: https://console.groq.com/docs/agentic-tooling/scripts/fact-checker

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 const user_query = "What were the main highlights from the latest Apple keynote event?"
 // Or: "What's the current weather in San Francisco?"
 // Or: "Summarize the latest developments in fusion energy research this week."

 const completion = await groq.chat.completions.create({
 messages: [
 {
 role: "user",
 content: user_query,
 },
 ],
 // The *only* change needed: Specify the compound model!
 model: "compound-beta",
 });

 console.log(`Query: ${user_query}`);
 console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);

 // You might also inspect chat_completion.choices[0].message.executed_tools
 // if you want to see if/which tool was used, though it's not necessary.
}

main();

---

## Ensure your GROQ_API_KEY is set as an environment variable

URL: https://console.groq.com/docs/agentic-tooling/scripts/fact-checker.py

import os
from groq import Groq

# Ensure your GROQ_API_KEY is set as an environment variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

user_query = "What were the main highlights from the latest Apple keynote event?"
# Or: "What's the current weather in San Francisco?"
# Or: "Summarize the latest developments in fusion energy research this week."

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": user_query,
 }
 ],
 # The *only* change needed: Specify the compound model!
 model="compound-beta",
)

print(f"Query: {user_query}")
print(f"Compound Beta Response:\n{chat_completion.choices[0].message.content}")

# You might also inspect chat_completion.choices[0].message.executed_tools
# if you want to see if/which tool was used, though it's not necessary.

---

## Agentic Tooling: Code Debugger.doc (ts)

URL: https://console.groq.com/docs/agentic-tooling/scripts/code-debugger.doc

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 // Example1: Error Explanation (might trigger search)
 const debugQuerySearch = "I'm getting a 'Kubernetes CrashLoopBackOff' error on my pod. What are the common causes based on recent discussions?";

 // Example2: Code Check (might trigger code execution)
 const debugQueryExec = "Will this Python code raise an error? `import numpy as np; a = np.array([1,2]); b = np.array([3,4,5]); print(a+b)`";

 // Choose one query to run
 const selectedQuery = debugQueryExec;

 const completion = await groq.chat.completions.create({
 messages: [
 {
 role: "system",
 content: "You are a helpful coding assistant. You can explain errors, potentially searching for recent information, or check simple code snippets by executing them.",
 },
 {
 role: "user",
 content: selectedQuery,
 }
 ],
 // Use the compound model
 model: "compound-beta-mini",
 });

 console.log(`Query: ${selectedQuery}`);
 console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);
}

main();

---

## Example 1: Error Explanation (might trigger search)

URL: https://console.groq.com/docs/agentic-tooling/scripts/code-debugger.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Example1: Error Explanation (might trigger search)
debug_query_search = "I'm getting a 'Kubernetes CrashLoopBackOff' error on my pod. What are the common causes based on recent discussions?"

# Example2: Code Check (might trigger code execution)
debug_query_exec = "Will this Python code raise an error? `import numpy as np; a = np.array([1,2]); b = np.array([3,4,5]); print(a+b)`"

# Choose one query to run
selected_query = debug_query_exec

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful coding assistant. You can explain errors, potentially searching for recent information, or check simple code snippets by executing them.",
 },
 {
 "role": "user",
 "content": selected_query,
 }
 ],
 # Use the compound model
 model="compound-beta-mini",
)

print(f"Query: {selected_query}")
print(f"Compound Beta Response:\n{chat_completion.choices[0].message.content}")
```

---

## Agentic Tooling: Usage.doc (ts)

URL: https://console.groq.com/docs/agentic-tooling/scripts/usage.doc

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
  const completion = await groq.chat.completions.create({
    messages: [
      {
        role: "user",
        content: "What is the current weather in Tokyo?",
      },
    ],
    // Change model to compound-beta to use agentic tooling
    // model: "llama-3.3-70b-versatile",
    model: "compound-beta",
  });

  console.log(completion.choices[0]?.message?.content || "");
  // Print all tool calls
  // console.log(completion.choices[0]?.message?.executed_tools || "");
}

main();

---

## Example 1: Calculation

URL: https://console.groq.com/docs/agentic-tooling/scripts/natural-language.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Example1: Calculation
computation_query = "Calculate the monthly payment for a $30,000 loan over5 years at6% annual interest."

# Example2: Simple code execution
code_query = "What is the output of this Python code snippet: `data = {'a':1, 'b':2}; print(data.keys())`"

# Choose one query to run
selected_query = computation_query

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant capable of performing calculations and executing simple code when asked.",
 },
 {
 "role": "user",
 "content": selected_query,
 }
 ],
 # Use the compound model
 model="compound-beta-mini",
)

print(f"Query: {selected_query}")
print(f"Compound Beta Response:\n{chat_completion.choices[0].message.content}")
```

---

## Agentic Tooling: Usage (js)

URL: https://console.groq.com/docs/agentic-tooling/scripts/usage

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
  const completion = await groq.chat.completions.create({
    messages: [
      {
        role: "user",
        content: "What is the current weather in Tokyo?",
      },
    ],
    // Change model to compound-beta to use agentic tooling
    // model: "llama-3.3-70b-versatile",
    model: "compound-beta",
  });

  console.log(completion.choices[0]?.message?.content || "");
  // Print all tool calls
  // console.log(completion.choices[0]?.message?.executed_tools || "");
}

main();

---

## Agentic Tooling: Code Debugger (js)

URL: https://console.groq.com/docs/agentic-tooling/scripts/code-debugger

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 // Example1: Error Explanation (might trigger search)
 const debugQuerySearch = "I'm getting a 'Kubernetes CrashLoopBackOff' error on my pod. What are the common causes based on recent discussions?";

 // Example2: Code Check (might trigger code execution)
 const debugQueryExec = "Will this Python code raise an error? `import numpy as np; a = np.array([1,2]); b = np.array([3,4,5]); print(a+b)`";

 // Choose one query to run
 const selectedQuery = debugQueryExec;

 const completion = await groq.chat.completions.create({
 messages: [
 {
 role: "system",
 content: "You are a helpful coding assistant. You can explain errors, potentially searching for recent information, or check simple code snippets by executing them.",
 },
 {
 role: "user",
 content: selectedQuery,
 }
 ],
 // Use the compound model
 model: "compound-beta-mini",
 });

 console.log(`Query: ${selectedQuery}`);
 console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);
}

main();

---

## Change model to compound-beta to use agentic tooling

URL: https://console.groq.com/docs/agentic-tooling/scripts/usage.py

from groq import Groq

client = Groq()

completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": "What is the current weather in Tokyo?",
 }
 ],
 # Change model to compound-beta to use agentic tooling
 # model: "llama-3.3-70b-versatile",
 model="compound-beta",
)

print(completion.choices[0].message.content)
# Print all tool calls
# print(completion.choices[0].message.executed_tools)

---

## Agentic Tooling: Fact Checker.doc (ts)

URL: https://console.groq.com/docs/agentic-tooling/scripts/fact-checker.doc

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 const user_query = "What were the main highlights from the latest Apple keynote event?"
 // Or: "What's the current weather in San Francisco?"
 // Or: "Summarize the latest developments in fusion energy research this week."

 const completion = await groq.chat.completions.create({
 messages: [
 {
 role: "user",
 content: user_query,
 },
 ],
 // The *only* change needed: Specify the compound model!
 model: "compound-beta",
 });

 console.log(`Query: ${user_query}`);
 console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);

 // You might also inspect chat_completion.choices[0].message.executed_tools
 // if you want to see if/which tool was used, though it's not necessary.
}

main();

---

## Agentic Tooling: Natural Language (js)

URL: https://console.groq.com/docs/agentic-tooling/scripts/natural-language

import Groq from "groq-sdk";

const groq = new Groq();

export async function main() {
 // Example1: Calculation
 const computationQuery = "Calculate the monthly payment for a $30,000 loan over5 years at6% annual interest.";

 // Example2: Simple code execution
 const codeQuery = "What is the output of this Python code snippet: `data = {'a':1, 'b':2}; print(data.keys())`";

 // Choose one query to run
 const selectedQuery = computationQuery;

 const completion = await groq.chat.completions.create({
 messages: [
 {
 role: "system",
 content: "You are a helpful assistant capable of performing calculations and executing simple code when asked.",
 },
 {
 role: "user",
 content: selectedQuery,
 }
 ],
 // Use the compound model
 model: "compound-beta-mini",
 });

 console.log(`Query: ${selectedQuery}`);
 console.log(`Compound Beta Response:\n${completion.choices[0]?.message?.content || ""}`);
}

main();

---

## Agentic Tooling

URL: https://console.groq.com/docs/agentic-tooling

## Agentic Tooling

While LLMs excel at generating text, [`compound-beta`](/docs/agentic-tooling/compound-beta) takes the next step. 
It's an advanced AI system that is designed to solve problems by taking action and intelligently uses external tools - starting with web search and code execution - alongside the powerful Llama4 models and Llama3.370b model.
This allows it access to real-time information and interaction with external environments, providing more accurate, up-to-date, and capable responses than an LLM alone.

### Available Agentic Tools

There are two agentic tool systems available:
 - [`compound-beta`](/docs/agentic-tooling/compound-beta): supports multiple tool calls per request. This system is great for use cases that require multiple web searches or code executions per request.
 - [`compound-beta-mini`](/docs/agentic-tooling/compound-beta-mini): supports a single tool call per request. This system is great for use cases that require a single web search or code execution per request. `compound-beta-mini` has an average of 3x lower latency than `compound-beta`.

 

Both systems support the following tools:

- Web Search via [Tavily](https://tavily.com/)
- Code Execution via [E2B](https://e2b.dev/) (only Python is currently supported)

<br/>

Custom [user-provided tools](/docs/tool-use) are not supported at this time.

### Usage

To use agentic tools, change the `model` parameter to either `compound-beta` or `compound-beta-mini`:

And that's it!

<br/>

When the API is called, it will intelligently decide when to use search or code execution to best answer the user's query.
These tool calls are performed on the server side, so no additional setup is required on your part to use agentic tooling.

<br/>

In the above example, the API will use its build in web search tool to find the current weather in Tokyo.
If you didn't use agentic tooling, you might have needed to add your own custom tools to make API requests to a weather service, then perform multiple API calls to Groq to get a final result.
Instead, with agentic tooling, you can get a final result with a single API call.


## Use Cases

Compound-beta excels at a wide range of use cases, particularly when real-time information is required.

### Real-time Fact Checker and News Agent

Your application needs to answer questions or provide information that requires up-to-the-minute knowledge, such as:
- Latest news
- Current stock prices
- Recent events
- Weather updates

Building and maintaining your own web scraping or search API integration is complex and time-consuming.

#### Solution with Compound Beta
Simply send the user's query to `compound-beta`. If the query requires current information beyond its training data, it will automatically trigger its built-in web search tool (powered by Tavily) to fetch relevant, live data before formulating the answer.

#### Why It's Great
- Get access to real-time information instantly without writing any extra code for search integration
- Leverage Groq's speed for a real-time, responsive experience

#### Code Example


### Natural Language Calculator and Code Extractor

You want users to perform calculations, run simple data manipulations, or execute small code snippets using natural language commands within your application, without building a dedicated parser or execution environment.

#### Solution with Compound Beta

Frame the user's request as a task involving computation or code. `compound-beta-mini` can recognize these requests and use its secure code execution tool to compute the result.

#### Why It's Great
 - Effortlessly add computational capabilities
 - Users can ask things like:
 - "What's15% of $540?"
 - "Calculate the standard deviation of [10,12,11,15,13]"
 - "Run this python code: print('Hello from Compound Beta!')"

#### Code Example


### Code Debugging Assistant

Developers often need quick help understanding error messages or testing small code fixes. Searching documentation or running snippets requires switching contexts.

#### Solution with Compound Beta
Users can paste an error message and ask for explanations or potential causes. Compound Beta Mini might use web search to find recent discussions or documentation about that specific error. Alternatively, users can provide a code snippet and ask "What's wrong with this code?" or "Will this Python code run: ...?". It can use code execution to test simple, self-contained snippets.

#### Why It's Great
- Provides a unified interface for getting code help
- Potentially draws on live web data for new errors
- Executes code directly for validation
- Speeds up the debugging process

**Note**: `compound-beta-mini` uses one tool per turn, so it might search OR execute, not both simultaneously in one response.

---

## Key Technical Specifications

URL: https://console.groq.com/docs/agentic-tooling/compound-beta-mini

### Key Technical Specifications

Compound-beta-mini leverages Llama4 Scout for core reasoning along with Llama3.3 70B to help with routing and tool use. Unlike compound-beta, it can only use one tool per request, but has an average of 3x lower latency.

 
### Key Technical Specifications

* **Model Architecture**: 
Compound-beta-mini leverages [Llama4 Scout](/docs/model/llama-4-scout-17b-16e-instruct) for core reasoning along with [Llama3.3 70B](/docs/model/llama-3.3-70b-versatile) to help with routing and tool use. Unlike [compound-beta](/docs/agentic-tooling/compound-beta), it can only use one tool per request, but has an average of 3x lower latency.

* **Performance Metrics**: 
Groq developed a new evaluation benchmark for measuring search capabilities called [RealtimeEval](https://github.com/groq/realtime-eval). This benchmark is designed to evaluate tool-using systems on current events and live data. On the benchmark, Compound Beta Mini outperformed GPT-4o-search-preview and GPT-4o-mini-search-preview significantly.

### Quick Start
Experience the capabilities of `compound-beta-mini` on Groq:  

### Key Use Cases

* **Realtime Web Search**: 
Automatically access up-to-date information from the web using the built-in web search tool powered by [Tavily](https://tavily.com/).

* **Code Execution**: 
Execute Python code automatically using the code execution tool powered by [E2B](https://e2b.dev/).

* **Code Generation and Technical Tasks**: 
Create AI tools for code generation, debugging, and technical problem-solving with high-quality multilingual support.

### Best Practices

* Use system prompts to improve steerability and reduce false refusals. Compound-beta-mini is designed to be highly steerable with appropriate system prompts.
* Consider implementing system-level protections like Llama Guard for input filtering and response validation.
* Deploy with appropriate safeguards when working in specialized domains or with critical content.
* Compound-beta-mini should not be used by customers for processing protected health information. It is not a HIPAA Covered Cloud Service under Groq's Business Associate Addendum for customers at this time.

### Technical Details

* **Context Window**: 128K
* **Max Output Tokens**: 8,192
* **Max File Size**: N/A
* **Token Speed**: 275 tokens per second
* **Input Price**: Varies. Pricing is based on input tokens to underlying models (while in preview)
* **Output Price**: Varies. Pricing is based on output tokens from underlying models (while in preview)
* **Tool Use**: false
* **Agentic Tools**: true
* **JSON Mode**: true
* **Image Support**: false

---

## Integrations: Button Group (tsx)

URL: https://console.groq.com/docs/integrations/button-group

## Button Group

The Button Group component is used to display a collection of buttons in a grid layout. It accepts an array of button objects, each containing properties such as title, description, href, iconSrc, iconDarkSrc, and color.

### Button Group Properties

* **buttons**: An array of IntegrationButton objects.

### Integration Button Properties

* **title**: The title of the button.
* **description**: A brief description of the button.
* **href**: The link URL of the button.
* **iconSrc**: The source URL of the button's icon.
* **iconDarkSrc**: The source URL of the button's dark icon (optional).
* **color**: The color of the button (optional).

---

## Integrations: Integration Buttons (ts)

URL: https://console.groq.com/docs/integrations/integration-buttons

import type { IntegrationButton } from "./button-group";

type IntegrationGroup =
  | "ai-agent-frameworks"
  | "llm-app-development"
  | "observability"
  | "llm-code-execution"
  | "ui-and-ux"
  | "tool-management"
  | "real-time-voice";

export const integrationButtons: Record<IntegrationGroup, IntegrationButton[]> = {
  "ai-agent-frameworks": [
    {
      title: "Agno",
      description:
        "Agno is a lightweight library for building Agents with memory, knowledge, tools and reasoning.",
      href: "/docs/agno",
      iconSrc: "/integrations/agno_black.svg",
      iconDarkSrc: "/integrations/agno_white.svg",
      color: "gray",
    },
    {
      title: "AutoGen",
      description:
        "AutoGen is a framework for building conversational AI systems that can operate autonomously or collaborate with humans and other agents.",
      href: "/docs/autogen",
      iconSrc: "/integrations/autogen.svg",
      color: "gray",
    },
    {
      title: "CrewAI",
      description:
        "CrewAI is a framework for orchestrating role-playing AI agents that work together to accomplish complex tasks.",
      href: "/docs/crewai",
      iconSrc: "/integrations/crewai.png",
      color: "gray",
    },
    {
      title: "xRx",
      description:
        "xRx is a reactive AI agent framework for building reliable and observable LLM agents with real-time feedback.",
      href: "/docs/xrx",
      iconSrc: "/integrations/xrx.png",
      color: "gray",
    },
  ],
  "llm-app-development": [
    {
      title: "LangChain",
      description:
        "LangChain is a framework for developing applications powered by language models through composability.",
      href: "/docs/langchain",
      iconSrc: "/integrations/langchain_black.png",
      iconDarkSrc: "/integrations/langchain_white.png",
      color: "gray",
    },
    {
      title: "LlamaIndex",
      description:
        "LlamaIndex is a data framework for building LLM applications with context augmentation over external data.",
      href: "/docs/llama-index",
      iconSrc: "/integrations/llamaindex_black.png",
      iconDarkSrc: "/integrations/llamaindex_white.png",
      color: "gray",
    },
    {
      title: "LiteLLM",
      description:
        "LiteLLM is a library that standardizes LLM API calls and provides robust tracking, fallbacks, and observability for LLM applications.",
      href: "/docs/litellm",
      iconSrc: "/integrations/litellm.png",
      color: "gray",
    },
    {
      title: "Vercel AI SDK",
      description:
        "Vercel AI SDK is a typescript library for building AI-powered applications in modern frontend frameworks.",
      href: "/docs/ai-sdk",
      iconSrc: "/vercel-integration.png",
      color: "gray",
    },
  ],
  observability: [
    {
      title: "Arize",
      description:
        "Arize is an observability platform for monitoring, troubleshooting, and explaining LLM applications.",
      href: "/docs/arize",
      iconSrc: "/integrations/arize_phoenix.png",
      color: "gray",
    },
    {
      title: "MLflow",
      description:
        "MLflow is an open-source platform for managing the end-to-end machine learning lifecycle, including experiment tracking and model deployment.",
      href: "/docs/mlflow",
      iconSrc: "/integrations/mlflow-white.svg",
      iconDarkSrc: "/integrations/mlflow-black.svg",
      color: "gray",
    },
  ],
  "llm-code-execution": [
    {
      title: "E2B",
      description:
        "E2B provides secure sandboxed environments for LLMs to execute code and use tools in a controlled manner.",
      href: "/docs/e2b",
      iconSrc: "/integrations/e2b_black.png",
      iconDarkSrc: "/integrations/e2b_white.png",
      color: "gray",
    },
  ],
  "ui-and-ux": [
    {
      title: "FlutterFlow",
      description:
        "FlutterFlow is a visual development platform for building high-quality, custom, cross-platform apps with AI capabilities.",
      href: "/docs/flutterflow",
      iconSrc: "/integrations/flutterflow_black.png",
      iconDarkSrc: "/integrations/flutterflow_white.png",
      color: "gray",
    },
    {
      title: "Gradio",
      description:
        "Gradio is a Python library for quickly creating customizable UI components for machine learning models and LLM applications.",
      href: "/docs/gradio",
      iconSrc: "/integrations/gradio.svg",
      color: "gray",
    },
  ],
  "tool-management": [
    {
      title: "Composio",
      description:
        "Composio is a platform for managing and integrating tools with LLMs and AI agents for seamless interaction with external applications.",
      href: "/docs/composio",
      iconSrc: "/integrations/composio_black.png",
      iconDarkSrc: "/integrations/composio_white.png",
      color: "gray",
    },
    {
      title: "JigsawStack",
      description:
        "JigsawStack is a powerful AI SDK that integrates into any backend, automating tasks using LLMs with features like Mixture-of-Agents approach.",
      href: "/docs/jigsawstack",
      iconSrc: "/integrations/jigsaw.svg",
      color: "gray",
    },
    {
      title: "Toolhouse",
      description:
        "Toolhouse is a tool management platform that helps developers organize, secure, and scale tool usage across AI agents.",
      href: "/docs/toolhouse",
      iconSrc: "/integrations/toolhouse.svg",
      color: "gray",
    },
  ],
  "real-time-voice": [
    {
      title: "LiveKit",
      description:
        "LiveKit provides text-to-speech and real-time communication features that complement Groq's speech recognition for end-to-end AI voice applications.",
      href: "/docs/livekit",
      iconSrc: "/integrations/livekit_white.svg",
      color: "gray",
    },
  ],
};

---

## What are integrations?

URL: https://console.groq.com/docs/integrations

## What are integrations?

Integrations are a way to connect your application to external services and enhance your Groq-powered applications with additional capabilities.
Browse the categories below to find integrations that suit your needs.

 

 

<div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-4 text-sm text-groq-orange">
 <div className="flex flex-col gap-2">
 <a href="#ai-agent-frameworks" className="hover:underline w-fit">AI Agent Frameworks</a>
 <a href="#llm-app-development" className="hover:underline w-fit">LLM App Development</a>
 <a href="#observability-and-monitoring" className="hover:underline w-fit">Observability and Monitoring</a>
 <a href="#llm-code-execution-and-sandboxing" className="hover:underline w-fit">LLM Code Execution and Sandboxing</a>
 </div>
 <div className="flex flex-col gap-2">
 <a href="#ui-and-ux" className="hover:underline w-fit">UI and UX</a>
 <a href="#tool-management" className="hover:underline w-fit">Tool Management</a>
 <a href="#realtime-voice" className="hover:underline w-fit">Real-time Voice</a>
 </div>
</div>

### AI Agent Frameworks

Create autonomous AI agents that can perform complex tasks, reason, and collaborate effectively using Groq's fast inference capabilities.

 

 

### LLM App Development

Build powerful LLM applications with these frameworks and libraries that provide essential tools for working with Groq models.

 

 

### Observability and Monitoring

Track, analyze, and optimize your LLM applications with these integrations that provide insights into model performance and behavior.

 

 

### LLM Code Execution and Sandboxing

Enable secure code execution in controlled environments for your AI applications with these integrations.

 

 

### UI and UX

Create beautiful and responsive user interfaces for your Groq-powered applications with these UI frameworks and tools.

 

 

### Tool Management

Manage and orchestrate tools for your AI agents, enabling them to interact with external services and perform complex tasks.

 

 

### Real-time Voice

Build voice-enabled applications that leverage Groq's fast inference for natural and responsive conversations.

---

## 🎨 Gradio + Groq: Easily Build Web Interfaces

URL: https://console.groq.com/docs/gradio

## 🎨 Gradio + Groq: Easily Build Web Interfaces

[Gradio](https://www.gradio.app/) is a powerful library for creating web interfaces for your applications that enables you to quickly build 
interactive demos for your fast Groq apps with features such as:

- **Interface Builder:** Create polished UIs with just a few lines of code, supporting text, images, audio, and more
- **Interactive Demos:** Build demos that showcase your LLM applications with multiple input/output components
- **Shareable Apps:** Deploy and share your Groq-powered applications with a single click

### Quick Start (2 minutes to hello world)

####1. Install the packages:
```bash
pip install groq-gradio
```

####2. Set up your API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

####3. Create your first Gradio chat interface:
The following code creates a simple chat interface with `llama-3.3-70b-versatile` that includes a clean UI.
```python
import gradio as gr
import groq_gradio
import os

# Initialize Groq client
client = Groq(
 api_key=os.environ.get("GROQ_API_KEY")
)

gr.load(
 name='llama-3.3-70b-versatile', # The specific model powered by Groq to use
 src=groq_gradio.registry, # Tells Gradio to use our custom interface registry as the source
 title='Groq-Gradio Integration', # The title shown at the top of our UI
 description="Chat with the Llama3.370B model powered by Groq.", # Subtitle
 examples=["Explain quantum gravity to a5-year old.", "How many R are there in the word Strawberry?"] # Pre-written prompts users can click to try
).launch() # Creates and starts the web server!
```

**Challenge**: Enhance the above example to create a multi-modal chatbot that leverages text, audio, and vision models powered by Groq and
displayed on a customized UI built with Gradio blocks!

For more information on building robust applications with Gradio and Groq, see:
- [Official Documentation: Gradio](https://www.gradio.app/docs)
- [Tutorial: Automatic Voice Detection with Groq](https://www.gradio.app/guides/automatic-voice-detection)
- [Groq API Cookbook: Groq and Gradio for Realtime Voice-Powered AI Applications](https://github.com/groq/groq-api-cookbook/blob/main/tutorials/groq-gradio/groq-gradio-tutorial.ipynb)
- [Webinar: Building a Multimodal Voice Enabled Calorie Tracking App with Groq and Gradio](https://youtu.be/azXaioGdm2Q?si=sXPJW1IerbghsCKU)

---

## FlutterFlow + Groq: Fast & Powerful Cross-Platform Apps

URL: https://console.groq.com/docs/flutterflow

## FlutterFlow + Groq: Fast & Powerful Cross-Platform Apps

[**FlutterFlow**](https://flutterflow.io/) is a visual development platform to build high-quality, custom, cross-platform apps. By leveraging Groq's fast AI inference in FlutterFlow, you can build beautiful AI-powered apps to:

- **Build for Scale**: Collaborate efficiently to create robust apps that grow with your needs.
- **Iterate Fast**: Rapidly test, refine, and deploy your app, accelerating your development.
- **Fully Integrate Your Project**: Access databases, APIs, and custom widgets in one place.
- **Deploy Cross-Platform**: Launch on iOS, Android, web, and desktop from a single codebase.

### FlutterFlow + Groq Quick Start (10 minutes to hello world)

####1. Securely store your Groq API Key in FlutterFlow as an App State Variable

Go to the App Values tab in the FlutterFlow Builder, add `groqApiKey` as an app state variable, and enter your API key. It should have type `String` and be `persisted` (that way, the API Key is remembered even if you close out of your application). 

![*Store your api key securely as an App State variable by selecting "secure persisted fields"*](/showcase-applications/flutterflow/flutterflow_1.png)

*Store your api key securely as an App State variable by selecting "secure persisted fields"*

####2. Create a call to the Groq API

Next, navigate to the API calls tab
Create a new API call, call it `Groq Completion`, set the method type as `POST`, and for the API URL, use: https://api.groq.com/openai/v1/chat/completions

Now, add the following variables: 

- `token` - This is your Groq API key, which you can get from the App Values tab.
- `model` - This is the model you want to use. For this example, we'll use `llama-3.3-70b-versatile`.
- `text` - This is the text you want to send to the Groq API.

![Screenshot2025-02-11 at12.05.22 PM.png](/showcase-applications/flutterflow/flutterflow_2.png)

####3. Define your API call header

Once you have added the relevant variables, define your API call header. You can reference the token variable you defined by putting it in square brackets ([]).

Define your API call header as follows: `Authorization: Bearer [token]`

![Screenshot2025-02-11 at12.05.38 PM.png](/showcase-applications/flutterflow/flutterflow_3.png)

####4. Define the body of your API call

You can drag and drop your variables into the JSON body, or include them in angle brackets.

Select JSON, and add the following: 
- `model` - This is the model we defined in the variables section.
- `messages` - This is the message you want to send to the Groq API. We need to add the 'text' variable we defined in the variables section within the message within the system-message.

You can modify the system message to fit your specific use-case. We are going to use a generic system message:
"Provide a helpful answer for the following question - text"

![Screenshot2025-02-11 at12.05.49 PM.png](/showcase-applications/flutterflow/flutterflow_4.png)

####5. Test your API call

By clicking on the “Response & Test” button, you can test your API call. Provide values for your variables, and hit “Test API call” to see the response. 

![Screenshot2025-02-11 at12.32.34 PM.png](/showcase-applications/flutterflow/flutterflow_5.png)

####6. Save relevant JSON Paths of the response
Once you have your API response, you can save relevant JSON Paths of the response. 
To save the content of the response from Groq, you can scroll down and click “Add JSON Path” for `$.choices[:].message.content` and provide a name for it, such as “groqResponse” 

![Screenshot2025-02-11 at12.34.22 PM.png](/showcase-applications/flutterflow/flutterflow_6.png)

####7. Connect the API call to your UI with an action

Now that you have added & tested your API call, let’s connect the API call to your UI with an action.

*If you are interested in following along, you can* [**clone the project**](https://app.flutterflow.io/project/groq-documentation-vc2rt1) *and include your own API Key. You can also follow along with this [3-minute video.](https://www.loom.com/share/053ee6ab744e4cf4a5179fac1405a800?sid=4960f7cd-2b29-4538-89bb-51aa5b76946c)* 

In this page, we create a simple UI that includes a TextField for a user to input their question, a button to trigger our Groq Completion API call, and a Text widget to display the result from the API. We define a page state variable, groqResult, which will be updated to the result from the API. We then bind the Text widget to our page state variable groqResult, as shown below. 

![Screenshot2025-02-25 at3.58.57 PM.png](/showcase-applications/flutterflow/flutterflow_8.png)

####8. Define an action that calls our API

Now that we have created our UI, we can add an action to our button that will call the API, and update our Text with the API’s response. 
To do this, click on the button, open the action editor, and add an action to call the Groq Completion API.

To create our first action to the Groq endpoint, create an action of type Backend API call, and set the "group or call name" to `Groq Completion`.
Then add two additional variables:
- `token` - This is your Groq API key, which you can get from the App State tab.
- `text` - This is the text you want to send to the Groq API, which you can get from the TextField widget.

Finally, rename the action output to `groqResponse`.
![Screenshot2025-02-25 at4.57.28 PM.png](/showcase-applications/flutterflow/flutterflow_10.png)

####9. Update the page state variable

Once the API call succeeds, we can update our page state variable `groqResult` to the contents of the API response from Groq, using the JSON path we created when defining the API call. 

Click on the "+" button for True, and add an action of type "Update Page State". 
Add a field for `groqResult`, and set the value to `groqResponse`, found under Action Output. 
Select `JSON Body` for the API Response Options, `Predifined Path` Path for the Available Options, and `groqResponse` for the Path.

![Screenshot2025-02-25 at5.03.33 PM.png](/showcase-applications/flutterflow/flutterflow_11.png)

![Screenshot2025-02-25 at5.03.47 PM.png](/showcase-applications/flutterflow/flutterflow_12.png)

####10. Run your app in test mode

Now that we have connected our API call to the UI as an action, we can run our app in test mode.

*Watch a [video](https://www.loom.com/share/8f965557a51d43c7ba518280b9c4fd12?sid=006c88e6-a0f2-4c31-bf03-6ba7fc8178a3) of the app live in test mode.* 

![Screenshot2025-02-25 at5.37.17 PM.png](/showcase-applications/flutterflow/flutterflow_13.png)

![Result from Test mode session](/showcase-applications/flutterflow/flutterflow_14.png)

*Result from Test mode session*

**Challenge:** Add to the above example and create a chat-interface, showing the history of the conversation, the current question, and a loading indicator.

### Additional Resources
For additional documentation and support, see the following:

- [Flutterflow Documentation](https://docs.flutterflow.io/)

---

## Batch: List Batches (js)

URL: https://console.groq.com/docs/batch/scripts/list_batches

import Groq from 'groq-sdk';

const groq = new Groq();

async function main() {
 const response = await groq.batches.list();
 console.log(response);
}

main();

---

## Batch: Upload File (py)

URL: https://console.groq.com/docs/batch/scripts/upload_file.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

file_path = "batch_file.jsonl"
response = client.files.create(file=open(file_path, "rb"), purpose="batch")

print(response)
```

---

## Batch: Status (js)

URL: https://console.groq.com/docs/batch/scripts/status

import Groq from 'groq-sdk';

const groq = new Groq();

async function main() {
 const response = await groq.batches.retrieve("batch_01jh6xa7reempvjyh6n3yst2zw");
 console.log(response);
}

main();

---

## Batch: Retrieve (py)

URL: https://console.groq.com/docs/batch/scripts/retrieve.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.files.content("file_01jh6xa97be52b7pg88czwrrwb")
response.write_to_file("batch_results.jsonl")
print("Batch file saved to batch_results.jsonl")
```

---

## Batch: Create Batch Job (js)

URL: https://console.groq.com/docs/batch/scripts/create_batch_job

import Groq from 'groq-sdk';

const groq = new Groq();

async function main() {
  const response = await groq.batches.create({
    completion_window: "24h",
    endpoint: "/v1/chat/completions",
    input_file_id: "file_01jh6x76wtemjr74t1fh0faj5t",
  });
  console.log(response);
}

main();

---

## Batch: Create Batch Job (py)

URL: https://console.groq.com/docs/batch/scripts/create_batch_job.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.batches.create(
    completion_window="24h",
    endpoint="/v1/chat/completions",
    input_file_id="file_01jh6x76wtemjr74t1fh0faj5t",
)
print(response.to_json())
```

---

## Batch: Retrieve (js)

URL: https://console.groq.com/docs/batch/scripts/retrieve

import fs from 'fs';
import Groq from 'groq-sdk';

const groq = new Groq();

async function main() {
 const response = await groq.files.content("file_01jh6xa97be52b7pg88czwrrwb");
 fs.writeFileSync("batch_results.jsonl", await response.text());
 console.log("Batch file saved to batch_results.jsonl");
}

main();

---

## Batch: Status (py)

URL: https://console.groq.com/docs/batch/scripts/status.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.batches.retrieve("batch_01jh6xa7reempvjyh6n3yst2zw")

print(response.to_json())
```

---

## Batch: Upload File (js)

URL: https://console.groq.com/docs/batch/scripts/upload_file

import fs from 'fs';
import Groq from 'groq-sdk';

const groq = new Groq();

async function main() {
 const filePath = 'batch_file.jsonl'; 

 const response = await groq.files.create({
 purpose: 'batch',
 file: fs.createReadStream(filePath)
 });

 console.log(response);
}

main();

---

## Batch: List Batches (py)

URL: https://console.groq.com/docs/batch/scripts/list_batches.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.batches.list()
print(response.to_json())
```

---

## Groq Batch API

URL: https://console.groq.com/docs/batch

## Groq Batch API
Process large-scale workloads asynchronously with our Batch API. 

### What is Batch Processing?
Batch processing lets you run thousands of API requests at scale by submitting your workload as an asynchronous batch of requests to Groq with25% lower cost (50% off from now until end of April2025), no impact to your standard rate limits, and24-hour to7 day processing window.

### Overview
While some of your use cases may require synchronous API requests, asynchronous batch processing is perfect for use cases that don't need immediate reponses or for processing a large number of queries that standard rate limits cannot handle, such as processing large datasets, generating content in bulk, and running evaluations.

Compared to using our synchronous API endpoints, our Batch API has:
- **Higher rate limits:** Process thousands of requests per batch with no impact on your standard API rate limits
- **Cost efficiency:**25% cost discount compared to synchronous APIs (50% off now until end of April2025)

## Model Availability and Pricing
The Batch API can currently be used to execute queries for chat completion (both text and vision), audio transcription, and audio translation inputs with the following models:

<ul>
 <li>mistral-saba-24b</li>
 <li>llama-3.3-70b-versatile</li>
 <li>deepseek-r1-distill-llama-70b</li>
 <li>llama-3.1-8b-instant</li>
 <li>meta-llama/llama-4-scout-17b-16e-instruct</li>
 <li>meta-llama/llama-4-maverick-17b-128e-instruct</li>
</ul>

<ul>
 <li>distil-whisper-large-v3-en</li>
 <li>whisper-large-v3</li>
 <li>whisper-large-v3-turbo</li>
</ul>

<ul>
 <li>whisper-large-v3</li>
</ul>

Pricing is at a25% cost discount compared to [synchronous API pricing (50% off now until end of April2025). ](https://groq.com/pricing)

## Getting Started
Our Batch API endpoints allow you to collect a group of requests into a single file, kick off a batch processing job to execute the requests within your file, query for the status of your batch, and eventually 
retrieve the results when your batch is complete.

Multiple batch jobs can be submitted at once.

Each batch has a processing window, during which we'll process as many requests as our capacity allows while maintaining service quality for all users. We allow for setting 
a batch window from24 hours to7 days and recommend setting a longer batch window allow us more time to complete your batch jobs instead of expiring them.

###1. Prepare Your Batch File
A batch is composed of a list of API requests and every batch job starts with a JSON Lines (JSONL) file that contains the requests
you want processed. Each line in this file represents a single API call.

The Groq Batch API currently supports:
- Chat completion requests through [`/v1/chat/completions`](/docs/text-chat)
- Audio transcription requests through [`/v1/audio/transcriptions`](/docs/speech-to-text)
- Audio translation requests through [`/v1/audio/translations`](/docs/speech-to-text)

The structure for each line must include:
- `custom_id`: Your unique identifier for tracking the batch request
- `method`: The HTTP method (currently `POST` only)
- `url`: The API endpoint to call (one of: `/v1/chat/completions`, `/v1/audio/transcriptions`, or `/v1/audio/translations`)
- `body`: The parameters of your request matching our synchronous API format. See our API Reference [here. ](https://console.groq.com/docs/api-reference#chat-create)

The following is an example of a JSONL batch file with different types of requests:


```json
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is2+2?"}]}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is2+3?"}]}}
{"custom_id": "request-3", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "count up to1000000. starting with1,2,3. print all the numbers, do not stop until you get to1000000."}]}
```

```json
{"custom_id":"job-cb6d01f6-1","method":"POST","url":"/v1/audio/transcriptions","body":{"model":"whisper-large-v3","language":"en","url":"https://github.com/voxserv/audio_quality_testing_samples/raw/refs/heads/master/testaudio/8000/test01_20s.wav","response_format":"verbose_json","timestamp_granularities":["segment"]}}
{"custom_id":"job-cb6d01f6-2","method":"POST","url":"/v1/audio/transcriptions","body":{"model":"whisper-large-v3","language":"en","url":"https://github.com/voxserv/audio_quality_testing_samples/raw/refs/heads/master/testaudio/8000/test01_20s.wav","response_format":"verbose_json","timestamp_granularities":["segment"]}}
{"custom_id":"job-cb6d01f6-3","method":"POST","url":"/v1/audio/transcriptions","body":{"model":"distil-whisper-large-v3-en","language":"en","url":"https://github.com/voxserv/audio_quality_testing_samples/raw/refs/heads/master/testaudio/8000/test01_20s.wav","response_format":"verbose_json","timestamp_granularities":["segment"]}}
```

```json
{"custom_id":"job-cb6d01f6-1","method":"POST","url":"/v1/audio/translations","body":{"model":"whisper-large-v3","language":"en","url":"https://console.groq.com/audio/batch/sample-zh.wav","response_format":"verbose_json","timestamp_granularities":["segment"]}}
```

```json
{"custom_id": "chat-request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is quantum computing?"}]}}
{"custom_id": "audio-request-1", "method": "POST", "url": "/v1/audio/transcriptions", "body": {"model": "whisper-large-v3", "language": "en", "url": "https://github.com/voxserv/audio_quality_testing_samples/raw/refs/heads/master/testaudio/8000/test01_20s.wav", "response_format": "verbose_json", "timestamp_granularities": ["segment"]}}
{"custom_id": "chat-request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Explain machine learning in simple terms."}]}}
{"custom_id":"audio-request-2","method":"POST","url":"/v1/audio/translations","body":{"model":"whisper-large-v3","language":"en","url":"https://console.groq.com/audio/batch/sample-zh.wav","response_format":"verbose_json","timestamp_granularities":["segment"]}}
```

#### Converting Sync Calls to Batch Format 
If you're familiar with making synchronous API calls, converting them to batch format is straightforward. Here's how a regular API call transforms
into a batch request:

```json
# Your typical synchronous API call in Python:
response = client.chat.completions.create(
 model="llama-3.1-8b-instant",
 messages=[
 {"role": "user", "content": "What is quantum computing?"}
 ]
)

# The same call in batch format (must be on a single line as JSONL):
{"custom_id": "quantum-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "What is quantum computing?"}]}}
```

```json
# Your typical synchronous API call in Python:
response = client.audio.transcriptions.create(
 model="whisper-large-v3",
 language="en",
 url="https://example.com/audio-file.wav",
 response_format="verbose_json",
 timestamp_granularities=["segment"]
)

# The same call in batch format (must be on a single line as JSONL):
{"custom_id": "audio-1", "method": "POST", "url": "/v1/audio/transcriptions", "body": {"model": "whisper-large-v3", "language": "en", "url": "https://example.com/audio-file.wav", "response_format": "verbose_json", "timestamp_granularities": ["segment"]}}
```

```json
# Your typical synchronous API call in Python:
response = client.audio.translations.create(
 model="whisper-large-v3",
 language="en",
 url="https://example.com/audio-file.wav",
 response_format="verbose_json",
 timestamp_granularities=["segment"]
)

# The same call in batch format (must be on a single line as JSONL):
{"custom_id": "audio-1", "method": "POST", "url": "/v1/audio/translations", "body": {"model": "whisper-large-v3", "language": "en", "url": "https://example.com/audio-file.wav", "response_format": "verbose_json", "timestamp_granularities": ["segment"]}}
```

###2. Upload Your Batch File
Upload your `.jsonl` batch file using the Files API endpoint for when kicking off your batch job:

**Note:** The Files API currently only supports `.jsonl` files50,000 lines or less and up to maximum of200MB in size. There is no limit for the 
number of batch jobs you can submit. We recommend submitting multiple shorter batch files for a better chance of completion.

You will receive a JSON response that contains the ID (`id`) for your file object that you will then use to create your batch job:
```json
{
 "id":"file_01jh6x76wtemjr74t1fh0faj5t",
 "object":"file",
 "bytes":966,
 "created_at":1736472501,
 "filename":"input_file.jsonl",
 "purpose":"batch"
}
```

###3. Create Your Batch Job 
Once you've uploaded your `.jsonl` file, you can use the file object ID (in this case, `file_01jh6x76wtemjr74t1fh0faj5t` as shown in Step2) to create a batch: 

**Note:** The completion window for batch jobs can be set from to24 hours (`24h`) to7 days (`7d`). We recommend setting a longer batch window 
to have a better chance for completed batch jobs rather than expirations for when we are under heavy load.

This request will return a Batch object with metadata about your batch, including the batch `id` that you can use to check the status of your batch:
```json
{
 "id":"batch_01jh6xa7reempvjyh6n3yst2zw",
 "object":"batch",
 "endpoint":"/v1/chat/completions",
 "errors":null,
 "input_file_id":"file_01jh6x76wtemjr74t1fh0faj5t",
 "completion_window":"24h",
 "status":"validating",
 "output_file_id":null,
 "error_file_id":null,
 "finalizing_at":null,
 "failed_at":null,
 "expired_at":null,
 "cancelled_at":null,
 "request_counts":{
 "total":0,
 "completed":0,
 "failed":0
 },
 "metadata":null,
 "created_at":1736472600,
 "expires_at":1736559000,
 "cancelling_at":null,
 "completed_at":null,
 "in_progress_at":null
}
```

###4. Check Batch Status
You can check the status of a batch any time your heart desires with the batch `id` (in this case, `batch_01jh6xa7reempvjyh6n3yst2zw` from the above Batch response object), which will also return a Batch object:

The status of a given batch job can return any of the following status codes:

| Status | Description |
|---------------|----------------------------------------------------------------------------|
| `validating` | batch file is being validated before the batch processing begins |
| `failed` | batch file has failed the validation process |
| `in_progress` | batch file was successfully validated and the batch is currently being run |
| `finalizing` | batch has completed and the results are being prepared |
| `completed` | batch has been completed and the results are ready |
| `expired` | batch was not able to be completed within the processing window |
| `cancelling` | batch is being cancelled (may take up to10 minutes) |
| `cancelled` | batch was cancelled |

When your batch job is complete, the Batch object will return an `output_file_id` and/or an `error_file_id` that you can then use to retrieve
your results (as shown below in Step5). Here's an example:
```json
{
 "id":"batch_01jh6xa7reempvjyh6n3yst2zw",
 "object":"batch",
 "endpoint":"/v1/chat/completions",
 "errors":[
 {
 "code":"invalid_method",
 "message":"Invalid value: 'GET'. Supported values are: 'POST'","param":"method",
 "line":4
 }
 ],
 "input_file_id":"file_01jh6x76wtemjr74t1fh0faj5t",
 "completion_window":"24h",
 "status":"completed",
 "output_file_id":"file_01jh6xa97be52b7pg88czwrrwb",
 "error_file_id":"file_01jh6xa9cte52a5xjnmnt5y0je",
 "finalizing_at":null,
 "failed_at":null,
 "expired_at":null,
 "cancelled_at":null,
 "request_counts":
 {
 "total":3,
 "completed":2,
 "failed":1
 },
 "metadata":null,
 "created_at":1736472600,
 "expires_at":1736559000,
 "cancelling_at":null,
 "completed_at":1736472607,
 "in_progress_at":1736472601
}
```

###5. Retrieve Batch Results 
Now for the fun. Once the batch is complete, you can retrieve the results using the `output_file_id` from your Batch object (in this case, `file_01jh6xa97be52b7pg88czwrrwb` from the above Batch response object) and write it to
a file on your machine (`batch_output.jsonl` in this case) to view them:

```json
{"id": "batch_req_123", "custom_id": "my-request-1", "response": {"status_code":200, "request_id": "req_abc", "body": {"id": "completion_xyz", "model": "llama-3.1-8b-instant", "choices": [{"index":0, "message": {"role": "assistant", "content": "Hello!"}}], "usage": {"prompt_tokens":20, "completion_tokens":5, "total_tokens":25}}}, "error": null}
```

Any failed or expired requests in the batch will have their error information written to an error file that can be accessed via the batch's `error_file_id`. 
**Note:** Results may not appears in the same order as your batch request submissions. Always use the `custom_id` field to match results with your
original request. 


## List Batches
You can view all your batch jobs by making a call to `https://api.groq.com/openai/v1/batches`:



## Batch Size
The Files API supports JSONL files up to50,000 lines and200MB in size. Multiple batch jobs can be submitted at once.

**Note:** Consider splitting very large workloads into multiple smaller batches (e.g.1000 requests per batch) for a better chance at completion 
rather than expiration for when we are under heavy load.

## Batch Expiration
Each batch has a processing window (24 hours to7 days) during which we'll process as many requests as our capacity allows while maintaining service quality for all users. 

**Note:** We recommend setting a longer batch window for a better chance of completing your batch job rather than returning expired jobs when we are under 
heavy load.

Batch jobs that do not complete within their processing window will have a status of `expired`. 

In cases where your batch job expires:
- You are only charged for successfully completed requests
- You can access all completed results and see which request IDs were not processed
- You can resubmit any uncompleted requests in a new batch


## Data Expiration
Input, intermediate files, and results from processed batches will be stored securely for up to30 days in Groq's systems. You may also immediately delete once a processed batch is retrieved.

## Rate limits
The Batch API rate limits are separate than existing per-model rate limits for synchronous requests. Using the Batch API will not consume tokens 
from your standard per-model limits, which means you can conveniently leverage batch processing to increase the number of tokens you process with
us. 

See your limits [here. ](https://groq.com/settings/limits)

---

## Script: Openai Compat (py)

URL: https://console.groq.com/docs/scripts/openai-compat.py

import os
import openai

client = openai.OpenAI(
 base_url="https://api.groq.com/openai/v1",
 api_key=os.environ.get("GROQ_API_KEY")
)

---

## Script: Openai Compat (js)

URL: https://console.groq.com/docs/scripts/openai-compat

import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.GROQ_API_KEY,
  baseURL: "https://api.groq.com/openai/v1"
});

---

## Qwen Qwq 32b: Model (tsx)

URL: https://console.groq.com/docs/model/qwen-qwq-32b

# Groq Hosted Models: Qwen/QwQ-32B

## Overview

Qwen/Qwq-32B is a 32-billion parameter reasoning model delivering competitive performance against state-of-the-art models like DeepSeek-R1 and o1-mini on complex reasoning and coding tasks. Deployed on Groq's hardware, it provides the world's fastest reasoning, producing chains and results in seconds.

## Key Features

* Competitive performance on complex reasoning and coding tasks
* 32-billion parameter reasoning model
* World's fastest reasoning on Groq's hardware

## Additional Information

* [Groq Chat](https://chat.groq.com/?model=qwen-qwq-32b)

---

## Qwen 2.5 Coder 32b: Model (tsx)

URL: https://console.groq.com/docs/model/qwen-2.5-coder-32b

# Groq Hosted Models: Qwen-2.5-Coder-32B

## Overview

Qwen-2.5-Coder-32B is a specialized version of Qwen-2.5-32B, fine-tuned specifically for code generation and development tasks. Built on 5.5 trillion tokens of code and technical content, it delivers instant, production-quality code generation that matches GPT-4's capabilities.

---

## Model: Eu Notice (tsx)

URL: https://console.groq.com/docs/model/eu-notice

## Usage note:
With respect to any multimodal models included in Llama4, the rights granted under Section 1(a) of the [Llama4 Community License Agreement](https://www.llama.com/llama4/use-policy/) are not being granted to you by Meta if you are an individual domiciled in, or a company with a principal place of business in, the European Union.

---

## Llama3 70b 8192: Model (tsx)

URL: https://console.groq.com/docs/model/llama3-70b-8192

# Groq Hosted Models: llama3-70b-8192

## Overview

Llama3.0 70B on Groq offers a balance of performance and speed as a reliable foundation model that excels at dialogue and content-generation tasks. While newer models have since emerged, Llama3.0 70B remains production-ready and cost-effective with fast, consistent outputs via Groq API.

### Key Features

*   **Performance and Speed**: Llama3.0 70B provides a reliable balance between performance and speed.
*   **Dialogue and Content Generation**: Excels at tasks related to dialogue and content generation.

### Additional Information

*   **OpenGraph Information**
    *   Title: Groq Hosted Models: llama3-70b-8192
    *   Description: Llama3.0 70B on Groq offers a balance of performance and speed as a reliable foundation model that excels at dialogue and content-generation tasks. While newer models have since emerged, Llama3.0 70B remains production-ready and cost-effective with fast, consistent outputs via Groq API.
    *   URL: <https://chat.groq.com/?model=llama3-70b-8192>
    *   Site Name: Groq Hosted AI Models
    *   Locale: en\_US
    *   Type: website

*   **Twitter Information**
    *   Card: summary\_large\_image
    *   Title: Groq Hosted Models: llama3-70b-8192
    *   Description: Llama3.0 70B on Groq offers a balance of performance and speed as a reliable foundation model that excels at dialogue and content-generation tasks. While newer models have since emerged, Llama3.0 70B remains production-ready and cost-effective with fast, consistent outputs via Groq API.

*   **Robots Information**
    *   Index: true
    *   Follow: true

*   **Alternates Information**
    *   Canonical: <https://chat.groq.com/?model=llama3-70b-8192>

---

## Llama 3.1 8b Instant: Model (tsx)

URL: https://console.groq.com/docs/model/llama-3.1-8b-instant

## Groq Hosted Models: llama-3.1-8b-instant

llama-3.1-8b-instant on Groq offers rapid response times with production-grade reliability, suitable for latency-sensitive applications. The model balances efficiency and performance, providing quick responses for chat interfaces, content filtering systems, and large-scale data processing workloads.

---

## Llama 3.2 3b Preview: Model (tsx)

URL: https://console.groq.com/docs/model/llama-3.2-3b-preview

## LLaMA-3.2-3B-Preview

LLaMA-3.2-3B-Preview is one of the fastest models on Groq, offering a great balance of speed and generation quality. With 3.1 billion parameters and a 128K context window, it delivers rapid responses while providing improved accuracy compared to the 1B version. The model excels at tasks like content creation, summarization, and information retrieval, making it ideal for applications where quality matters without requiring a large model. Its efficient design translates to cost-effective performance for real-time applications such as chatbots, content generation, and summarization tasks that need reliable responses with good output quality.

---

## Llama 3.3 70b Specdec: Model (tsx)

URL: https://console.groq.com/docs/model/llama-3.3-70b-specdec

## Groq Hosted Models: Llama-3.3-70B-SpecDec

Llama-3.3-70B-SpecDec is Groq's speculative decoding version of Meta's Llama3.3-70B model, optimized for high-speed inference while maintaining high quality. This speculative decoding variant delivers exceptional performance with significantly reduced latency, making it ideal for real-time applications while maintaining the robust capabilities of the Llama3.3-70B architecture.

### Open Graph Metadata

* **Title**: Groq Hosted Models: Llama-3.3-70B-SpecDec
* **Description**: Llama-3.3-70B-SpecDec is Groq's speculative decoding version of Meta's Llama3.3-70B model, optimized for high-speed inference while maintaining high quality. This speculative decoding variant delivers exceptional performance with significantly reduced latency, making it ideal for real-time applications while maintaining the robust capabilities of the Llama3.3-70B architecture.
* **URL**: https://chat.groq.com/?model=llama-3.3-70b-specdec
* **Site Name**: Groq Hosted AI Models
* **Locale**: en_US
* **Type**: website

### Twitter Metadata

* **Card**: summary_large_image
* **Title**: Groq Hosted Models: Llama-3.3-70B-SpecDec
* **Description**: Llama-3.3-70B-SpecDec is Groq's speculative decoding version of Meta's Llama3.3-70B model, optimized for high-speed inference while maintaining high quality. This speculative decoding variant delivers exceptional performance with significantly reduced latency, making it ideal for real-time applications while maintaining the robust capabilities of the Llama3.3-70B architecture.

### Robots Metadata

* **Index**: true
* **Follow**: true

### Alternates

* **Canonical**: https://chat.groq.com/?model=llama-3.3-70b-specdec

---

## Llama3 8b 8192: Model (tsx)

URL: https://console.groq.com/docs/model/llama3-8b-8192

## Groq Hosted Models: Llama-3-8B-8192

Llama-3-8B-8192 delivers exceptional performance with industry-leading speed and cost-efficiency on Groq hardware. This model stands out as one of the most economical options while maintaining impressive throughput, making it perfect for high-volume applications where both speed and cost matter.

### Key Details

* **Title**: Groq Hosted Models: Llama-3-8B-8192
* **Description**: Llama-3-8B-8192 delivers exceptional performance with industry-leading speed and cost-efficiency on Groq hardware. This model stands out as one of the most economical options while maintaining impressive throughput, making it perfect for high-volume applications where both speed and cost matter.
* **OpenGraph Details**
  * **Title**: Groq Hosted Models: Llama-3-8B-8192
  * **Description**: Llama-3-8B-8192 delivers exceptional performance with industry-leading speed and cost-efficiency on Groq hardware. This model stands out as one of the most economical options while maintaining impressive throughput, making it perfect for high-volume applications where both speed and cost matter.
  * **URL**: https://chat.groq.com/?model=llama3-8b-8192
  * **Site Name**: Groq Hosted AI Models
  * **Locale**: en_US
  * **Type**: website
* **Twitter Details**
  * **Card**: summary_large_image
  * **Title**: Groq Hosted Models: Llama-3-8B-8192
  * **Description**: Llama-3-8B-8192 delivers exceptional performance with industry-leading speed and cost-efficiency on Groq hardware. This model stands out as one of the most economical options while maintaining impressive throughput, making it perfect for high-volume applications where both speed and cost matter.
* **Robots Details**
  * **Index**: true
  * **Follow**: true
* **Alternates Details**
  * **Canonical**: https://chat.groq.com/?model=llama3-8b-8192

---

## Mistral Saba 24b: Model (tsx)

URL: https://console.groq.com/docs/model/mistral-saba-24b

## Groq Hosted Models: Mistral Saba24B

Mistral Saba24B is a specialized model trained to excel in Arabic, Farsi, Urdu, Hebrew, and Indic languages. With a 32K token context window and tool use capabilities, it delivers exceptional results across multilingual tasks while maintaining strong performance in English.

### OpenGraph Metadata

*   **Title**: Groq Hosted Models: Mistral Saba24B
*   **Description**: Mistral Saba24B is a specialized model trained to excel in Arabic, Farsi, Urdu, Hebrew, and Indic languages. With a 32K token context window and tool use capabilities, it delivers exceptional results across multilingual tasks while maintaining strong performance in English.
*   **URL**: <https://chat.groq.com/?model=mistral-saba-24b>
*   **Site Name**: Groq Hosted AI Models
*   **Locale**: en\_US
*   **Type**: website

### Twitter Metadata

*   **Card**: summary\_large\_image
*   **Title**: Groq Hosted Models: Mistral Saba24B
*   **Description**: Mistral Saba24B is a specialized model trained to excel in Arabic, Farsi, Urdu, Hebrew, and Indic languages. With a 32K token context window and tool use capabilities, it delivers exceptional results across multilingual tasks while maintaining strong performance in English.

### Robots Metadata

*   **Index**: true
*   **Follow**: true

### Alternates

*   **Canonical**: <https://chat.groq.com/?model=mistral-saba-24b>

---

## Qwen 2.5 32b: Model (tsx)

URL: https://console.groq.com/docs/model/qwen-2.5-32b

# Groq Hosted Models: Qwen-2.5-32B

## Overview

Qwen-2.5-32B is Alibaba's flagship model, delivering near-instant responses with GPT-4 level capabilities across a wide range of tasks. Built on 5.5 trillion tokens of diverse training data, it excels at everything from creative writing to complex reasoning.

## Key Features

* Near-instant responses
* GPT-4 level capabilities
* 5.5 trillion tokens of diverse training data
* Excels at creative writing, complex reasoning, and more

## Learn More

You can try out the Qwen-2.5-32B model at [https://chat.groq.com/?model=qwen-2.5-32b](https://chat.groq.com/?model=qwen-2.5-32b)

---

## Llama 4 Maverick 17b 128e Instruct: Model (tsx)

URL: https://console.groq.com/docs/model/llama-4-maverick-17b-128e-instruct

## Groq Hosted Models: meta-llama/llama-4-maverick-17b-128e-instruct

### Description

meta-llama/llama-4-maverick-17b-128e-instruct, or Llama4 Maverick, is Meta's 17 billion parameter mixture-of-experts model with 128 experts, featuring native multimodality for text and image understanding. This instruction-tuned model excels at assistant-like chat, visual reasoning, and coding tasks with a 1M token context length. On Groq, this model offers industry-leading performance for inference speed.

[https://console.groq.com/playground?model=meta-llama/llama-4-maverick-17b-128e-instruct](https://console.groq.com/playground?model=meta-llama/llama-4-maverick-17b-128e-instruct)

---

## Deepseek R1 Distill Llama 70b: Model (tsx)

URL: https://console.groq.com/docs/model/deepseek-r1-distill-llama-70b

# Groq Hosted Models: DeepSeek-R1-Distill-Llama-70B

DeepSeek-R1-Distill-Llama-70B is a distilled version of DeepSeek's R1 model, fine-tuned from the Llama-3.3-70B-Instruct base model. This model leverages knowledge distillation to retain robust reasoning capabilities and deliver exceptional performance on mathematical and logical reasoning tasks with Groq's industry-leading speed.

## Overview

DeepSeek-R1-Distill-Llama-70B is a distilled version of DeepSeek's R1 model, fine-tuned from the Llama-3.3-70B-Instruct base model. This model leverages knowledge distillation to retain robust reasoning capabilities and deliver exceptional performance on mathematical and logical reasoning tasks with Groq's industry-leading speed.

### Key Features

*   **Model Details**: 
    *   Model Name: DeepSeek-R1-Distill-Llama-70B
    *   Base Model: Llama-3.3-70B-Instruct
    *   Fine-tuning: Knowledge distillation from DeepSeek's R1 model
*   **Performance**: Exceptional performance on mathematical and logical reasoning tasks
*   **Speed**: Groq's industry-leading speed 

### Additional Information

*   **OpenGraph Details**
    *   Title: Groq Hosted Models: DeepSeek-R1-Distill-Llama-70B
    *   Description: DeepSeek-R1-Distill-Llama-70B is a distilled version of DeepSeek's R1 model, fine-tuned from the Llama-3.3-70B-Instruct base model. This model leverages knowledge distillation to retain robust reasoning capabilities and deliver exceptional performance on mathematical and logical reasoning tasks with Groq's industry-leading speed.
    *   URL: https://chat.groq.com/?model=deepseek-r1-distill-llama-70b
    *   Site Name: Groq Hosted AI Models
    *   Images: 
        *   URL: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B/og-image.jpg
        *   Width: 1200
        *   Height: 630
        *   Alt: DeepSeek-R1-Distill-Llama-70B Model
*   **Twitter Details**
    *   Card: summary_large_image
    *   Title: Groq Hosted Models: DeepSeek-R1-Distill-Llama-70B
    *   Description: DeepSeek-R1-Distill-Llama-70B is a distilled version of DeepSeek's R1 model, fine-tuned from the Llama-3.3-70B-Instruct base model. This model leverages knowledge distillation to retain robust reasoning capabilities and deliver exceptional performance on mathematical and logical reasoning tasks with Groq's industry-leading speed.
    *   Images: 
        *   https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-70B/twitter-image.jpg

### SEO and Indexing

*   **Robots**: 
    *   Index: true
    *   Follow: true
*   **Alternates**: 
    *   Canonical: https://chat.groq.com/?model=deepseek-r1-distill-llama-70b

---

## Llama 3.3 70b Versatile: Model (tsx)

URL: https://console.groq.com/docs/model/llama-3.3-70b-versatile

## Groq Hosted Models: Llama-3.3-70B-Versatile

Llama-3.3-70B-Versatile is Meta's advanced multilingual large language model, optimized for a wide range of natural language processing tasks. With 70 billion parameters, it offers high performance across various benchmarks while maintaining efficiency suitable for diverse applications.

### Open Graph Metadata

* **Title**: Groq Hosted Models: Llama-3.3-70B-Versatile
* **Description**: Llama-3.3-70B-Versatile is Meta's advanced multilingual large language model, optimized for a wide range of natural language processing tasks. With 70 billion parameters, it offers high performance across various benchmarks while maintaining efficiency suitable for diverse applications.
* **URL**: https://chat.groq.com/?model=llama-3.3-70b-versatile
* **Site Name**: Groq Hosted AI Models
* **Locale**: en_US
* **Type**: website

### Twitter Metadata

* **Card**: summary_large_image
* **Title**: Groq Hosted Models: Llama-3.3-70B-Versatile
* **Description**: Llama-3.3-70B-Versatile is Meta's advanced multilingual large language model, optimized for a wide range of natural language processing tasks. With 70 billion parameters, it offers high performance across various benchmarks while maintaining efficiency suitable for diverse applications.

### Robots Metadata

* **Index**: true
* **Follow**: true

### Alternates

* **Canonical**: https://chat.groq.com/?model=llama-3.3-70b-versatile

---

## Model Details

URL: https://console.groq.com/docs/model/playai-tts

### Model Details
- **Name:** PlayAI Dialog 
- **Model IDs:** `playai-tts`, `playai-tts-arabic`
- **Version:**1.0 
- **Developer:** Playht, Inc
- **Terms and Conditions:** Use of this model is subject to Play.ht's [Terms of Service](https://play.ht/terms/#partner-hosted-deployment-terms).

### Model Overview

PlayAI Dialog v1.0 is a generative AI model designed to assist with creative content generation, interactive storytelling, and narrative development. Built on a transformer-based architecture, the model generates human-like audio to support writers, game developers, and content creators in vocalizing text to speech, crafting voice agentic experiences, or exploring interactive dialogue options.

### Key Features

- **Creative Generation**: Produces imaginative and contextually coherent audio based on user prompts and text
- **Interactivity**: Supports dynamic conversation flows suitable for interactive storytelling, agent-like interactions, and gaming scenarios
- **Customizability**: Allows users to clone voices and adjust tone, style, or narrative focus through configurable parameters

### Model Architecture and Training

#### Architecture

- Based on a transformer architecture similar to state-of-the-art large language models
- Optimized for high-quality speech output in a large variety of accents and styles

#### Training Data

- **Sources**: A blend of publicly available video and audio works, and interactive dialogue datasets, supplemented with licensed creative content and recordings
- **Volume**: Trained on millions of audio samples spanning diverse genres, narrative, and conversational styles
- **Preprocessing**: Involves standard audio normalization, tokenization, and filtering to remove sensitive or low-quality content

### Evaluation and Performance Metrics

#### Evaluation Datasets

- Internally curated audio and dialogue datasets
- Human user feedback from beta testing in creative applications and testing

### Limitations and Bias Considerations

#### Known Limitations

- **Cultural Bias**: The model's outputs can reflect biases present in its training data. It might underrepresent certain pronunciations and accents.
- **Variability**: The inherently stochastic nature of creative generation means that outputs can be unpredictable and may require human curation.

#### Bias and Fairness Mitigation

- **Bias Audits**: Regular reviews and bias impact assessments are conducted to identify poor quality or unintended audio generations.
- **User Controls**: Users are encouraged to provide feedback on problematic outputs, which informs iterative updates and bias mitigation strategies.

### Ethical and Regulatory Considerations

#### Data Privacy

- All training data has been processed and anonymized in accordance with GDPR and other relevant data protection laws.
- We do not train on any of our user data.

#### Responsible Use Guidelines

- This model should be used in accordance with [Play.ht's Terms of Service](https://play.ht/terms/#partner-hosted-deployment-terms)
- Users should ensure the model is applied responsibly, particularly in contexts where content sensitivity is important.
- The model should not be used to generate harmful, misleading, or plagiarized content.

### Maintenance and Updates

#### Versioning

- PlayAI Dialog v1.0 is the inaugural release.
- Future versions will integrate more languages, emotional controllability, and custom voices.

#### Support and Feedback

- Users are invited to submit feedback and report issues via "Chat with us" on [Groq Console](https://console.groq.com).
- Regular updates and maintenance reviews are scheduled to ensure ongoing compliance with legal standards and to incorporate evolving best practices.

### Licensing

- **License**: PlayAI-Groq Commercial License

---

## Llama Guard 3 8b: Model (tsx)

URL: https://console.groq.com/docs/model/llama-guard-3-8b

## Groq Hosted Models: Llama-Guard-3-8B

Llama-Guard-3-8B, a specialized content moderation model built on the Llama framework, excels at identifying and filtering potentially harmful content. Groq supports fast inference with industry-leading latency and performance for high-speed AI processing for your content moderation applications.

### Overview

*   **Title**: Groq Hosted Models: Llama-Guard-3-8B
*   **Description**: Llama-Guard-3-8B, a specialized content moderation model built on the Llama framework, excels at identifying and filtering potentially harmful content. Groq supports fast inference with industry-leading latency and performance for high-speed AI processing for your content moderation applications.
*   **OpenGraph**:
    *   **Title**: Groq Hosted Models: Llama-Guard-3-8B
    *   **Description**: Llama-Guard-3-8B, a specialized content moderation model built on the Llama framework, excels at identifying and filtering potentially harmful content. Groq supports fast inference with industry-leading latency and performance for high-speed AI processing for your content moderation applications.
    *   **URL**: <https://chat.groq.com/?model=llama-guard-3-8b>
    *   **Site Name**: Groq Hosted AI Models
    *   **Locale**: en\_US
    *   **Type**: website
*   **Twitter**:
    *   **Card**: summary\_large\_image
    *   **Title**: Groq Hosted Models: Llama-Guard-3-8B
    *   **Description**: Llama-Guard-3-8B, a specialized content moderation model built on the Llama framework, excels at identifying and filtering potentially harmful content. Groq supports fast inference with industry-leading latency and performance for high-speed AI processing for your content moderation applications.

### SEO and Indexing

*   **Robots**:
    *   **Index**: true
    *   **Follow**: true
*   **Alternates**:
    *   **Canonical**: <https://chat.groq.com/?model=llama-guard-3-8b>

---

## Deepseek R1 Distill Qwen 32b: Model (tsx)

URL: https://console.groq.com/docs/model/deepseek-r1-distill-qwen-32b

# Groq Hosted Models: DeepSeek-R1-Distill-Qwen-32B

## Overview

DeepSeek-R1-Distill-Qwen-32B is a distilled version of DeepSeek's R1 model, fine-tuned from the Qwen-2.5-32B base model. This model leverages knowledge distillation to retain robust reasoning capabilities while enhancing efficiency. Delivering exceptional performance on mathematical and logical reasoning tasks, it achieves near-o1 level capabilities with faster response times. With its massive 128K context window, native tool use, and JSON mode support, it excels at complex problem-solving while maintaining the reasoning depth of much larger models.

### Key Features

*   **Massive Context Window**: 128K context window for handling long-range dependencies and complex tasks.
*   **Native Tool Use**: Seamlessly integrates with external tools and APIs.
*   **JSON Mode Support**: Enables efficient data exchange and processing.

### Performance

DeepSeek-R1-Distill-Qwen-32B delivers exceptional performance on mathematical and logical reasoning tasks, achieving near-o1 level capabilities with faster response times. Its massive 128K context window, native tool use, and JSON mode support make it an ideal choice for complex problem-solving.

---

## Llama 3.2 1b Preview: Model (tsx)

URL: https://console.groq.com/docs/model/llama-3.2-1b-preview

## Groq Hosted Models: LLaMA-3.2-1B-Preview

LLaMA-3.2-1B-Preview is one of the fastest models on Groq, making it perfect for cost-sensitive, high-throughput applications. With just 1.23 billion parameters and a 128K context window, it delivers near-instant responses while maintaining impressive accuracy for its size. The model excels at essential tasks like text analysis, information retrieval, and content summarization, offering an optimal balance of speed, quality, and cost. Its lightweight nature translates to significant cost savings compared to larger models, making it an excellent choice for rapid prototyping, content processing, and applications requiring quick, reliable responses without excessive computational overhead.

### Key Features

* **High-Speed Performance**: Delivers near-instant responses
* **Cost-Effective**: Significant cost savings compared to larger models
* **Optimal Balance**: Balances speed, quality, and cost

### Use Cases

* Rapid prototyping
* Content processing
* Applications requiring quick, reliable responses

### Additional Information

* [Open Graph URL](https://chat.groq.com/?model=llama-3.2-1b-preview)
* Site Name: Groq Hosted AI Models
* Locale: en_US
* Type: website 

## Social Media Previews

### Twitter
* Card: summary_large_image
* Title: Groq Hosted Models: LLaMA-3.2-1B-Preview
* Description: LLaMA-3.2-1B-Preview is one of the fastest models on Groq, making it perfect for cost-sensitive, high-throughput applications. With just 1.23 billion parameters and a 128K context window, it delivers near-instant responses while maintaining impressive accuracy for its size. The model excels at essential tasks like text analysis, information retrieval, and content summarization, offering an optimal balance of speed, quality and cost. Its lightweight nature translates to significant cost savings compared to larger models, making it an excellent choice for rapid prototyping, content processing, and applications requiring quick, reliable responses without excessive computational overhead.

### Open Graph
* Title: Groq Hosted Models: LLaMA-3.2-1B-Preview
* Description: LLaMA-3.2-1B-Preview is one of the fastest models on Groq, making it perfect for cost-sensitive, high-throughput applications. With just 1.23 billion parameters and a 128K context window, it delivers near-instant responses while maintaining impressive accuracy for its size. The model excels at essential tasks like text analysis, information retrieval, and content summarization, offering an optimal balance of speed, quality and cost. Its lightweight nature translates to significant cost savings compared to larger models, making it an excellent choice for rapid prototyping, content processing, and applications requiring quick, reliable responses without excessive computational overhead.

## SEO Settings

* Index: true
* Follow: true
* Canonical URL: https://chat.groq.com/?model=llama-3.2-1b-preview

---

## Llama 4 Scout 17b 16e Instruct: Model (tsx)

URL: https://console.groq.com/docs/model/llama-4-scout-17b-16e-instruct

## Groq Hosted Models: meta-llama/llama-4-scout-17b-16e-instruct

### Description

meta-llama/llama-4-scout-17b-16e-instruct, or Llama4 Scout, is Meta's 17 billion parameter mixture-of-experts model with 16 experts, featuring native multimodality for text and image understanding. This instruction-tuned model excels at assistant-like chat, visual reasoning, and coding tasks with a 10M token context length. On Groq, this model offers industry-leading performance for inference speed.

### Additional Information

- **OpenGraph Details**
  - Title: Groq Hosted Models: meta-llama/llama-4-scout-17b-16e-instruct
  - Description: meta-llama/llama-4-scout-17b-16e-instruct, or Llama4 Scout, is Meta's 17 billion parameter mixture-of-experts model with 16 experts, featuring native multimodality for text and image understanding. This instruction-tuned model excels at assistant-like chat, visual reasoning, and coding tasks with a 10M token context length. On Groq, this model offers industry-leading performance for inference speed.
  - URL: https://console.groq.com/playground?model=meta-llama/llama-4-scout-17b-16e-instruct
  - Site Name: Groq Hosted AI Models
  - Locale: en_US
  - Type: website

- **Twitter Details**
  - Card: summary_large_image
  - Title: Groq Hosted Models: meta-llama/llama-4-scout-17b-16e-instruct
  - Description: meta-llama/llama-4-scout-17b-16e-instruct, or Llama4 Scout, is Meta's 17 billion parameter mixture-of-experts model with 16 experts, featuring native multimodality for text and image understanding. This instruction-tuned model excels at assistant-like chat, visual reasoning, and coding tasks with a 10M token context length. On Groq, this model offers industry-leading performance for inference speed.

- **Robots**
  - Index: true
  - Follow: true

- **Alternates**
  - Canonical: https://console.groq.com/playground?model=meta-llama/llama-4-scout-17b-16e-instruct

---

## LiveKit + Groq: Build End-to-End AI Voice Applications

URL: https://console.groq.com/docs/livekit

## LiveKit + Groq: Build End-to-End AI Voice Applications

[LiveKit](https://livekit.io) complements Groq's high-performance speech recognition capabilities by providing text-to-speech and real-time communication features. This integration enables you to build 
end-to-end AI voice applications with:

- **Complete Voice Pipeline:** Combine Groq's fast and accurate speech-to-text (STT) with LiveKit's text-to-speech (TTS) capabilities
- **Real-time Communication:** Enable multi-user voice interactions with LiveKit's WebRTC infrastructure
- **Flexible TTS Options:** Access multiple text-to-speech voices and languages through LiveKit's TTS integrations
- **Scalable Architecture:** Handle thousands of concurrent users with LiveKit's distributed system

### Quick Start (7 minutes to hello world)

####1. Prerequisites
- Grab your [Groq API Key](https://console.groq.com/keys)
- Create a free [LiveKit Cloud account](https://cloud.livekit.io/login)
- Install the [LiveKit CLI](https://docs.livekit.io/home/cli/cli-setup/) and authenticate in your Command Line Interface (CLI)
- Create a free ElevenLabs account and [generate an API Key](https://elevenlabs.io/app/settings/api-keys)

####1. Clone the starter template for our Python voice agent using your CLI:

When prompted for your OpenAI and Deepgram API key, press **Enter** to skip as we'll be using custommized plugins for Groq and ElevenLabs for fast inference speed.

```bash
lk app create --template voice-pipeline-agent-python
```

####2. CD into your project directory and update the `.env.local` file to replace `OPENAI_API_KEY` and `DEEPGRAM_API_KEY` with the following:
```bash
GROQ_API_KEY=<your-groq-api-key>
ELEVEN_API_KEY=<your-elevenlabs-api-key>
```

####3. Update your `requirements.txt` file and add the following line:
```bash
livekit-plugins-elevenlabs>=0.7.9
```

####4. Update your `agent.py` file with the following to configure Groq for STT with `whisper-large-v3`, Groq for LLM with `llama-3.3-70b-versatile`, and ElevenLabs for TTS:

```python
import logging

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc):
 proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx):
 initial_ctx = (
 "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
 "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
 "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
 )

 logger.info(f"connecting to room {ctx.room.name}")
 await ctx.connect()

 # Wait for the first participant to connect
 participant = await ctx.wait_for_participant()
 logger.info(f"starting voice assistant for participant {participant.identity}")


 agent.start(ctx.room, participant)

 # The agent should be polite and greet the user when it joins :)
 await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
 
 WorkerOptions(
 entrypoint_fnc=entrypoint,
 prewarm_fnc=prewarm,
 )

```

####5. Make sure you're in your project directory to install the dependencies and start your agent:
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 agent.py dev
```

####6. Within your project directory, clone the voice assistant frontend Next.js app starter template using your CLI:
```bash
lk app create --template voice-assistant-frontend
```

####7. CD into your frontend directory and launch your frontend application locally:
```bash
pnpm install
pnpm dev
```

####8. Visit your application (http://localhost:3000/ by default), select **Connect** and talk to your agent! 


**Challenge:** Configure your voice assistant and the frontend to create a travel agent that will help plan trips! 


For more detailed documentation and resources, see:
- [Official Documentation: LiveKit](https://docs.livekit.io)

---

## Agno + Groq: Lightning Fast Agents

URL: https://console.groq.com/docs/agno

## Agno + Groq: Lightning Fast Agents

[Agno](https://github.com/agno-agi/agno) is a lightweight framework for building multi-modal Agents. Its easy to use, extremely fast and supports multi-modal inputs and outputs.

With Groq & Agno, you can build:

- **Agentic RAG**: Agents that can search different knowledge stores for RAG or dynamic few-shot learning.
- **Image Agents**: Agents that can understand images and make tool calls accordingly.
- **Reasoning Agents**: Agents that can reason using a reasoning model, then generate a result using another model.
- **Structured Outputs**: Agents that can generate pydantic objects adhering to a schema.

### Python Quick Start (2 minutes to hello world)

Agents are autonomous programs that use language models to achieve tasks. They solve problems by running tools, accessing knowledge and memory to improve responses.

Let's build a simple web search agent, with a tool to search DuckDuckGo to get better results. 

####1. Create a file called `web_search_agent.py` and add the following code:
```python web_search_agent.py
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools

# Initialize the agent with an LLM via Groq and DuckDuckGoTools
agent = Agent(
 model=Groq(id="llama-3.3-70b-versatile"),
 description="You are an enthusiastic news reporter with a flair for storytelling!",
 tools=[DuckDuckGoTools()], # Add DuckDuckGo tool to search the web
 show_tool_calls=True, # Shows tool calls in the response, set to False to hide
 markdown=True # Format responses in markdown
)

# Prompt the agent to fetch a breaking news story from New York
agent.print_response("Tell me about a breaking news story from New York.", stream=True)
```

####3. Set up and activate your virtual environment:
```shell
python3 -m venv .venv
source .venv/bin/activate
```

####4. Install the Groq, Agno, and DuckDuckGo dependencies:
```shell
pip install -U groq agno duckduckgo-search
```

####5. Configure your Groq API Key:
```bash
GROQ_API_KEY="your-api-key"
```

####6. Run your Agno agent that now extends your LLM's context to include web search for up-to-date information and send results in seconds:
```shell
python web_search_agent.py
```

### Multi-Agent Teams
Agents work best when they have a singular purpose, a narrow scope, and a small number of tools. When the number of tools grows beyond what the language model can handle or the tools belong to different 
categories, use a **team of agents** to spread the load.

The following code expands upon our quick start and creates a team of two agents to provide analysis on financial markets:
```python agent_team.py
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
 name="Web Agent",
 role="Search the web for information",
 model=Groq(id="llama-3.3-70b-versatile"),
 tools=[DuckDuckGoTools()],
 instructions="Always include sources",
 markdown=True,
)

finance_agent = Agent(
 name="Finance Agent",
 role="Get financial data",
 model=Groq(id="llama-3.3-70b-versatile"),
 tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
 instructions="Use tables to display data",
 markdown=True,
)

agent_team = Agent(
 team=[web_agent, finance_agent],
 model=Groq(id="llama-3.3-70b-versatile"), # You can use a different model for the team leader agent
 instructions=["Always include sources", "Use tables to display data"],
 # show_tool_calls=True, # Uncomment to see tool calls in the response
 markdown=True,
)

# Give the team a task
agent_team.print_response("What's the market outlook and financial performance of AI semiconductor companies?", stream=True)
```

### Additional Resources
For additional documentation and support, see the following:

- [Agno Documentation](https://docs.agno.com)
- [Groq via Agno Documentation](https://docs.agno.com/models/groq)
- [Groq via Agno examples](https://docs.agno.com/examples/models/groq/basic)
- [Various industry-ready examples](https://docs.agno.com/examples/introduction)

---

## API Error Codes and Responses

URL: https://console.groq.com/docs/errors

## API Error Codes and Responses

Our API uses standard HTTP response status codes to indicate the success or failure of an API request. In cases of errors, the body of the response will contain a JSON object with details about the error. Below are the error codes you may encounter, along with their descriptions and example response bodies.

### Error Codes Documentation

Our API uses specific error codes to indicate the success or failure of an API request. Understanding these codes and their implications is essential for effective error handling and debugging.

### Success Codes

- **200 OK**: The request was successfully executed. No further action is needed.

### Client Error Codes

- **400 Bad Request**: The server could not understand the request due to invalid syntax. Review the request format and ensure it is correct.
- **401 Unauthorized**: The request was not successful because it lacks valid authentication credentials for the requested resource. Ensure the request includes the necessary authentication credentials and the api key is valid.
- **404 Not Found**: The requested resource could not be found. Check the request URL and the existence of the resource.
- **413 Request Entity Too Large**: The request body is too large. Please reduce the size of the request body.
- **422 Unprocessable Entity**: The request was well-formed but could not be followed due to semantic errors. Verify the data provided for correctness and completeness.
- **429 Too Many Requests**: Too many requests were sent in a given timeframe. Implement request throttling and respect rate limits.
- **498 Custom: Flex Tier Capacity Exceeded**: This is a custom status code we use and will return in the event that the flex tier is at capacity and the request won't be processed. You can try again later.
- **499 Custom: Request Cancelled**: This is a custom status code we use in our logs page to signify when the request is cancelled by the caller.

### Server Error Codes

- **500 Internal Server Error**: A generic error occurred on the server. Try the request again later or contact support if the issue persists.
- **502 Bad Gateway**: The server received an invalid response from an upstream server. This may be a temporary issue; retrying the request might resolve it.
- **503 Service Unavailable**: The server is not ready to handle the request, often due to maintenance or overload. Wait before retrying the request.

### Informational Codes

- **206 Partial Content**: Only part of the resource is being delivered, usually in response to range headers sent by the client. Ensure this is expected for the request being made.

### Error Object Explanation

When an error occurs, our API returns a structured error object containing detailed information about the issue. This section explains the components of the error object to aid in troubleshooting and error handling.

### Error Object Structure

The error object follows a specific structure, providing a clear and actionable message alongside an error type classification:

```json
{
 "error": {
 "message": "String - description of the specific error",
 "type": "invalid_request_error"
 }
}
```

### Components

- **`error` (object):** The primary container for error details.
 - **`message` (string):** A descriptive message explaining the nature of the error, intended to aid developers in diagnosing the problem.
 - **`type` (string):** A classification of the error type, such as `"invalid_request_error"`, indicating the general category of the problem encountered.

---

## Composio

URL: https://console.groq.com/docs/composio

## Composio

[Composio](https://composio.ai/) is a platform for managing and integrating tools with LLMs and AI agents. You can build fast, Groq-based assistants to seamlessly interact with external applications 
through features including:

- **Tool Integration:** Connect AI agents to APIs, RPCs, shells, file systems, and web browsers with90+ readily available tools
- **Authentication Management:** Secure, user-level auth across multiple accounts and tools
- **Optimized Execution:** Improve security and cost-efficiency with tailored execution environments
- **Comprehensive Logging:** Track and analyze every function call made by your LLMs

### Python Quick Start (5 minutes to hello world)
####1. Install the required packages:
```bash
pip install composio-langchain langchain-groq
```

####2. Configure your Groq and [Composio](https://app.composio.dev/) API keys:
```bash
export GROQ_API_KEY="your-groq-api-key"
export COMPOSIO_API_KEY="your-composio-api-key"
```

####3. Connect your first Composio tool:
```bash
# Connect GitHub (you'll be guided through OAuth flow to get things going)
composio add github

# View all available tools
composio apps
```

####4. Create your first Composio-enabled Groq agent:

Running this code will create an agent that can interact with GitHub through natural language in mere seconds! Your agent will be able to:
- Perform GitHub operations like starring repos and creating issues for you
- Securely manage your OAuth flows and API keys
- Process natural language to convert your requests into specific tool actions 
- Provide feedback to let you know about the success or failure of operations

```python
from langchain.agents import AgentType, initialize_agent
from langchain_groq import ChatGroq
from composio_langchain import ComposioToolSet, App

# Initialize LLM
llm = ChatGroq(model="llama-3.3-70b-versatile")

# Get Composio tools (GitHub in this example)
composio_toolset = ComposioToolSet()
tools = composio_toolset.get_tools(apps=[App.GITHUB])

# Create agent
agent = initialize_agent(
 tools,
 llm,
 agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
 verbose=True
)

# Define task and run
task = "Star groq/groq-api-cookbook repo on GitHub"
agent.run(task)
```

**Challenge**: Create a Groq-powered agent that can summarize your GitHub issues and post updates to Slack through Composio tools! 


For more detailed documentation and resources on building AI agents with Groq and Composio, see:
- [Composio documentation](https://docs.composio.dev/framework/groq)
- [Guide to Building Agents with Composio and Llama3.1 models powered by Groq](https://composio.dev/blog/tool-calling-in-llama-3-a-guide-to-build-agents/)
- [Groq API Cookbook tutorial](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/composio-newsletter-summarizer-agent)

---

## Changelog

URL: https://console.groq.com/docs/legacy-changelog

## Changelog

Welcome to the Groq Changelog, where you can follow ongoing developments to our API.

### April5,2025
- Shipped Meta's Llama4 models. See more on our [models page](/docs/models).

### April4,2025
- Shipped new console home page. See yours [here](/home).

### March26,2025
- Shipped text-to-speech models `playai-tts` and `playai-tts-arabic`. See more on our [models page](/docs/models).

### March13,2025
- Batch processing is50% off now until end of April2025! Learn how to submit a batch job [here](/docs/batch).  

### March11,2025
- Added support for word level timestamps. See more in our [speech-to-text docs](/docs/speech-to-text).
- Added [llms.txt](/llms.txt) and [llms-full.txt](/llms-full.txt) files to make it easy for you to use our docs as context for models and AI agents.

### March5,2025
- Shipped `qwen-qwq-32b`. See more on our [models page](/docs/models).

### February25,2025
- Shipped `mistral-saba-24b`. See more on our [models page](/docs/models).

### February13,2025
- Shipped `qwen-2.5-coder-32b`. See more on our [models page](/docs/models).

### February10,2025
- Shipped `qwen-2.5-32b`. See more on our [models page](/docs/models).
- Shipped `deepseek-r1-distill-qwen-32b`. See more on our [models page](/docs/models).

### February5,2025
- Updated integrations to include [Agno](/docs/agno).

### February3,2025
- Shipped `deepseek-r1-distill-llama-70b-specdec`. See more on our [models page](/docs/models).

### January29,2025
- Added support for tool use and JSON mode for `deepseek-r1-distill-llama-70b`. 

### January26,2025
- Released `deepseek-r1-distill-llama-70b`. See more on our [models page](/docs/models).

### January9,2025
- Added [batch API docs](/docs/batch).

### January7,2025
- Updated integrations pages to include quick start guides and additional resources.
- Updated [deprecations](/docs/deprecations) for Llama3.1 and Llama3.0 Tool Use models.
- Updated [speech docs](/docs/speech-text)

### December17,2024
- Updated integrations to include [CrewAI](/docs/crewai).
- Updated [deprecations page](/docs/deprecations) to include `gemma-7b-it`.

### December6,2024
- Released `llama-3.3-70b-versatile` and `llama-3.3-70b-specdec`. See more on our [models page](https://console.groq.com/docs/models).

### November15,2024
- Released `llama-3.1-70b-specdec` model for customers. See more on our [models page](https://console.groq.com/docs/models).

### October18,2024
- Deprecated `llava-v1.5-7b-4096-preview` model. 

### October9,2024
- Released `whisper-large-v3-turbo` model. See more on our [models page](https://console.groq.com/docs/models).
- Released `llama-3.2-90b-vision-preview` model. See more on our [models page](https://console.groq.com/docs/models).
- Updated integrations to include [xRx](https://console.groq.com/docs/xrx).

### September27,2024
- Released `llama-3.2-11b-vision-preview` model. See more on our [models page](https://console.groq.com/docs/models). 
- Updated Integrations to include [JigsawStack](https://console.groq.com/docs/jigsawstack).

### September25,2024
- Released `llama-3.2-1b-preview` model. See more on our [models page](https://console.groq.com/docs/models). 
- Released `llama-3.2-3b-preview` model. See more on our [models page](https://console.groq.com/docs/models). 
- Released `llama-3.2-90b-text-preview` model. See more on our [models page](https://console.groq.com/docs/models).

### September24,2024
- Revamped tool use documentation with in-depth explanations and code examples.
- Upgraded code box style and design.

### September3,2024

- Released `llava-v1.5-7b-4096-preview` model. 
- Updated Integrations to include [E2B](https://console.groq.com/docs/e2b).

### August20,2024

- Released 'distil-whisper-large-v3-en' model. See more on our [models page](https://console.groq.com/docs/models).

### August8,2024

- Moved 'llama-3.1-405b-reasoning' from preview to offline due to overwhelming demand. Stay tuned for updates on availability!

### August1,2024

- Released 'llama-guard-3-8b' model. See more on our [models page](https://console.groq.com/docs/models).

### July23,2024

- Released Llama3.1 suite of models in preview ('llama-3.1-8b-instant', 'llama-3.1-70b-versatile', 'llama-3.1-405b-reasoning'). Learn more in [our blog post](https://groq.link/llama3405bblog).

### July16,2024

- Released 'Llama3-groq-70b-tool-use' and 'Llama3-groq-8b-tool-use' models in

 preview, learn more in [our blog post](https://wow.groq.com/introducing-llama-3-groq-tool-use-models/).

### June24,2024

- Released 'whisper-large-v3' model.

### May8,2024

- Released 'whisper-large-v3' model as a private beta.

### April19,2024

- Released 'llama3-70b-8192' and 'llama3-8b-8192' models.

### April10,2024

- Upgraded Gemma to `gemma-1.1-7b-it`.

### April3,2024

- [Tool use](/docs/tool-use) released in beta.

### March28,2024

- Launched the [Groq API Cookbook](https://github.com/groq/groq-api-cookbook).

### March21,2024

- Added JSON mode and streaming to [Playground](https://console.groq.com/playground).

### March8,2024

- Released `gemma-7b-it` model.

### March6,2024

- Released [JSON mode](/docs/text-chat#json-mode-object-object), added `seed` parameter.

### Feb26,2024

- Released Python and Javascript LlamaIndex [integrations](/docs/llama-index).

### Feb21,2024

- Released Python and Javascript Langchain [integrations](/docs/langchain).

### Feb16,2024

- Beta launch
- Released GroqCloud [Javascript SDK](/docs/libraries).

### Feb7,2024

- Private Beta launch
- Released `llama2-70b` and `mixtral-8x7b` models.
- Released GroqCloud [Python SDK](/docs/libraries).

---

## Overview: Chat (json)

URL: https://console.groq.com/docs/overview/scripts/chat.json

```
{
 "model": "llama-3.3-70b-versatile",
 "messages": [
 {
 "role": "user",
 "content": "Explain the importance of fast language models"
 }
 ]
}
```

---

## Overview: Chat (py)

URL: https://console.groq.com/docs/overview/scripts/chat.py

from groq import Groq
import os

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],
 model="llama-3.3-70b-versatile",
 stream=False,
)

print(chat_completion.choices[0].message.content)

---

## Overview: Chat (js)

URL: https://console.groq.com/docs/overview/scripts/chat

```javascript
// Default
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
  const completion = await groq.chat.completions
    .create({
      messages: [
        {
          role: "user",
          content: "Explain the importance of fast language models",
        },
      ],
      model: "llama-3.3-70b-versatile",
    })
    .then((chatCompletion) => {
      console.log(chatCompletion.choices[0]?.message?.content || "");
    });
}

main();
```

---

## Overview

URL: https://console.groq.com/docs/overview

## Overview
Fast LLM inference, OpenAI-compatible. Simple to integrate, easy to scale. Start building in minutes.

#### Start building apps on Groq

<div className="md:flex flex-row mt-6 mb-6 items-stretch">
 <div className="flex-1 mb-4 md:mb-0 md:mr-4">
  <p className="pb-6">Get up and running with the Groq API in a few minutes.</p>
  <p className="">Create and setup your API Key</p>
 </div>
 <div className="flex-1 mb-4 md:mb-0 md:mr-4">
  <p className="pb-6">Experiment with the Groq API</p>
 </div>
 <div className="flex-1 mb-4 md:mb-0 md:mr-4">
  <p className="pb-6">Check out cool Groq built apps</p>
 </div>
</div>

#### Developer Resources

<p className="text-xs pb-7">Essential resources to accelerate your development and maximize productivity</p>

<div className="flex flex-row mb-7">
 <div className="flex-1">
  <p className="">Explore all API parameters and response attributes</p>
 </div>
 <div className="flex-1">
  <p className="">Check out sneak peeks, announcements & get support</p>
 </div>
</div>

<div className="flex flex-row mb-7">
 <div className="flex-1">
  <p className="">See code examples and tutorials to jumpstart your app</p>
 </div>
 <div className="flex-1">
  <p className="">Compatible with OpenAI's client libraries</p>
 </div>
</div>

#### The Models

<p className="text-xs pb-7">We’re adding new models all the time and will let you know when a new one comes online. See full details on our Models page.</p>

<div className="flex flex-row mb-6 items-stretch">
 <div className="flex-1 mr-4">
  <p className="">Deepseek R1 Distill Llama70B</p>
 </div>

 <div className="flex-1 mr-4">
  <p className="">Llama3.3,3.2,3.1, and LlamaGuard</p>
 </div>
</div>

<div className="flex flex-row mb-6 items-stretch">
 <div className="flex-1 mr-4">
  <p className="">Whisper Large v3, Turbo, and Distill</p>
 </div>

 <div className="flex-1 mr-4">
  <p className="">Gemma2</p>
 </div>
</div>

---

## ✨ Vercel AI SDK + Groq: Rapid App Development

URL: https://console.groq.com/docs/ai-sdk

## ✨ Vercel AI SDK + Groq: Rapid App Development

Vercel's AI SDK enables seamless integration with Groq, providing developers with powerful tools to leverage language models hosted on Groq for a variety of applications. By combining Vercel's cutting-edge platform with Groq's advanced inference capabilities, developers can create scalable, high-speed applications with ease.

### Why Choose the Vercel AI SDK?
- A versatile toolkit for building applications powered by advanced language models like Llama3.370B 
- Ideal for creating chat interfaces, document summarization, and natural language generation
- Simple setup and flexible provider configurations for diverse use cases
- Fully supports standalone usage and seamless deployment with Vercel
- Scalable and efficient for handling complex tasks with minimal configuration

### Quick Start Guide in JavaScript (5 minutes to deployment)

####1. Create a new Next.js project with the AI SDK template:
```bash
npx create-next-app@latest my-groq-app --typescript --tailwind --src-dir
cd my-groq-app
```
####2. Install the required packages:
```bash
npm install @ai-sdk/groq ai
npm install react-markdown
```

####3. Create a `.env.local` file in your project root and configure your Groq API Key:
```bash
GROQ_API_KEY="your-api-key"
```

####4. Create a new directory structure for your Groq API endpoint:
```bash
mkdir -p src/app/api/chat
```

####5. Initialize the AI SDK by creating an API route file called `route.ts` in `app/api/chat`:
```javascript
const { messages } = await req.json();

const result = streamText({
  model: groq('llama-3.3-70b-versatile'),
  messages,
});

return result.toDataStreamResponse();
```

**Challenge**: Now that you have your basic chat interface working, try enhancing it to create a specialized code explanation assistant! 


####6. Create your front end interface by updating the `app/page.tsx` file:
```javascript
const { messages, input, handleInputChange, handleSubmit } = useChat();

return (
  <div className="min-h-screen bg-white">
    <div className="mx-auto w-full max-w-2xl py-8 px-4">
      <div className="space-y-4 mb-4">
        {messages.map(m => (
          <div 
            key={m.id} 
            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`
                max-w-[80%] rounded-lg px-4 py-2
                ${m.role === 'user' 
                  ? 'bg-blue-100 text-black' 
                  : 'bg-gray-100 text-black'}
              `}
            >
              <div className="text-xs text-gray-500 mb-1">
                {m.role === 'user' ? 'You' : 'Llama3.3.70B powered by Groq'}
              </div>
              <div className="text-sm whitespace-pre-wrap">
                {m.content}
              </div>
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-4">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-[#f55036]"
        />
        <button 
          type="submit"
          className="rounded-lg bg-[#f55036] px-4 py-2 text-white hover:bg-[#d94530] focus:outline-none focus:ring-2 focus:ring-[#f55036]"
        >
          Send
        </button>
      </form>
    </div>
  </div>
);
```

####7. Run your development enviornment to test our application locally:
```bash
npm run dev
```

####8. Easily deploy your application using Vercel CLI by installing `vercel` and then running the `vercel` command:

The CLI will guide you through a few simple prompts:
- If this is your first time using Vercel CLI, you'll be asked to create an account or log in
- Choose to link to an existing Vercel project or create a new one
- Confirm your deployment settings 

Once you've gone through the prompts, your app will be deployed instantly and you'll receive a production URL! 🚀
```bash
npm install -g vercel
vercel
```

### Additional Resources

For more details on integrating Groq with the Vercel AI SDK, see the following:
- [Official Documentation: Vercel](https://sdk.vercel.ai/providers/ai-sdk-providers/groq)
- [Vercel Templates for Groq](https://sdk.vercel.ai/providers/ai-sdk-providers/groq)

---

## E2B + Groq: Open-Source Code Interpreter

URL: https://console.groq.com/docs/e2b

## E2B + Groq: Open-Source Code Interpreter

[E2B](https://e2b.dev/) Code Interpreter is an open-source SDK that provides secure, sandboxed environments for executing code generated by LLMs via Groq API. Built specifically for AI data analysts, 
coding applications, and reasoning-heavy agents, E2B enables you to both generate and execute code in a secure sandbox environment in real-time.

### Python Quick Start (3 minutes to hello world)

####1. Install the required packages:
```bash
pip install groq e2b-code-interpreter python-dotenv
```

####2. Configure your Groq and [E2B](https://e2b.dev/docs) API keys:
```bash
export GROQ_API_KEY="your-groq-api-key"
export E2B_API_KEY="your-e2b-api-key"
```

####3. Create your first simple and fast Code Interpreter application that generates and executes code to analyze data:

Running the below code will create a secure sandbox environment, generate Python code using `llama-3.3-70b-versatile` powered by Groq, execute the code, and display the results. When you go to your 
[E2B Dashboard](https://e2b.dev/dashboard), you'll see your sandbox's data. 

```python
from e2b_code_interpreter import Sandbox
from groq import Groq
import os

e2b_api_key = os.environ.get('E2B_API_KEY')
groq_api_key = os.environ.get('GROQ_API_KEY')

# Initialize Groq client
client = Groq(api_key=groq_api_key)

SYSTEM_PROMPT = """You are a Python data scientist. Generate simple code that:
1. Uses numpy to generate5 random numbers
2. Prints only the mean and standard deviation in a clean format
Example output format:
Mean:5.2
Std Dev:1.8"""

def main():
 # Create sandbox instance (by default, sandbox instances stay alive for5 mins)
 sbx = Sandbox()
    
 # Get code from Groq
 response = client.chat.completions.create(
 model="llama-3.1-70b-versatile",
 messages=[
 {"role": "system", "content": SYSTEM_PROMPT},
 {"role": "user", "content": "Generate random numbers and show their mean and standard deviation"}
 ]
 )
    
 # Extract and run the code
 code = response.choices[0].message.content
 if "```python" in code:
 code = code.split("```python")[1].split("```")[0]
    
 print("\nGenerated Python code:")
 print(code)
    
 print("\nExecuting code in sandbox...")
 execution = sbx.run_code(code)
 print(execution.logs.stdout[0])
    
if __name__ == "__main__":
 main()
```

**Challenge**: Try modifying the example to analyze your own dataset or solve a different data science problem!

For more detailed documentation and resources on building with E2B and Groq, see:
- [Tutorial: Code Interpreting with Groq (Python)](https://e2b.dev/blog/guide-code-interpreting-with-groq-and-e2b)
- [Tutorial: Code Interpreting with Groq (JavaScript)](https://e2b.dev/blog/guide-groq-js)

---

## 🚅 LiteLLM + Groq for Production Deployments

URL: https://console.groq.com/docs/litellm

## 🚅 LiteLLM + Groq for Production Deployments

[LiteLLM](https://docs.litellm.ai/docs/) provides a simple framework with features to help productionize your application infrastructure, including:

- **Cost Management:** Track spending, set budgets, and implement rate limiting for optimal resource utilization
- **Smart Caching:** Cache frequent responses to reduce API calls while maintaining Groq's speed advantage
- **Spend Tracking:** Track spend for individual API keys, users, and teams

### Quick Start (2 minutes to hello world)

####1. Install the package:
```bash
pip install litellm
```

####2. Set up your API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

####3. Send your first request:
```python
import os
import litellm

api_key = os.environ.get('GROQ_API_KEY')


response = litellm.completion(
 model="groq/llama-3.3-70b-versatile", 
 messages=[
 {"role": "user", "content": "hello from litellm"}
 ],
)
print(response)
```


### Next Steps
For detailed setup of advanced features:
- [Configuration of Spend Tracking for Keys, Users, and Teams](https://docs.litellm.ai/docs/proxy/cost_tracking)
- [Configuration for Budgets and Rate Limits](https://docs.litellm.ai/docs/proxy/users)

For more information on building production-ready applications with LiteLLM and Groq, see:
- [Official Documentation: LiteLLM](https://docs.litellm.ai/docs/providers/groq)
- [Tutorial: Groq API Cookbook](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/litellm-proxy-groq)

---

## AutoGen + Groq: Building Multi-Agent AI Applications

URL: https://console.groq.com/docs/autogen

## AutoGen + Groq: Building Multi-Agent AI Applications

[AutoGen](https://microsoft.github.io/autogen/) developed by [Microsoft Research](https://www.microsoft.com/research/) is an open-source framework for building multi-agent AI applications. By powering the
AutoGen agentic framework with Groq's fast inference speed, you can create sophisticated AI agents that work together to solve complex tasks fast with features including:

- **Multi-Agent Orchestration:** Create and manage multiple agents that can collaborate in realtime
- **Tool Integration:** Easily connect agents with external tools and APIs
- **Flexible Workflows:** Support both autonomous and human-in-the-loop conversation patterns
- **Code Generation & Execution:** Enable agents to write, review, and execute code safely


### Python Quick Start (3 minutes to hello world)
####1. Install the required packages:
```bash
pip install autogen-agentchat~=0.2 groq
```

####2. Configure your Groq API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

####3. Create your first multi-agent application with Groq:
In AutoGen, **agents** are autonomous entities that can engage in conversations and perform tasks. The example below shows how to create a simple two-agent system with `llama-3.3-70b-versatile` where
`UserProxyAgent` initiates the conversation with a question and `AssistantAgent` responds:

```python
import os
from autogen import AssistantAgent, UserProxyAgent

# Configure
config_list = [{
 "model": "llama-3.3-70b-versatile",
 "api_key": os.environ.get("GROQ_API_KEY"),
 "api_type": "groq"
}]

# Create an AI assistant
assistant = AssistantAgent(
 name="groq_assistant",
 system_message="You are a helpful AI assistant.",
 llm_config={"config_list": config_list}
)

# Create a user proxy agent (no code execution in this example)
user_proxy = UserProxyAgent(
 name="user_proxy",
 code_execution_config=False
)

# Start a conversation between the agents
user_proxy.initiate_chat(
 assistant,
 message="What are the key benefits of using Groq for AI apps?"
)
```


### Advanced Features

#### Code Generation and Execution
You can enable secure code execution by configuring the `UserProxyAgent` that allows your agents to write and execute Python code in a controlled environment:
```python
from pathlib import Path
from autogen.coding import LocalCommandLineCodeExecutor

# Create a directory to store code files
work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# Configure the UserProxyAgent with code execution
user_proxy = UserProxyAgent(
 name="user_proxy",
 code_execution_config={"executor": code_executor}
)
```

#### Tool Integration
You can add tools for your agents to use by creating a function and registering it with the assistant. Here's an example of a weather forecast tool:
```python
from typing import Annotated

def get_current_weather(location, unit="fahrenheit"):
 """Get the weather for some location"""
 weather_data = {
 "berlin": {"temperature": "13"},
 "istanbul": {"temperature": "40"},
 "san francisco": {"temperature": "55"}
 }
    
 location_lower = location.lower()
 if location_lower in weather_data:
 return json.dumps({
 "location": location.title(),
 "temperature": weather_data[location_lower]["temperature"],
 "unit": unit
 })
 return json.dumps({"location": location, "temperature": "unknown"})

# Register the tool with the assistant
@assistant.register_for_llm(description="Weather forecast for cities.")
def weather_forecast(
 location: Annotated[str, "City name"],
 unit: Annotated[str, "Temperature unit (fahrenheit/celsius)"] = "fahrenheit"
) -> str:
 weather_details = get_current_weather(location=location, unit=unit)
 weather = json.loads(weather_details)
 return f"{weather['location']} will be {weather['temperature']} degrees {weather['unit']}"
```

#### Complete Code Example
Here is our quick start agent code example combined with code execution and tool use that you can play with:
```python
import os
import json
from pathlib import Path
from typing import Annotated
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

# Configure Groq
config_list = [{
 "model": "llama-3.3-70b-versatile",
 "api_key": os.environ.get("GROQ_API_KEY"),
 "api_type": "groq"
}]

# Create a directory to store code files from code executor
work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)
code_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# Define weather tool
def get_current_weather(location, unit="fahrenheit"):
 """Get the weather for some location"""
 weather_data = {
 "berlin": {"temperature": "13"},
 "istanbul": {"temperature": "40"},
 "san francisco": {"temperature": "55"}
 }
    
 location_lower = location.lower()
 if location_lower in weather_data:
 return json.dumps({
 "location": location.title(),
 "temperature": weather_data[location_lower]["temperature"],
 "unit": unit
 })
 return json.dumps({"location": location, "temperature": "unknown"})

# Create an AI assistant that uses the weather tool
assistant = AssistantAgent(
 name="groq_assistant",
 system_message="""You are a helpful AI assistant who can:
 - Use weather information tools
 - Write Python code for data visualization
 - Analyze and explain results""",
 llm_config={"config_list": config_list}
)

# Register weather tool with the assistant
@assistant.register_for_llm(description="Weather forecast for cities.")
def weather_forecast(
 location: Annotated[str, "City name"],
 unit: Annotated[str, "Temperature unit (fahrenheit/celsius)"] = "fahrenheit"
) -> str:
 weather_details = get_current_weather(location=location, unit=unit)
 weather = json.loads(weather_details)
 return f"{weather['location']} will be {weather['temperature']} degrees {weather['unit']}"

# Create a user proxy agent that only handles code execution
user_proxy = UserProxyAgent(
 name="user_proxy",
 code_execution_config={"executor": code_executor}
)

# Start the conversation
user_proxy.initiate_chat(
 assistant,
 message="""Let's do two things:
1. Get the weather for Berlin, Istanbul, and San Francisco
2. Write a Python script to create a bar chart comparing their temperatures"""
)
```


**Challenge:** Add to the above example and create a multi-agent [`GroupChat`](https://microsoft.github.io/autogen/0.2/docs/topics/groupchat/customized_speaker_selection) workflow!


For more detailed documentation and resources on building agentic applications with Groq and AutoGen, see:
- [AutoGen Documentation](https://microsoft.github.io/autogen/0.2/docs/topics/non-openai-models/cloud-groq/)
- [AutoGroq](https://github.com/jgravelle/AutoGroq)

---

## OpenAI Compatibility

URL: https://console.groq.com/docs/openai

## OpenAI Compatibility

We designed Groq API to be mostly compatible with OpenAI's client libraries, making it easy to 
configure your existing applications to run on Groq and try our inference speed.

We also have our own [Groq Python and Groq TypeScript libraries](/docs/libraries) that we encourage you to use.

### Configuring OpenAI to Use Groq API
To start using Groq with OpenAI's client libraries, pass your Groq API key to the `api_key` parameter
and change the `base_url` to `https://api.groq.com/openai/v1`:


You can find your API key [here](/keys). 

### Currently Unsupported OpenAI Features

Note that although Groq API is mostly OpenAI compatible, there are a few features we don't support just yet: 

#### Text Completions
The following fields are currently not supported and will result in a400 error (yikes) if they are supplied:
- `logprobs`

- `logit_bias`

- `top_logprobs`

- `messages[].name`

- If `N` is supplied, it must be equal to1.

#### Temperature
If you set a `temperature` value of0, it will be converted to `1e-8`. If you run into any issues, please try setting the value to a float32 `>0` and `<=2`.

#### Audio Transcription and Translation
The following values are not supported:
- `vtt`
- `srt`

### Feedback
If you'd like to see support for such features as the above on Groq API, please reach out to us and let us know by submitting a "Feature Request" via "Chat with us" located on the left. We really value your feedback and would love to hear from you!

---

## JigsawStack 🧩

URL: https://console.groq.com/docs/jigsawstack

## JigsawStack 🧩

<br />

[JigsawStack](https://jigsawstack.com/) is a powerful AI SDK designed to integrate into any backend, automating tasks such as web scraping, Optical Character Recognition (OCR), translation, and more, using 
Large Language Models (LLMs). By plugging JigsawStack into your existing application infrastructure, you can offload the heavy lifting and focus on building.

The [JigsawStack Prompt Engine]() is a feature that allows you to not only leverage LLMs but automatically choose the best LLM for every one of your prompts, delivering lightning-fast inference speed and performance
powered by Groq with features including:

- **Mixture-of-Agents (MoA) Approach:** Automatically selects the best LLMs for your task, combining outputs for higher quality and faster results.
- **Prompt Caching:** Optimizes performance for repeated prompt runs.
- **Automatic Prompt Optimization:** Improves performance without manual intervention.
- **Response Schema Validation:** Ensures accuracy and consistency in outputs.

The Propt Engine also comes with a built-in prompt guard feature via Llama Guard3 powered by Groq, which helps prevent prompt injection and a wide range of unsafe categories when activated, such as:
- Privacy Protection
- Hate Speech Filtering
- Sexual Content Blocking
- Election Misinformation Prevention
- Code Interpreter Abuse Protection
- Unauthorized Professional Advice Prevention

<br />

To get started, refer to the JigsawStack documentation [here](https://docs.jigsawstack.com/integration/groq) and learn how to set up your Prompt 
Engine [here](https://github.com/groq/groq-api-cookbook/tree/main/tutorials/jigsawstack-prompt-engine).

---

## Api Reference: Batches Read Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/batches-read-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const batch = await client.batches.retrieve("batch_01jh6xa7reempvjyh6n3yst2zw");
  console.log(batch.id);
}

main();

---

## Api Reference: Library Usage Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-response.json

There is no code to clean. The provided content appears to be a JSON object and does not contain any code that needs to be preserved or cleaned. 

However, if you provide a script file with React component tags, I can assist with cleaning it according to the specified guidelines.

---

## Api Reference: Files Delete Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/files-delete-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const fileDelete = await client.files.delete("file_01jh6x76wtemjr74t1fh0faj5t");
  console.log(fileDelete);
}

main();

---

## Api Reference: Models List Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/models-list-response.json

```
{
 "object": "list",
 "data": [
 {
 "id": "gemma2-9b-it",
 "object": "model",
 "created":1693721698,
 "owned_by": "Google",
 "active": true,
 "context_window":8192,
 "public_apps": null
 },
 {
 "id": "llama3-8b-8192",
 "object": "model",
 "created":1693721698,
 "owned_by": "Meta",
 "active": true,
 "context_window":8192,
 "public_apps": null
 },
 {
 "id": "llama3-70b-8192",
 "object": "model",
 "created":1693721698,
 "owned_by": "Meta",
 "active": true,
 "context_window":8192,
 "public_apps": null
 },
 {
 "id": "whisper-large-v3-turbo",
 "object": "model",
 "created":1728413088,
 "owned_by": "OpenAI",
 "active": true,
 "context_window":448,
 "public_apps": null
 },
 {
 "id": "whisper-large-v3",
 "object": "model",
 "created":1693721698,
 "owned_by": "OpenAI",
 "active": true,
 "context_window":448,
 "public_apps": null
 },
 {
 "id": "llama-guard-3-8b",
 "object": "model",
 "created":1693721698,
 "owned_by": "Meta",
 "active": true,
 "context_window":8192,
 "public_apps": null
 },
 {
 "id": "distil-whisper-large-v3-en",
 "object": "model",
 "created":1693721698,
 "owned_by": "Hugging Face",
 "active": true,
 "context_window":448,
 "public_apps": null
 },
 {
 "id": "llama-3.1-8b-instant",
 "object": "model",
 "created":1693721698,
 "owned_by": "Meta",
 "active": true,
 "context_window":131072,
 "public_apps": null
 }
 ]
}
```

---

## Api Reference: Library Usage Image Input (js)

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-image-input

// Image input
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
  const completion = await groq.chat.completions
    .create({
      messages: [
        {
          role: "user",
          content: "Explain the importance of fast language models",
        },
      ],
      model: "mixtral-8x7b-32768",
    })
    .then((chatCompletion) => {
      console.log(chatCompletion.choices[0]?.message?.content || "");
    });
}

main();

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/files-list-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
file_list = client.files.list()
print(file_list.data)
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/batches-create-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
batch = client.batches.create(
 completion_window="24h",
 endpoint="/v1/chat/completions",
 input_file_id="file_01jh6x76wtemjr74t1fh0faj5t",
)
print(batch.id)
```

---

## Api Reference: Library Speech Request (py)

URL: https://console.groq.com/docs/api-reference/scripts/library-speech-request.py

```python
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

speech_file_path = "speech.wav" 
model = "playai-tts"
voice = "Fritz-PlayAI"
text = "I love building and shipping new features for our users!"
response_format = "wav"

response = client.audio.speech.create(
 model=model,
 voice=voice,
 input=text,
 response_format=response_format
)

response.write_to_file(speech_file_path)
```

---

## Api Reference: Library Transcription Default (js)

URL: https://console.groq.com/docs/api-reference/scripts/library-transcription-default

import fs from "fs";
import Groq from "groq-sdk";

const groq = new Groq();
async function main() {
 const transcription = await groq.audio.transcriptions.create({
 file: fs.createReadStream("sample_audio.m4a"),
 model: "whisper-large-v3",
 prompt: "Specify context or spelling", // Optional
 response_format: "json", // Optional
 language: "en", // Optional
 temperature:0.0, // Optional
 });
 console.log(transcription.text);
}
main();

---

## Api Reference: Files Download Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/files-download-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const response = await client.files.content('file_01jh6x76wtemjr74t1fh0faj5t');
  console.log(response);
}

main();

---

## Api Reference: Files Upload Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/files-upload-request.curl

```bash
curl https://api.groq.com/openai/v1/files \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -F purpose="batch" \
 -F "file=@batch_file.jsonl"
```

---

## Api Reference: Model Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/model-request.curl

```bash
curl https://api.groq.com/openai/v1/models/llama-3.3-70b-versatile \
-H "Authorization: Bearer $GROQ_API_KEY"
```

---

## Api Reference: Files List Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/files-list-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const fileList = await client.files.list();
  console.log(fileList.data);
}

main();

---

## Api Reference: Files List Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/files-list-response.json

{
 "object": "list",
 "data": [
 {
 "id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "object": "file",
 "bytes":966,
 "created_at":1736472501,
 "filename": "batch_file.jsonl",
 "purpose": "batch"
 }
 ]
}

---

## Image input

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-image-input.py

# Image input
import os

from groq import Groq

client = Groq(
 # This is the default and can be omitted
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant."
 },
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],
 model="mixtral-8x7b-32768",
)

print(chat_completion.choices[0].message.content)

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/files-delete-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
file_delete = client.files.delete(
 "file_01jh6x76wtemjr74t1fh0faj5t",
)
print(file_delete)
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/batches-read-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
batch = client.batches.retrieve(
 "batch_01jh6xa7reempvjyh6n3yst2zw",
)
print(batch.id)
```

---

## Api Reference: Library Transcription Default (curl)

URL: https://console.groq.com/docs/api-reference/scripts/library-transcription-default.curl

```bash
curl https://api.groq.com/openai/v1/audio/transcriptions \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: multipart/form-data" \
 -F file="@./sample_audio.m4a" \
 -F model="whisper-large-v3"
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/files-download-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
response = client.files.content(
 "file_01jh6x76wtemjr74t1fh0faj5t",
)
print(response)
```

---

## Api Reference: Files Download Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/files-download-request.curl

```bash
curl https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t/content \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Optional

URL: https://console.groq.com/docs/api-reference/scripts/library-transcription-default.py

```python
import os
from groq import Groq

client = Groq()
filename = os.path.dirname(__file__) + "/sample_audio.m4a"

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(filename, file.read()),
        model="whisper-large-v3",
        prompt="Specify context or spelling", # Optional
        response_format="json", # Optional
        language="en", # Optional
        temperature=0.0 # Optional
    )
print(transcription.text)
```

---

## Api Reference: Library Speech Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/library-speech-request

import fs from "fs";
import path from "path";
import Groq from 'groq-sdk';

const groq = new Groq({
 apiKey: process.env.GROQ_API_KEY
});

const speechFilePath = "speech.wav";
const model = "playai-tts";
const voice = "Fritz-PlayAI";
const text = "I love building and shipping new features for our users!";
const responseFormat = "wav";

async function main() {
 const response = await groq.audio.speech.create({
 model: model,
 voice: voice,
 input: text,
 response_format: responseFormat
 });
  
 const buffer = Buffer.from(await response.arrayBuffer());
 await fs.promises.writeFile(speechFilePath, buffer);
}

main();

---

## Api Reference: Batches Create Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/batches-create-request.curl

The provided content is not a script file or code documentation that contains React component tags or code structure that needs cleaning according to the provided guidelines. It appears to be a curl command example for an API request.

However, to adhere strictly to the instructions and given that there's no code to clean in terms of React components or script files, the response will simply be the content itself as it does not contain any React-specific component tags or code structure that needs to be cleaned:

```bash
curl https://api.groq.com/openai/v1/batches \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "endpoint": "/v1/chat/completions",
 "completion_window": "24h"
 }'
```

---

## Api Reference: Batches Create Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/batches-create-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const batch = await client.batches.create({
    completion_window: "24h",
    endpoint: "/v1/chat/completions",
    input_file_id: "file_01jh6x76wtemjr74t1fh0faj5t",
  });
  console.log(batch.id);
}

main();

---

## Api Reference: Models List Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/models-list-request.curl

```bash
curl https://api.groq.com/openai/v1/models \
-H "Authorization: Bearer $GROQ_API_KEY"
```

---

## Api Reference: Library Usage Default (js)

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-default

```javascript
import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
  const completion = await groq.chat.completions
    .create({
      messages: [
        {
          role: "user",
          content: "Explain the importance of fast language models",
        },
      ],
      model: "llama-3.3-70b-versatile",
    })
  console.log(completion.choices[0].message.content);
}

main();
```

---

## Api Reference: Library Translation Default (curl)

URL: https://console.groq.com/docs/api-reference/scripts/library-translation-default.curl

```bash
curl https://api.groq.com/openai/v1/audio/translations \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: multipart/form-data" \
 -F file="@./sample_audio.m4a" \
 -F model="whisper-large-v3"
```

---

## Default

URL: https://console.groq.com/docs/api-reference/scripts/library-translation-default.py

# Default
import os
from groq import Groq

client = Groq()
filename = os.path.dirname(__file__) + "/sample_audio.m4a"

with open(filename, "rb") as file:
    translation = client.audio.translations.create(
        file=(filename, file.read()),
        model="whisper-large-v3",
        prompt="Specify context or spelling", # Optional
        response_format="json", # Optional
        temperature=0.0 # Optional
    )
    print(translation.text)

---

## Api Reference: Library Transcription Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/library-transcription-response.json

```
{
  "text": "Your transcribed text appears here...",
  "x_groq": {
    "id": "req_unique_id"
  }
}
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/files-read-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
file = client.files.info(
 "file_01jh6x76wtemjr74t1fh0faj5t",
)
print(file)
```

---

## Api Reference: Model Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/model-request

import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
 const model = await groq.models.retrieve("llama-3.3-70b-versatile");
 console.log(model);
}

main();

---

## Api Reference: Files Read Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/files-read-request.curl

```bash
curl https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Api Reference: Model Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/model-response.json

{
 "id": "llama3-8b-8192",
 "object": "model",
 "created":1693721698,
 "owned_by": "Meta",
 "active": true,
 "context_window":8192,
 "public_apps": null
}

---

## pip install requests first!

URL: https://console.groq.com/docs/api-reference/scripts/files-upload-request.py

```python
import os
import requests # pip install requests first!

def upload_file_to_groq(api_key, file_path):
 url = "https://api.groq.com/openai/v1/files"
    
 headers = {
 "Authorization": f"Bearer {api_key}"
 }
    
 # Prepare the file and form data
 files = {
 "file": ("batch_file.jsonl", open(file_path, "rb"))
 }
    
 data = {
 "purpose": "batch"
 }
    
 # Make the POST request
 response = requests.post(url, headers=headers, files=files, data=data)
    
 return response.json()

# Usage example
api_key = os.environ.get("GROQ_API_KEY")
file_path = "batch_file.jsonl" # Path to your JSONL file

try:
 result = upload_file_to_groq(api_key, file_path)
 print(result)
except Exception as e:
 print(f"Error: {e}")
```

---

## Api Reference: Batches List Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/batches-list-request.curl

```bash
curl https://api.groq.com/openai/v1/batches \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Api Reference: Models List Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/models-list-request

import Groq from "groq-sdk";

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

async function main() {
 const models = await groq.models.list();
 console.log(models);
}

main();

---

## Api Reference: Batches List Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/batches-list-response.json

{
 "object": "list",
 "data": [
 {
 "id": "batch_01jh6xa7reempvjyh6n3yst2zw",
 "object": "batch",
 "endpoint": "/v1/chat/completions",
 "errors": null,
 "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "completion_window": "24h",
 "status": "validating",
 "output_file_id": null,
 "error_file_id": null,
 "finalizing_at": null,
 "failed_at": null,
 "expired_at": null,
 "cancelled_at": null,
 "request_counts": {
 "total":0,
 "completed":0,
 "failed":0
 },
 "metadata": null,
 "created_at":1736472600,
 "expires_at":1736559000,
 "cancelling_at": null,
 "completed_at": null,
 "in_progress_at": null
 }
 ]
}

---

## Api Reference: Batches List Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/batches-list-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const batchList = await client.batches.list();
  console.log(batchList.data);
}

main();

---

## Api Reference: Batches Create Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/batches-create-response.json

The provided content does not appear to be a script or code file that requires cleaning, but rather a JSON object. However, based on the instructions to preserve all code and only remove React-specific component tags if present, and given that there are no React component tags or code structure to maintain, the content remains as is:


{
 "id": "batch_01jh6xa7reempvjyh6n3yst2zw",
 "object": "batch",
 "endpoint": "/v1/chat/completions",
 "errors": null,
 "input_file_id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "completion_window": "24h",
 "status": "validating",
 "output_file_id": null,
 "error_file_id": null,
 "finalizing_at": null,
 "failed_at": null,
 "expired_at": null,
 "cancelled_at": null,
 "request_counts": {
 "total":0,
 "completed":0,
 "failed":0
 },
 "metadata": null,
 "created_at":1736472600,
 "expires_at":1736559000,
 "cancelling_at": null,
 "completed_at": null,
 "in_progress_at": null
}

---

## Api Reference: Library Speech Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/library-speech-request.curl

```bash
curl https://api.groq.com/openai/v1/audio/speech \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "model": "playai-tts",
 "input": "I love building and shipping new features for our users!",
 "voice": "Fritz-PlayAI",
 "response_format": "wav"
 }'
```

---

## Api Reference: Library Translation Default (js)

URL: https://console.groq.com/docs/api-reference/scripts/library-translation-default

```javascript
// Default
import fs from "fs";
import Groq from "groq-sdk";

const groq = new Groq();
async function main() {
  const translation = await groq.audio.translations.create({
    file: fs.createReadStream("sample_audio.m4a"),
    model: "whisper-large-v3",
    prompt: "Specify context or spelling", // Optional
    response_format: "json", // Optional
    temperature:0.0, // Optional
  });
  console.log(translation.text);
}
main();
```

---

## Api Reference: Batches Read Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/batches-read-request.curl

```bash
curl https://api.groq.com/openai/v1/batches/batch_01jh6xa7reempvjyh6n3yst2zw \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Api Reference: Files Delete Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/files-delete-request.curl

```bash
curl -X DELETE https://api.groq.com/openai/v1/files/file_01jh6x76wtemjr74t1fh0faj5t \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Api Reference: Files List Request (curl)

URL: https://console.groq.com/docs/api-reference/scripts/files-list-request.curl

```bash
curl https://api.groq.com/openai/v1/files \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json"
```

---

## Api Reference: Library Usage Default (curl)

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-default.curl

```bash
curl https://api.groq.com/openai/v1/chat/completions -s \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $GROQ_API_KEY" \
-d '{
"model": "llama-3.3-70b-versatile",
"messages": [{
 "role": "user",
 "content": "Explain the importance of fast language models"
}]
}'
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/library-usage-default.py

```python
import os

from groq import Groq

client = Groq(
 # This is the default and can be omitted
 api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
 messages=[
 {
 "role": "system",
 "content": "You are a helpful assistant."
 },
 {
 "role": "user",
 "content": "Explain the importance of fast language models",
 }
 ],
 model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/models-list-request.py

```python
import os
from groq import Groq

client = Groq(
 # This is the default and can be omitted
 api_key=os.environ.get("GROQ_API_KEY"),
)

models = client.models.list()

print(models)
```

---

## Api Reference: Files Upload Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/files-upload-request

```javascript
import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

const fileContent = '{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "Explain the importance of fast language models"}]}}\n';

async function main() {
  const blob = new Blob([fileContent]);
  const file = new File([blob], 'batch.jsonl');

  const createdFile = await client.files.create({ file: file, purpose: 'batch' });
  console.log(createdFile.id);
}

main();
```

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/batches-list-request.py

```python
import os
from groq import Groq

client = Groq(
 api_key=os.environ.get("GROQ_API_KEY"), # This is the default and can be omitted
)
batch_list = client.batches.list()
print(batch_list.data)
```

---

## Api Reference: Library Translation Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/library-translation-response.json

{
 "text": "Your translated text appears here...",
 "x_groq": {
 "id": "req_unique_id"
 }
}

---

## Api Reference: Files Upload Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/files-upload-response.json

{
 "id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "object": "file",
 "bytes":966,
 "created_at":1736472501,
 "filename": "batch_file.jsonl",
 "purpose": "batch"
}

---

## Api Reference: Files Delete Response (json)

URL: https://console.groq.com/docs/api-reference/scripts/files-delete-response.json

{
 "id": "file_01jh6x76wtemjr74t1fh0faj5t",
 "object": "file",
 "deleted": true
}

---

## This is the default and can be omitted

URL: https://console.groq.com/docs/api-reference/scripts/model-request.py

```python
import os
from groq import Groq

client = Groq(
 # This is the default and can be omitted
 api_key=os.environ.get("GROQ_API_KEY"),
)

model = client.models.retrieve("llama-3.3-70b-versatile")

print(model)
```

---

## Api Reference: Files Read Request (js)

URL: https://console.groq.com/docs/api-reference/scripts/files-read-request

import Groq from 'groq-sdk';

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'], // This is the default and can be omitted
});

async function main() {
  const file = await client.files.info('file_01jh6x76wtemjr74t1fh0faj5t');
  console.log(file);
}

main();

---

## Groq API Reference

URL: https://console.groq.com/docs/api-reference

## Groq API Reference

---

## Hooks: Use Extended Models (ts)

URL: https://console.groq.com/docs/hooks/use-extended-models

import { ENV_VARS } from "@/shared/env";
import { useCachedRequest } from "@/shared/hooks/use-cached-request";
import { z } from "zod";

// Define the ServiceTier enum
const ServiceTierEnum = z.enum(["auto", "on_demand", "flex", "batch"]);

// Define ModelFeatures schema
const ModelFeaturesSchema = z.object({
  chat: z.boolean(),
  tools: z.boolean(),
  json_mode: z.boolean(),
  max_input_images: z.number(),
  transcription: z.boolean(),
  audio_translation: z.boolean(),
  is_batch_enabled: z.boolean(),
});

// Define ModelPrice schema
const ModelPriceSchema = z.object({
  model: z.string(),
  price_in_tokens: z.number().nullable(),
  price_out_tokens: z.number().nullable(),
  price_audio_in_seconds: z.number().nullable(),
  price_in_image_tokens: z.number().nullable(),
  service_tier: ServiceTierEnum,
  audio_in_seconds_floor: z.number().nullable(),
});

// Define ModelMetadata schema
const ModelMetadataSchema = z.object({
  model_card: z.string().optional(),
  display_name: z.string(),
  audio_transcription_languages: z.array(z.string()).optional(),
  audio_translation_languages: z.array(z.string()).optional(),
  image_max_bytes: z.number().optional(),
  audio_max_bytes: z.number().optional(),
  model_price: z.record(ServiceTierEnum, ModelPriceSchema).optional(),
  limits: z
    .object({
      requests_per_minute: z.number().optional(),
      requests_per_day: z.number().optional(),
      tokens_per_minute: z.number().optional(),
      audio_seconds_per_hour: z.number().optional(),
      audio_seconds_per_day: z.number().optional(),
      tokens_per_day: z.number().optional(),
      max_file_size: z.number().optional(),
    })
    .optional(),
});

// Define OAIModel schema based on the Go struct
const OAIModelSchema = z.object({
  id: z.string(),
  object: z.string(),
  created: z.number(),
  owned_by: z.string(),
  active: z.boolean(),
  context_window: z.number(),
  public_apps: z.array(z.string()),
  max_completion_tokens: z.number(),
});

// Define ExtendedModel schema
export const ExtendedModelSchema = z.object({
  ...OAIModelSchema.shape,
  features: ModelFeaturesSchema,
  metadata: ModelMetadataSchema,
  terms_url: z.string().nullable(),
  is_terms_required: z.boolean(),
  is_terms_accepted: z.boolean().nullable(),
});

// TypeScript type for ExtendedModel
export type ExtendedModel = z.infer<typeof ExtendedModelSchema>;

export const ExtendedModelResponseSchema = z.object({
  type: z.literal("list"),
  data: z.array(ExtendedModelSchema),
});

export type ExtendedModelResponse = z.infer<typeof ExtendedModelResponseSchema>;

export const isText2TextModel = (model: ExtendedModel) => {
  return model.features.chat;
};

export const isSpeech2TextModel = (model: ExtendedModel) => {
  return model.features.audio_translation || model.features.transcription;
};

export const isText2SpeechModel = (model: ExtendedModel) => {
  return model.id.includes("-tts");
};

export const useExtendedModelsDev = () => {
  const res = useCachedRequest<ExtendedModelResponse>({
    url: `${ENV_VARS.BASE_API_URL}/public/v1/models/dev`,
  });

  return res;
};

export const useExtendedModelsFree = () => {
  const res = useCachedRequest<ExtendedModelResponse>({
    url: `${ENV_VARS.BASE_API_URL}/public/v1/models/free`,
  });

  return res;
};

---

## Script: Types.d (ts)

URL: https://console.groq.com/docs/scripts/types.d

declare module "*.sh" {
  const content: string;
  export default content;
}

---

## Script: Code Examples (ts)

URL: https://console.groq.com/docs/scripts/code-examples

```
export const getExampleCode = (modelId: string) => ({
  shell: `curl https://api.groq.com/v1/chat/completions \\
 -H "Authorization: Bearer $GROQ_API_KEY" \\
 -H "Content-Type: application/json" \\
 -d '{
 "model": "${modelId}",
 "messages": [
 {
 "role": "user",
 "content": "Explain why fast inference is critical for reasoning models"
 }
 ]
 }'`,

  javascript: `import Groq from "groq-sdk";
const groq = new Groq();
async function main() {
  const completion = await groq.chat.completions.create({
    model: "${modelId}",
    messages: [
      {
        role: "user",
        content: "Explain why fast inference is critical for reasoning models",
      },
    ],
  });
  console.log(completion.choices[0]?.message?.content);
}
main().catch(console.error);`,

  python: `from groq import Groq
client = Groq()
completion = client.chat.completions.create(
  model="${modelId}",
  messages=[
    {
      "role": "user",
      "content": "Explain why fast inference is critical for reasoning models"
    }
  ]
)
print(completion.choices[0].message.content)`,

  json: `{
 "model": "${modelId}",
 "messages": [
 {
 "role": "user", 
 "content": "Explain why fast inference is critical for reasoning models"
 }
 ]
}`,
}); 
```

---
