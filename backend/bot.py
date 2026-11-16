
import os
from pathlib import Path

from dotenv import load_dotenv

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import (
    PipelineWorker,
    PipelineParams,
    ProcessorUnusablePolicy,
)

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)

from pipecat.runner.types import SmallWebRTCRunnerArguments
from pipecat.workers.runner import WorkerRunner

from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService

from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

from backend.agent import create_llm


# Load .env from the backend folder
load_dotenv(
    dotenv_path=Path(__file__).resolve().parent / ".env",
    override=True
)


async def run_bot(transport, runner_args):

    # 1. Speech-to-text
    stt = ElevenLabsRealtimeSTTService(
        api_key=os.environ["ELEVENLABS_API_KEY"]
    )

    # 2. Gemini
    llm = create_llm(
        api_key=os.environ["GOOGLE_API_KEY"]
    )

    # 3. Text-to-speech
    tts = ElevenLabsTTSService(
        api_key=os.environ["ELEVENLABS_API_KEY"],
        voice_id=os.environ["ELEVENLABS_VOICE_ID"],
    )

    # 4. Store conversation messages
    context = LLMContext()

    # 5. Detect when the patient stops speaking
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer()
        ),
    )

    # 6. Connect all voice components
    pipeline = Pipeline([
        transport.input(),
        stt,
        user_aggregator,
        llm,
        tts,
        transport.output(),
        assistant_aggregator,
    ])

    # 7. Create pipeline worker
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        processor_unusable_policy=ProcessorUnusablePolicy.END,
    )

    # 8. Start the worker
    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint
    )

    await runner.add_workers(worker)

    # When browser connects
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):

        print("Patient connected!")

        context.add_message({
            "role": "developer",
            "content": (
                "Greet the patient and ask how you can help "
                "with their doctor appointment."
            ),
        })

        await worker.queue_frames([LLMRunFrame()])

    # When browser disconnects
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):

        print("Patient disconnected!")

        await runner.cancel()

    await runner.run()


async def bot(runner_args: SmallWebRTCRunnerArguments):

    # Get the WebRTC connection
    webrtc_connection: SmallWebRTCConnection = (
        runner_args.webrtc_connection
    )

    # Enable microphone input and speaker output
    transport = SmallWebRTCTransport(
        webrtc_connection=webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    )

    await run_bot(transport, runner_args)


if __name__ == "__main__":

    from pipecat.runner.run import main

    main()
