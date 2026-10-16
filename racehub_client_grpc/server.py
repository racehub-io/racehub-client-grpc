import asyncio
import grpc
import grpc.aio
from concurrent import futures
import logging
import sys
import os
import signal as signal_module
import platform
import time
import math
import random
from typing import Dict

# Import generated protobuf code
from racehub_client_grpc import racehub_pb2
from racehub_client_grpc import racehub_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TelemetryGenerator:
    def __init__(self, recorder_id: str):
        self.recorder_id = recorder_id
        self.lap = 1
        self.lap_time = 0.0
        self.last_lap_time = 0.0
        self.track_position = 0.0  # 0.0 to 1.0 representing position on track
        self.sectors = ["Sector 1", "Sector 2", "Sector 3"]
        self.current_sector = self.sectors[0]

    async def generate_telemetry(self) -> racehub_pb2.TelemetryData:
        # Update track position (simulate car moving around track)
        self.track_position += 0.001
        if self.track_position >= 1.0:
            self.track_position = 0.0
            self.last_lap_time = self.lap_time
            self.lap_time = 0.0
            self.lap += 1

        # Update lap time
        self.lap_time += 0.1

        # Update sector based on track position
        sector_index = int(self.track_position * 3)
        self.current_sector = self.sectors[min(sector_index, 2)]

        # Generate dummy data with some variation
        speed = (
            250 + math.sin(self.track_position * 2 * math.pi) * 50
        )  # Speed varies between 200-300 km/h
        rpm = (
            10000 + math.sin(self.track_position * 4 * math.pi) * 2000
        )  # RPM varies between 8000-12000

        # Calculate gear based on speed
        gear = max(1, min(8, int(speed / 50)))

        return racehub_pb2.TelemetryData(
            timestamp=int(time.time() * 1000),
            throttle=random.uniform(0.7, 1.0),
            brake=random.uniform(0.0, 0.3),
            steering=math.sin(self.track_position * 4 * math.pi) * 0.5,
            speed_ms=speed / 3.6,  # Convert km/h to m/s
            gear=gear,
            rpm=rpm,
            position_x=math.cos(self.track_position * 2 * math.pi) * 100,
            position_y=0,
            position_z=math.sin(self.track_position * 2 * math.pi) * 100,
            rotation_pitch=random.uniform(-2, 2),
            rotation_yaw=self.track_position * 360,
            rotation_roll=random.uniform(-1, 1),
            lateral_g=random.uniform(-3, 3),
            longitudinal_g=random.uniform(-2, 4),
            fuel_level=max(0, 100 - (self.lap_time / 2)),
            engine_temp=90 + random.uniform(-5, 5),
            drs_enabled=speed > 280,
            current_lap=self.lap,
            last_lap_time=self.last_lap_time,
            current_lap_time=self.lap_time,
            sector=self.current_sector,
        )


class RaceHubTelemetryServicer(racehub_pb2_grpc.RaceHubTelemetryServicer):
    def __init__(self):
        self.telemetry_generators: Dict[str, TelemetryGenerator] = {}

    async def StreamTelemetry(
        self, request: racehub_pb2.TelemetryRequest, context: grpc.aio.ServicerContext
    ) -> racehub_pb2.TelemetryData:
        logger.info(
            f"New telemetry stream requested for recorder: {request.recorder_id}"
        )

        # Get or create telemetry generator for this recorder
        generator = self.telemetry_generators.get(request.recorder_id)
        if not generator:
            generator = TelemetryGenerator(request.recorder_id)
            self.telemetry_generators[request.recorder_id] = generator

        try:
            while not context.done():
                telemetry = await generator.generate_telemetry()
                yield telemetry
                await asyncio.sleep(0.1)  # Send data every 100ms

        except Exception as e:
            logger.error(f"Error in telemetry stream for {request.recorder_id}: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))
        finally:
            logger.info(f"Telemetry stream ended for recorder: {request.recorder_id}")


class RaceHubServer:
    def __init__(self, port=50051):
        self.port = port
        self._shutdown_event = asyncio.Event()

    async def start(self):
        try:
            # Initialize grpc.aio
            grpc.aio.init_grpc_aio()  # This doesn't return anything to await

            # Create async server
            self.server = grpc.aio.server(
                compression=grpc.Compression.Gzip,
                options=[
                    ("grpc.max_send_message_length", 100 * 1024 * 1024),
                    ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                ],
            )

            # Add the telemetry service
            telemetry_servicer = RaceHubTelemetryServicer()
            racehub_pb2_grpc.add_RaceHubTelemetryServicer_to_server(
                telemetry_servicer, self.server
            )

            addr = f"[::]:{self.port}"
            port = self.server.add_insecure_port(addr)
            if port == 0:
                raise RuntimeError(f"Failed to bind to address {addr}")

            logger.info(f"Starting server on {addr}")
            await self.server.start()
            logger.info("Server started successfully")

            # Wait for shutdown event
            await self._shutdown_event.wait()
            await self.stop()

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            if hasattr(self, "server"):
                await self.stop()
            sys.exit(1)

    async def stop(self):
        """Gracefully stop the server"""
        if hasattr(self, "server"):
            logger.info("Stopping server...")
            try:
                await self.server.stop(grace=5.0)
                logger.info("Server stopped")
            except Exception as e:
                logger.error(f"Error during server shutdown: {e}")

    def signal_shutdown(self):
        """Signal the server to shutdown"""
        self._shutdown_event.set()


async def serve():
    server = RaceHubServer()

    if platform.system() == "Windows":
        # Windows-specific signal handling
        def handle_signal(signum, frame):
            logger.info(f"Received signal {signum}")
            server.signal_shutdown()

        signal_module.signal(signal_module.SIGINT, handle_signal)
        signal_module.signal(signal_module.SIGTERM, handle_signal)
    else:
        # Unix-style signal handling
        loop = asyncio.get_running_loop()
        for sig in [signal_module.SIGTERM, signal_module.SIGINT]:
            loop.add_signal_handler(sig, lambda s=sig: server.signal_shutdown())

    await server.start()


def main():
    asyncio.run(serve())


if __name__ == "__main__":
    main()
