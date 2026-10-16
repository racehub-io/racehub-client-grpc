import asyncio
import grpc
import logging
from datetime import datetime
from racehub_client_grpc import racehub_pb2
from racehub_client_grpc import racehub_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TelemetryClient:
    def __init__(self, address="localhost:50051"):
        self.address = address

    async def stream_telemetry(self, recorder_id: str):
        try:
            # Create channel and stub
            channel = grpc.aio.insecure_channel(self.address)
            stub = racehub_pb2_grpc.RaceHubTelemetryStub(channel)

            # Create request
            request = racehub_pb2.TelemetryRequest(recorder_id=recorder_id)

            logger.info(f"Starting telemetry stream for recorder {recorder_id}")

            # Stream telemetry data
            async for telemetry in stub.StreamTelemetry(request):
                self._display_telemetry(telemetry)

        except Exception as e:
            logger.error(f"Error in telemetry stream: {e}")
        finally:
            await channel.close()

    def _display_telemetry(self, telemetry):
        """Display telemetry data in a readable format"""
        # Convert timestamp to datetime
        dt = datetime.fromtimestamp(telemetry.timestamp / 1000)

        # Clear screen (Windows)
        print("\033[H\033[J", end="")

        # Display data in sections
        print(f"=== Telemetry Data at {dt.strftime('%H:%M:%S.%f')[:-3]} ===")

        print("\n=== Car Controls ===")
        print(f"Throttle: {telemetry.throttle:6.1%}")
        print(f"Brake:    {telemetry.brake:6.1%}")
        print(f"Steering: {telemetry.steering:6.1f}")

        print("\n=== Car State ===")
        print(f"Speed:    {telemetry.speed_ms * 3.6:6.1f} km/h")
        print(f"Gear:     {telemetry.gear:6d}")
        print(f"RPM:      {telemetry.rpm:6.0f}")
        print(f"DRS:      {'ENABLED' if telemetry.drs_enabled else 'DISABLED'}")

        print("\n=== Position & Orientation ===")
        print(
            f"Position: X={telemetry.position_x:6.1f}, Y={telemetry.position_y:6.1f}, Z={telemetry.position_z:6.1f}"
        )
        print(
            f"Rotation: Pitch={telemetry.rotation_pitch:6.1f}, Yaw={telemetry.rotation_yaw:6.1f}, Roll={telemetry.rotation_roll:6.1f}"
        )

        print("\n=== Forces & Temperature ===")
        print(f"Lateral G:  {telemetry.lateral_g:6.2f} G")
        print(f"Longit. G:  {telemetry.longitudinal_g:6.2f} G")
        print(f"Eng. Temp:  {telemetry.engine_temp:6.1f}°C")
        print(f"Fuel:       {telemetry.fuel_level:6.1f}%")

        print("\n=== Lap Information ===")
        print(f"Current Lap:      {telemetry.current_lap}")
        print(f"Sector:           {telemetry.sector}")
        print(f"Current Lap Time: {telemetry.current_lap_time:6.2f}s")
        print(f"Last Lap Time:    {telemetry.last_lap_time:6.2f}s")


async def main():
    # Create and run client
    client = TelemetryClient()

    # You can change the recorder ID to test multiple streams
    await client.stream_telemetry("test-recorder-1")


if __name__ == "__main__":
    asyncio.run(main())
